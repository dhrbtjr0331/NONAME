from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.config.database import get_db
from app.dependencies.auth import get_current_user_info, get_current_supplier, get_current_manufacturer
from app.schemas.quote import QuoteCreate, QuoteUpdate, QuoteResponse, QuoteListItem, QuoteStatus
from app.services.quote_service import QuoteService

router = APIRouter(prefix="/quotes", tags=["quotes"])

@router.post("/", response_model=QuoteResponse, status_code=status.HTTP_201_CREATED)
async def create_quote(
    quote_data: QuoteCreate,
    current_user = Depends(get_current_supplier),
    db: AsyncSession = Depends(get_db)
):
    """Create a new quote (suppliers only)"""
    quote_service = QuoteService(db)
    try:
        quote = await quote_service.create_quote(quote_data, current_user.user_id)
        return QuoteResponse.from_orm(quote)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/my-quotes", response_model=List[QuoteListItem])
async def list_my_quotes(
    status: Optional[QuoteStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user = Depends(get_current_supplier),
    db: AsyncSession = Depends(get_db)
):
    """List quotes created by the current supplier"""
    quote_service = QuoteService(db)
    quotes = await quote_service.get_quotes_for_supplier(
        supplier_id=current_user.user_id,
        status=status,
        skip=skip,
        limit=limit
    )
    return [QuoteListItem.from_orm(quote) for quote in quotes]

@router.get("/rfq/{rfq_id}", response_model=List[QuoteResponse])
async def get_quotes_for_rfq(
    rfq_id: int,
    current_user = Depends(get_current_manufacturer),
    db: AsyncSession = Depends(get_db)
):
    """Get all quotes for an RFQ (manufacturer only)"""
    quote_service = QuoteService(db)
    try:
        quotes = await quote_service.get_quotes_for_rfq(rfq_id, current_user.user_id)
        return [QuoteResponse.from_orm(quote) for quote in quotes]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{quote_id}", response_model=QuoteResponse)
async def get_quote(
    quote_id: int,
    current_user = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db)
):
    """Get quote details"""
    quote_service = QuoteService(db)
    quote = await quote_service.get_quote_by_id(quote_id)
    
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found")
    
    # Check access permissions
    if (quote.supplier_id != current_user.user_id and 
        quote.rfq.manufacturer_id != current_user.user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return QuoteResponse.from_orm(quote)

@router.put("/{quote_id}", response_model=QuoteResponse)
async def update_quote(
    quote_id: int,
    update_data: QuoteUpdate,
    current_user = Depends(get_current_supplier),
    db: AsyncSession = Depends(get_db)
):
    """Update quote (supplier only)"""
    quote_service = QuoteService(db)
    try:
        quote = await quote_service.update_quote(quote_id, current_user.user_id, update_data)
        if not quote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found")
        return QuoteResponse.from_orm(quote)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{quote_id}/submit", response_model=QuoteResponse)
async def submit_quote(
    quote_id: int,
    current_user = Depends(get_current_supplier),
    db: AsyncSession = Depends(get_db)
):
    """Submit quote for review (supplier only)"""
    quote_service = QuoteService(db)
    try:
        quote = await quote_service.submit_quote(quote_id, current_user.user_id)
        if not quote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found")
        return QuoteResponse.from_orm(quote)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{quote_id}/withdraw", response_model=QuoteResponse)
async def withdraw_quote(
    quote_id: int,
    current_user = Depends(get_current_supplier),
    db: AsyncSession = Depends(get_db)
):
    """Withdraw quote (supplier only)"""
    quote_service = QuoteService(db)
    try:
        quote = await quote_service.withdraw_quote(quote_id, current_user.user_id)
        if not quote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found")
        return QuoteResponse.from_orm(quote)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{quote_id}/accept", response_model=QuoteResponse)
async def accept_quote(
    quote_id: int,
    current_user = Depends(get_current_manufacturer),
    db: AsyncSession = Depends(get_db)
):
    """Accept quote (manufacturer only)"""
    quote_service = QuoteService(db)
    try:
        quote = await quote_service.accept_quote(quote_id, current_user.user_id)
        if not quote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found")
        return QuoteResponse.from_orm(quote)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))