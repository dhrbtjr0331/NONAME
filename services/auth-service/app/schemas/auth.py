from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    is_manufacturer: bool = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    is_manufacturer: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    email: str
    is_manufacturer: bool
    is_verified: bool

    class Config:
        from_attributes = True