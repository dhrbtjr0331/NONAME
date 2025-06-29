from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    phone = Column(String(20))
    job_title = Column(String(100))
    bio = Column(Text)
    avatar_url = Column(String(255))
    is_profile_complete = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="profile")
    company = relationship("Company", back_populates="profile_owner", uselist=False)  # Fixed

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    company_name = Column(String(100), nullable=False)
    industry = Column(String(50))
    company_size = Column(String(20))
    website = Column(String(255))
    description = Column(Text)
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(50))
    country = Column(String(50))
    postal_code = Column(String(20))
    tax_id = Column(String(50))
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship - Fixed name
    profile_owner = relationship("UserProfile", back_populates="company")