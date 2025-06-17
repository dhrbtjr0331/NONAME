from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.schemas.user import UserBasicInfo

security = HTTPBearer()

# These should match your auth-service settings
SECRET_KEY = "your-secret-key-here"  # Should come from shared config
ALGORITHM = "HS256"

async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserBasicInfo:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        email: str = payload.get("email")
        is_manufacturer: bool = payload.get("is_manufacturer")
        
        if user_id is None or email is None:
            raise credentials_exception
            
        return UserBasicInfo(
            user_id=user_id,
            email=email,
            is_manufacturer=is_manufacturer,
            is_verified=True  # Assume verified if token is valid
        )
    except JWTError:
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