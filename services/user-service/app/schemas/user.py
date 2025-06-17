from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserProfileBase(BaseModel):
    first_name: str = None
    last_name: str = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    bio: Optional[str] = None

class UserProfileCreate(UserProfileBase):
    user_id: int

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    is_profile_complete: bool
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UserBasicInfo(BaseModel):
    user_id: int
    email: str
    is_manufacturer: bool
    is_verified: bool
