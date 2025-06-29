from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.config.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.services.user_service import UserService
from app.models.auth import User

router = APIRouter(prefix="/companies", tags=["companies"])

@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    try:
        company = await user_service.create_company(current_user.id, company_data)
        return CompanyResponse.from_orm(company)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/my-company", response_model=CompanyResponse)
async def get_my_company(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    profile = await user_service.get_profile_by_user_id(current_user.id)
    
    if not profile or not profile.company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return CompanyResponse.from_orm(profile.company)

@router.put("/my-company", response_model=CompanyResponse)
async def update_my_company(
    update_data: CompanyUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    try:
        company = await user_service.update_company(current_user.id, update_data)
        return CompanyResponse.from_orm(company)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company_by_id(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy.future import select
    from app.models.user import Company
    
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy.future import select
    from app.models.user import Company
    
    query = select(Company).offset(skip).limit(limit)
    
    if industry:
        query = query.where(Company.industry == industry)
    
    result = await db.execute(query)
    companies = result.scalars().all()
    
    return [CompanyResponse.from_orm(company) for company in companies]