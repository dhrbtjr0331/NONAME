from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, func, update
from typing import List, Optional
from datetime import datetime
from app.models.quote import Quote, QuoteStatus, RFQ, RFQStatus
from app.schemas.quote import QuoteCreate, QuoteUpdate

class QuoteService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_quote(self, quote_data: QuoteCreate, supplier_id: int) -> Quote:
        # Check if RFQ exists and is open
        rfq_result = await self.db.execute(select(RFQ).where(RFQ.id == quote_data.rfq_id))
        rfq = rfq_result.scalar_one_or_none()
        
        if not rfq:
            raise ValueError("RFQ not found")
        
        if rfq.status != RFQStatus.OPEN:
            raise ValueError("RFQ is not open for quotes")
        
        if rfq.quote_deadline < datetime.utcnow():
            raise ValueError("Quote deadline has passed")
        
        # Check if supplier already has a quote for this RFQ
        existing_quote = await self.get_quote_by_rfq_and_supplier(quote_data.rfq_id, supplier_id)
        if existing_quote:
            raise ValueError("Quote already exists for this RFQ")
        
        # Check max suppliers limit
        quote_count = await self.get_quote_count_for_rfq(quote_data.rfq_id)
        if quote_count >= rfq.max_suppliers:
            raise ValueError("Maximum number of suppliers reached for this RFQ")
        
        quote = Quote(
            **quote_data.dict(),
            supplier_id=supplier_id,
            status=QuoteStatus.DRAFT
        )
        
        self.db.add(quote)
        await self.db.commit()
        await self.db.refresh(quote)
        return quote
    
    async def get_quote_by_id(self, quote_id: int) -> Optional[Quote]:
        result = await self.db.execute(
            select(Quote)
            .options(selectinload(Quote.rfq))
            .where(Quote.id == quote_id)
        )
        return result.scalar_one_or_none()
    
    async def get_quote_by_rfq_and_supplier(self, rfq_id: int, supplier_id: int) -> Optional[Quote]:
        result = await self.db.execute(
            select(Quote).where(
                and_(
                    Quote.rfq_id == rfq_id,
                    Quote.supplier_id == supplier_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_quotes_for_supplier(
        self,
        supplier_id: int,
        status: Optional[QuoteStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Quote]:
        query = select(Quote).where(Quote.supplier_id == supplier_id)
        
        if status:
            query = query.where(Quote.status == status)
        
        query = query.offset(skip).limit(limit).order_by(Quote.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_quote(
        self,
        quote_id: int,
        supplier_id: int,
        update_data: QuoteUpdate
    ) -> Optional[Quote]:
        quote = await self.get_quote_by_id(quote_id)
        
        if not quote or quote.supplier_id != supplier_id:
            return None
        
        if quote.status not in [QuoteStatus.DRAFT, QuoteStatus.SUBMITTED]:
            raise ValueError("Cannot update quote in current status")
        
        if quote.is_final:
            raise ValueError("Cannot update final quote")
        
        # Check if RFQ deadline has passed
        if quote.rfq.quote_deadline < datetime.utcnow():
            raise ValueError("Quote deadline has passed")
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(quote, field, value)
        
        await self.db.commit()
        await self.db.refresh(quote)
        return quote
    
    async def submit_quote(self, quote_id: int, supplier_id: int) -> Optional[Quote]:
        quote = await self.get_quote_by_id(quote_id)
        
        if not quote or quote.supplier_id != supplier_id:
            return None
        
        if quote.status != QuoteStatus.DRAFT:
            raise ValueError("Quote must be in draft status to submit")
        
        if quote.rfq.quote_deadline < datetime.utcnow():
            raise ValueError("Quote deadline has passed")
        
        quote.status = QuoteStatus.SUBMITTED
        quote.submitted_at = datetime.utcnow()
        quote.is_final = True
        
        await self.db.commit()
        await self.db.refresh(quote)
        return quote
    
    async def withdraw_quote(self, quote_id: int, supplier_id: int) -> Optional[Quote]:
        quote = await self.get_quote_by_id(quote_id)
        
        if not quote or quote.supplier_id != supplier_id:
            return None
        
        if quote.status not in [QuoteStatus.DRAFT, QuoteStatus.SUBMITTED]:
            raise ValueError("Cannot withdraw quote in current status")
        
        # Check if RFQ deadline has passed
        if quote.rfq.quote_deadline < datetime.utcnow():
            raise ValueError("Quote deadline has passed")
        
        quote.status = QuoteStatus.WITHDRAWN
        
        await self.db.commit()
        await self.db.refresh(quote)
        return quote
    
    async def accept_quote(self, quote_id: int, manufacturer_id: int) -> Optional[Quote]:
        quote = await self.get_quote_by_id(quote_id)
        
        if not quote or quote.rfq.manufacturer_id != manufacturer_id:
            return None
        
        if quote.status != QuoteStatus.SUBMITTED:
            raise ValueError("Quote must be submitted to accept")
        
        # Update quote status
        quote.status = QuoteStatus.ACCEPTED
        
        # Close the RFQ
        quote.rfq.status = RFQStatus.AWARDED
        quote.rfq.closed_at = datetime.utcnow()
        
        # Reject other quotes for this RFQ
        await self.db.execute(
            update(Quote)
            .where(
                and_(
                    Quote.rfq_id == quote.rfq_id,
                    Quote.id != quote_id,
                    Quote.status == QuoteStatus.SUBMITTED
                )
            )
            .values(status=QuoteStatus.REJECTED)
        )
        
        await self.db.commit()
        await self.db.refresh(quote)
        return quote
    
    async def get_quote_count_for_rfq(self, rfq_id: int) -> int:
        result = await self.db.execute(
            select(func.count(Quote.id)).where(Quote.rfq_id == rfq_id)
        )
        return result.scalar()