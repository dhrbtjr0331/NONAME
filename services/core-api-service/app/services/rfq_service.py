from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime
from app.models.quote import RFQ, RFQStatus, Quote
from app.schemas.rfq import RFQCreate, RFQUpdate

class RFQService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_rfq(self, rfq_data: RFQCreate, manufacturer_id: int) -> RFQ:
        rfq = RFQ(
            **rfq_data.dict(),
            manufacturer_id=manufacturer_id,
            status=RFQStatus.OPEN
        )
        
        self.db.add(rfq)
        await self.db.commit()
        await self.db.refresh(rfq)
        return rfq
    
    async def get_rfq_by_id(self, rfq_id: int, include_quotes: bool = False) -> Optional[RFQ]:
        query = select(RFQ).where(RFQ.id == rfq_id)
        
        if include_quotes:
            query = query.options(selectinload(RFQ.quotes))
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_rfqs_for_manufacturer(
        self, 
        manufacturer_id: int, 
        status: Optional[RFQStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[RFQ]:
        query = select(RFQ).where(RFQ.manufacturer_id == manufacturer_id)
        
        if status:
            query = query.where(RFQ.status == status)
        
        query = query.offset(skip).limit(limit).order_by(RFQ.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_public_rfqs(
        self,
        product_category: Optional[str] = None,
        status: RFQStatus = RFQStatus.OPEN,
        skip: int = 0,
        limit: int = 100
    ) -> List[RFQ]:
        query = select(RFQ).where(
            and_(
                RFQ.is_public == True,
                RFQ.status == status,
                RFQ.quote_deadline > datetime.utcnow()
            )
        )
        
        if product_category:
            query = query.where(RFQ.product_category == product_category)
        
        query = query.offset(skip).limit(limit).order_by(RFQ.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_rfq(
        self, 
        rfq_id: int, 
        manufacturer_id: int, 
        update_data: RFQUpdate
    ) -> Optional[RFQ]:
        rfq = await self.get_rfq_by_id(rfq_id)
        
        if not rfq or rfq.manufacturer_id != manufacturer_id:
            return None
        
        if rfq.status != RFQStatus.OPEN:
            raise ValueError("Cannot update RFQ that is not open")
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(rfq, field, value)
        
        await self.db.commit()
        await self.db.refresh(rfq)
        return rfq
    
    async def close_rfq(self, rfq_id: int, manufacturer_id: int) -> Optional[RFQ]:
        rfq = await self.get_rfq_by_id(rfq_id)
        
        if not rfq or rfq.manufacturer_id != manufacturer_id:
            return None
        
        rfq.status = RFQStatus.CLOSED
        rfq.closed_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(rfq)
        return rfq
    
    async def get_quotes_for_rfq(self, rfq_id: int, manufacturer_id: int) -> List[Quote]:
        # Verify manufacturer owns the RFQ
        rfq_result = await self.db.execute(
            select(RFQ).where(
                and_(
                    RFQ.id == rfq_id,
                    RFQ.manufacturer_id == manufacturer_id
                )
            )
        )
        rfq = rfq_result.scalar_one_or_none()
        
        if not rfq:
            raise ValueError("RFQ not found or not owned by manufacturer")
        
        from app.models.quote import QuoteStatus
        result = await self.db.execute(
            select(Quote)
            .where(Quote.rfq_id == rfq_id)
            .where(Quote.status.in_([QuoteStatus.SUBMITTED, QuoteStatus.UNDER_REVIEW]))
            .order_by(Quote.total_price.asc())
        )
        return result.scalars().all()