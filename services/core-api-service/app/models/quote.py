from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.models import Base

class RFQStatus(enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    AWARDED = "AWARDED"
    CANCELLED = "CANCELLED"

class RFQPriority(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class QuoteStatus(enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"

class RFQ(Base):
    __tablename__ = "rfqs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    product_category = Column(String(100), nullable=False, index=True)
    
    # Manufacturer Info (references users table)
    manufacturer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Requirements
    quantity = Column(Integer, nullable=False)
    unit = Column(String(20), default="pieces")
    target_price_min = Column(Numeric(10, 2))
    target_price_max = Column(Numeric(10, 2))
    currency = Column(String(3), default="USD")
    
    # Timeline
    quote_deadline = Column(DateTime, nullable=False)
    delivery_deadline = Column(DateTime)
    
    # Location & Shipping
    delivery_location = Column(String(255))
    shipping_terms = Column(String(100))
    
    # Technical Specifications
    technical_specs = Column(Text)
    quality_requirements = Column(Text)
    certifications_required = Column(String(500))
    
    # RFQ Management
    status = Column(Enum(RFQStatus), default=RFQStatus.OPEN, index=True)
    priority = Column(Enum(RFQPriority), default=RFQPriority.MEDIUM)
    
    # Internal flags
    is_public = Column(Boolean, default=True)
    max_suppliers = Column(Integer, default=10)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True))
    
    # Relationships
    manufacturer = relationship("User", backref="rfqs")
    quotes = relationship("Quote", back_populates="rfq", cascade="all, delete-orphan")

class Quote(Base):
    __tablename__ = "quotes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # References
    rfq_id = Column(Integer, ForeignKey("rfqs.id"), nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Pricing
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    
    # Terms
    lead_time_days = Column(Integer, nullable=False)
    minimum_order_quantity = Column(Integer, default=1)
    payment_terms = Column(String(100))
    warranty_period = Column(String(50))
    
    # Additional Details
    notes = Column(Text)
    technical_response = Column(Text)
    certifications_provided = Column(String(500))
    
    # Supplier Confidence
    confidence_level = Column(Integer, default=100)
    
    # Quote Management
    status = Column(Enum(QuoteStatus), default=QuoteStatus.DRAFT, index=True)
    is_final = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    submitted_at = Column(DateTime(timezone=True))
    
    # Relationships
    rfq = relationship("RFQ", back_populates="quotes")
    supplier = relationship("User", foreign_keys=[supplier_id], backref="quotes")