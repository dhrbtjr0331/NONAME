from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.user import UserProfile, Company
from app.schemas.user import UserProfileCreate, UserProfileUpdate
from app.schemas.company import CompanyCreate, CompanyUpdate

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_profile(self, profile_data: UserProfileCreate) -> UserProfile:
        # Check if profile already exists
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == profile_data.user_id)
        )
        if result.scalar_one_or_none():
            raise ValueError("Profile already exists for this user")
        
        profile = UserProfile(**profile_data.dict())
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile
    
    async def get_profile_by_user_id(self, user_id: int) -> UserProfile:
        result = await self.db.execute(
            select(UserProfile)
            .options(selectinload(UserProfile.company))
            .where(UserProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def update_profile(self, user_id: int, update_data: UserProfileUpdate) -> UserProfile:
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise ValueError("Profile not found")
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(profile, field, value)
        
        # Check if profile is complete
        profile.is_profile_complete = self._check_profile_completeness(profile)
        
        await self.db.commit()
        await self.db.refresh(profile)
        return profile
    
    async def create_company(self, owner_user_id: int, company_data: CompanyCreate) -> Company:
        # Get user profile
        profile = await self.get_profile_by_user_id(owner_user_id)
        if not profile:
            raise ValueError("User profile not found")
        
        # Check if company already exists
        if profile.company:
            raise ValueError("Company already exists for this user")
        
        company = Company(owner_id=profile.id, **company_data.dict())
        self.db.add(company)
        await self.db.commit()
        await self.db.refresh(company)
        return company
    
    async def update_company(self, user_id: int, update_data: CompanyUpdate) -> Company:
        profile = await self.get_profile_by_user_id(user_id)
        if not profile or not profile.company:
            raise ValueError("Company not found")
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(profile.company, field, value)
        
        await self.db.commit()
        await self.db.refresh(profile.company)
        return profile.company
    
    def _check_profile_completeness(self, profile: UserProfile) -> bool:
        required_fields = ['first_name', 'last_name', 'phone', 'job_title']
        return all(getattr(profile, field) for field in required_fields)