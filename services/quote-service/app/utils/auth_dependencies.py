from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.config.settings import settings

security = HTTPBearer()

class UserBasicInfo:
    def __init__(self, user_id: int, email: str, is_manufacturer: bool, is_verified: bool = True):
        self.user_id = user_id
        self.email = email
        self.is_manufacturer = is_manufacturer
        self.is_verified = is_verified

async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserBasicInfo:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        if payload.get("type") != "access":
            raise credentials_exception
        
        user_id = payload.get("sub")
        email = payload.get("email")
        is_manufacturer = payload.get("is_manufacturer")
        
        if user_id is None or email is None:
            raise credentials_exception
            
        return UserBasicInfo(
            user_id=int(user_id),
            email=email,
            is_manufacturer=is_manufacturer,
            is_verified=True
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