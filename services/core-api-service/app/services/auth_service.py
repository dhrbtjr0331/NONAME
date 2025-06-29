from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from app.models.auth import User
from app.schemas.auth import UserRegister, UserLogin
from app.utils.jwt_handler import create_access_token, create_refresh_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    async def register_user(self, user_data: UserRegister) -> User:
        # Check if user exists
        result = await self.db.execute(select(User).where(User.email == user_data.email))
        if result.scalar_one_or_none():
            raise ValueError("Email already registered")
        
        # Create new user
        hashed_password = self.hash_password(user_data.password)
        new_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            is_manufacturer=user_data.is_manufacturer
        )
        
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user
    
    async def authenticate_user(self, credentials: UserLogin) -> User:
        result = await self.db.execute(select(User).where(User.email == credentials.email))
        user = result.scalar_one_or_none()
        
        if not user or not self.verify_password(credentials.password, user.password_hash):
            return None
        
        return user
    
    def create_tokens(self, user: User) -> tuple[str, str]:
        access_token = create_access_token({
            "sub": str(user.id),
            "email": user.email,
            "is_manufacturer": user.is_manufacturer
        })
        refresh_token = create_refresh_token({
            "sub": str(user.id)
        })
        return access_token, refresh_token