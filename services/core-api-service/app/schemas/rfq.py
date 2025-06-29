from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class RFQStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    AWARDED = "AWARDED"
    CANCELLED = "CANCELLED"

class RFQPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class RFQBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)
    product_category: str
    quantity: int = Field(..., gt=0)
    unit: str = "pieces"
    target_price_min: Optional[float] = None
    target_price_max: Optional[float] = None
    currency: str = "USD"
    quote_deadline: datetime
    delivery_deadline: Optional[datetime] = None
    delivery_location: Optional[str] = None
    shipping_terms: Optional[str] = None
    technical_specs: Optional[str] = None
    quality_requirements: Optional[str] = None
    certifications_required: Optional[str] = None
    priority: RFQPriority = RFQPriority.MEDIUM
    is_public: bool = True
    max_suppliers: int = Field(default=10, ge=1, le=50)

class RFQCreate(RFQBase):
    pass

class RFQUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    quote_deadline: Optional[datetime] = None
    delivery_deadline: Optional[datetime] = None
    technical_specs: Optional[str] = None
    quality_requirements: Optional[str] = None
    priority: Optional[RFQPriority] = None
    max_suppliers: Optional[int] = None

class RFQResponse(RFQBase):
    id: int
    manufacturer_id: int
    status: RFQStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class RFQListItem(BaseModel):
    id: int
    title: str
    product_category: str
    quantity: int
    unit: str
    currency: str
    quote_deadline: datetime
    status: RFQStatus
    priority: RFQPriority
    created_at: datetime
    
    class Config:
        from_attributes = True