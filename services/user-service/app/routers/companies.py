from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.utils.auth_dependencies import get_current_user_info, get_current_manufacturer
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.schemas.user import UserBasicInfo
from app.services.user_service import UserService
from typing import Optional

router = APIRouter(prefix="/companies", tags=["companies"])

@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    current_user: UserBasicInfo = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    try:
        company = await user_service.create_company(current_user.user_id, company_data)
        return CompanyResponse.from_orm(company)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/my-company", response_model=CompanyResponse)
async def get_my_company(
    current_user: UserBasicInfo = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    profile = await user_service.get_profile_by_user_id(current_user.user_id)
    
    if not profile or not profile.company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return CompanyResponse.from_orm(profile.company)

@router.put("/my-company", response_model=CompanyResponse)
async def update_my_company(
    update_data: CompanyUpdate,
    current_user: UserBasicInfo = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    try:
        company = await user_service.update_company(current_user.user_id, update_data)
        return CompanyResponse.from_orm(company)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company_by_id(
    company_id: int,
    current_user: UserBasicInfo = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy.future import select
    from app.models.user_profile import Company
    
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return CompanyResponse.from_orm(company)

@router.get("/", response_model=list[CompanyResponse])
async def list_companies(
    skip: int = 0,
    limit: int = 100,
    industry: Optional[str] = None,
    current_user: UserBasicInfo = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy.future import select
    from app.models.user_profile import Company
    
    query = select(Company).offset(skip).limit(limit)
    
    if industry:
        query = query.where(Company.industry == industry)
    
    result = await db.execute(query)
    companies = result.scalars().all()
    
    return [CompanyResponse.from_orm(company) for company in companies]

# Manufacturer-only endpoints
@router.get("/suppliers/search", response_model=list[CompanyResponse])
async def search_suppliers(
    industry: Optional[str] = None,
    company_size: Optional[str] = None,
    country: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: UserBasicInfo = Depends(get_current_manufacturer),
    db: AsyncSession = Depends(get_db)
):
    """Search for supplier companies (manufacturer-only endpoint)"""
    from sqlalchemy.future import select
    from sqlalchemy.orm import selectinload
    from app.models.user_profile import Company, UserProfile
    
    # Query companies where owner is a supplier (not manufacturer)
    query = select(Company).join(UserProfile).where(
        UserProfile.user_id.in_(
            # This would ideally be a call to auth-service to get supplier user_ids
            # For now, we'll assume a method to identify suppliers
            select([1])  # Placeholder - needs proper implementation
        )
    ).offset(skip).limit(limit)
    
    if industry:
        query = query.where(Company.industry == industry)
    if company_size:
        query = query.where(Company.company_size == company_size)
    if country:
        query = query.where(Company.country == country)
    
    result = await db.execute(query)
    companies = result.scalars().all()
    
    return [CompanyResponse.from_orm(company) for company in companies]