from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.config.database import get_db
from app.dependencies.auth import get_current_user, get_current_manufacturer
from app.schemas.rfq import RFQCreate, RFQUpdate, RFQResponse, RFQListItem, RFQStatus
from app.services.rfq_service import RFQService
from app.models.auth import User

router = APIRouter(prefix="/rfqs", tags=["rfqs"])

@router.post("/", response_model=RFQResponse, status_code=status.HTTP_201_CREATED)
async def create_rfq(
    rfq_data: RFQCreate,
    current_user: User = Depends(get_current_manufacturer),
    db: AsyncSession = Depends(get_db)
):
    """Create a new RFQ (manufacturers only)"""
    rfq_service = RFQService(db)
    try:
        rfq = await rfq_service.create_rfq(rfq_data, current_user.id)
        return RFQResponse.from_orm(rfq)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[RFQListItem])
async def list_public_rfqs(
    product_category: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List public RFQs available for quoting"""
    rfq_service = RFQService(db)
    rfqs = await rfq_service.get_public_rfqs(
        product_category=product_category,
        skip=skip,
        limit=limit
    )
    return [RFQListItem.from_orm(rfq) for rfq in rfqs]

@router.get("/my-rfqs", response_model=List[RFQListItem])
async def list_my_rfqs(
    status: Optional[RFQStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_manufacturer),
    db: AsyncSession = Depends(get_db)
):
    """List RFQs created by the current manufacturer"""
    rfq_service = RFQService(db)
    rfqs = await rfq_service.get_rfqs_for_manufacturer(
        manufacturer_id=current_user.id,
        status=status,
        skip=skip,
        limit=limit
    )
    return [RFQListItem.from_orm(rfq) for rfq in rfqs]

@router.get("/{rfq_id}", response_model=RFQResponse)
async def get_rfq(
    rfq_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get RFQ details"""
    rfq_service = RFQService(db)
    rfq = await rfq_service.get_rfq_by_id(rfq_id)
    
    if not rfq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RFQ not found")
    
    # Check access permissions
    if not rfq.is_public and rfq.manufacturer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return RFQResponse.from_orm(rfq)

@router.put("/{rfq_id}", response_model=RFQResponse)
async def update_rfq(
    rfq_id: int,
    update_data: RFQUpdate,
    current_user: User = Depends(get_current_manufacturer),
    db: AsyncSession = Depends(get_db)
):
    """Update RFQ (manufacturer only)"""
    rfq_service = RFQService(db)
    try:
        rfq = await rfq_service.update_rfq(rfq_id, current_user.id, update_data)
        if not rfq:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RFQ not found")
        return RFQResponse.from_orm(rfq)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{rfq_id}/close", response_model=RFQResponse)
async def close_rfq(
    rfq_id: int,
    current_user: User = Depends(get_current_manufacturer),
    db: AsyncSession = Depends(get_db)
):
    """Close RFQ (manufacturer only)"""
    rfq_service = RFQService(db)
    rfq = await rfq_service.close_rfq(rfq_id, current_user.id)
    
    if not rfq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RFQ not found")
    
    return RFQResponse.from_orm(rfq)