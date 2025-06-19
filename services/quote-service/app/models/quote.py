from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.models import Base

class QuoteStatus(enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"

class Quote(Base):
    __tablename__ = "quotes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # References
    rfq_id = Column(Integer, ForeignKey("rfqs.id"), nullable=False, index=True)
    supplier_id = Column(Integer, nullable=False, index=True)  # References user_id from auth
    
    # Pricing
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    
    # Terms
    lead_time_days = Column(Integer, nullable=False)  # Manufacturing/delivery time
    minimum_order_quantity = Column(Integer, default=1)
    payment_terms = Column(String(100))  # "30 days", "Net 15", etc.
    warranty_period = Column(String(50))  # "1 year", "6 months", etc.
    
    # Additional Details
    notes = Column(Text)  # Additional supplier comments
    technical_response = Column(Text)  # Response to technical requirements
    certifications_provided = Column(String(500))  # What certs supplier has
    
    # Supplier Confidence
    confidence_level = Column(Integer, default=100)  # 0-100, supplier's confidence in quote
    
    # Quote Management
    status = Column(Enum(QuoteStatus), default=QuoteStatus.DRAFT, index=True)
    is_final = Column(Boolean, default=False)  # Can supplier still modify?
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    submitted_at = Column(DateTime(timezone=True))
    
    # Relationships
    rfq = relationship("RFQ", back_populates="quotes")