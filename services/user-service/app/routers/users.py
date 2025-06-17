from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.config.database import get_db
from app.utils.auth_dependencies import get_current_user_info, get_current_manufacturer, get_current_supplier
from app.schemas.user import UserProfileCreate, UserProfileUpdate, UserProfileResponse, UserBasicInfo
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/profile", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_user_profile(
    profile_data: UserProfileCreate,
    current_user: UserBasicInfo = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db)
):
    # Ensure user can only create their own profile
    if profile_data.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create profile for another user"
        )

    user_service = UserService(db)
    try:
        profile = await user_service.create_profile(profile_data)
        return UserProfileResponse.from_orm(profile)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    

@router.get("/profile/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: UserBasicInfo = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    profile = await user_service.get_profile_by_user_id(user_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return UserProfileResponse.from_orm(profile)


@router.put("/profile", response_model=UserProfileResponse)
async def update_my_profile(
    update_data: UserProfileUpdate,
    current_user: UserBasicInfo = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    try:
        profile = await user_service.update_profile(current_user.user_id, update_data)
        return UserProfileResponse.from_orm(profile)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/me", response_model=UserBasicInfo)
async def get_current_user_details(
    current_user: UserBasicInfo = Depends(get_current_user_info)
):
    return current_user


@router.delete("/profile")
async def delete_my_profile(
    current_user: UserBasicInfo = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    profile = await user_service.get_profile_by_user_id(current_user.user_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    await db.delete(profile)
    await db.commit()
    
    return {"message": "Profile deleted successfully"}