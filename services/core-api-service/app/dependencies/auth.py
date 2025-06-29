from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError, jwt

from app.config.database import get_db
from app.config.settings import settings
from app.models.auth import User

security = HTTPBearer()

class UserBasicInfo:
    def __init__(self, user_id: int, email: str, is_manufacturer: bool, is_verified: bool = True):
        self.user_id = user_id
        self.email = email
        self.is_manufacturer = is_manufacturer
        self.is_verified = is_verified

async def get_current_user_token_data(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Extract and validate JWT token data"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        if payload.get("type") != "access":
            raise credentials_exception
        
        user_id = payload.get("sub")
        email = payload.get("email")
        is_manufacturer = payload.get("is_manufacturer")
        
        if user_id is None or email is None:
            raise credentials_exception
            
        return {
            "user_id": int(user_id),
            "email": email,
            "is_manufacturer": is_manufacturer
        }
    except JWTError:
        raise credentials_exception

async def get_current_user(
    token_data: dict = Depends(get_current_user_token_data),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current user from database using token data"""
    result = await db.execute(select(User).where(User.id == token_data["user_id"]))
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user

async def get_current_user_info(
    token_data: dict = Depends(get_current_user_token_data)
) -> UserBasicInfo:
    """Get basic user info without database query (for performance)"""
    return UserBasicInfo(
        user_id=token_data["user_id"],
        email=token_data["email"],
        is_manufacturer=token_data["is_manufacturer"],
        is_verified=True
    )

async def get_current_manufacturer(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure current user is a manufacturer"""
    if not current_user.is_manufacturer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Manufacturer account required."
        )
    return current_user

async def get_current_supplier(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure current user is a supplier"""
    if current_user.is_manufacturer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Supplier account required."
        )
    return current_user