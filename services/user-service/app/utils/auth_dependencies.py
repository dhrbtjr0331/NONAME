from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime
from app.schemas.user import UserBasicInfo
from app.config.settings import settings

security = HTTPBearer()

async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserBasicInfo:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    
    # DEBUG: Print token info
    print(f"Received token (first 50 chars): {token[:50]}...")
    print(f"Using SECRET_KEY: {settings.SECRET_KEY[:10]}...")
    print(f"Using ALGORITHM: {settings.ALGORITHM}")
    
    try:
        # FIXED: Proper way to decode without verification
        unverified_payload = jwt.decode(
            token, 
            key="", 
            algorithms=[settings.ALGORITHM], 
            options={"verify_signature": False}
        )
        print(f"Unverified payload: {unverified_payload}")
        
        # Check expiration
        exp_timestamp = unverified_payload.get("exp")
        if exp_timestamp:
            exp_time = datetime.fromtimestamp(exp_timestamp)
            current_time = datetime.utcnow()
            print(f"Token expires at: {exp_time}")
            print(f"Current time: {current_time}")
            print(f"Token expired: {current_time > exp_time}")
        
        # Now try with verification
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print(f"Verified payload: {payload}")
        
        if payload.get("type") != "access":
            print(f"Wrong token type: {payload.get('type')}")
            raise credentials_exception
        
        user_id = payload.get("sub")
        email = payload.get("email")
        is_manufacturer = payload.get("is_manufacturer")
        
        if user_id is None or email is None:
            print("Missing user_id or email in token")
            raise credentials_exception
            
        return UserBasicInfo(
            user_id=int(user_id),
            email=email,
            is_manufacturer=is_manufacturer,
            is_verified=True
        )
    except JWTError as e:
        print(f"JWT Error: {e}")
        raise credentials_exception
    
async def get_current_manufacturer(
    current_user: UserBasicInfo = Depends(get_current_user_info)
) -> UserBasicInfo:
    if not current_user.is_manufacturer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Manufacturer account required."
        )
    return current_user

async def get_current_supplier(
    current_user: UserBasicInfo = Depends(get_current_user_info)
) -> UserBasicInfo:
    if current_user.is_manufacturer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Supplier account required."
        )
    return current_user