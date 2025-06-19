from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, Numeric
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

class RFQ(Base):
    __tablename__ = "rfqs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    product_category = Column(String(100), nullable=False, index=True)
    
    # Manufacturer Info (from auth/user service)
    manufacturer_id = Column(Integer, nullable=False, index=True)  # References user_id from auth
    
    # Requirements
    quantity = Column(Integer, nullable=False)
    unit = Column(String(20), default="pieces")  # pieces, kg, meters, etc.
    target_price_min = Column(Numeric(10, 2))  # Optional price range
    target_price_max = Column(Numeric(10, 2))
    currency = Column(String(3), default="USD")
    
    # Timeline
    quote_deadline = Column(DateTime, nullable=False)
    delivery_deadline = Column(DateTime)
    
    # Location & Shipping
    delivery_location = Column(String(255))
    shipping_terms = Column(String(100))  # FOB, CIF, etc.
    
    # Technical Specifications
    technical_specs = Column(Text)  # JSON string or plain text
    quality_requirements = Column(Text)
    certifications_required = Column(String(500))  # ISO, CE, etc.
    
    # RFQ Management
    status = Column(Enum(RFQStatus), default=RFQStatus.OPEN, index=True)
    priority = Column(Enum(RFQPriority), default=RFQPriority.MEDIUM)
    
    # Internal flags
    is_public = Column(Boolean, default=True)  # Public vs private RFQ
    max_suppliers = Column(Integer, default=10)  # Limit number of quotes
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True))
    
    # Relationships
    quotes = relationship("Quote", back_populates="rfq", cascade="all, delete-orphan")