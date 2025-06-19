from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class QuoteStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"

class QuoteBase(BaseModel):
    unit_price: float = Field(..., gt=0)
    total_price: float = Field(..., gt=0)
    currency: str = "USD"
    lead_time_days: int = Field(..., ge=1)
    minimum_order_quantity: int = Field(default=1, ge=1)
    payment_terms: Optional[str] = None
    warranty_period: Optional[str] = None
    notes: Optional[str] = None
    technical_response: Optional[str] = None
    certifications_provided: Optional[str] = None
    confidence_level: int = Field(default=100, ge=0, le=100)

class QuoteCreate(QuoteBase):
    rfq_id: int

class QuoteUpdate(BaseModel):
    unit_price: Optional[float] = None
    total_price: Optional[float] = None
    lead_time_days: Optional[int] = None
    minimum_order_quantity: Optional[int] = None
    payment_terms: Optional[str] = None
    warranty_period: Optional[str] = None
    notes: Optional[str] = None
    technical_response: Optional[str] = None
    certifications_provided: Optional[str] = None
    confidence_level: Optional[int] = None

class QuoteResponse(QuoteBase):
    id: int
    rfq_id: int
    supplier_id: int
    status: QuoteStatus
    is_final: bool
    created_at: datetime
    updated_at: Optional[datetime]
    submitted_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class QuoteListItem(BaseModel):
    id: int
    rfq_id: int
    supplier_id: int
    unit_price: float
    total_price: float
    currency: str
    lead_time_days: int
    status: QuoteStatus
    created_at: datetime
    
    class Config:
        from_attributes = True