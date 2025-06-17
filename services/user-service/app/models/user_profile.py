from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class UserProfile(Base):
    __tablename__ = 'user_profiles'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True, nullable=False) # References auth-service user
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(20))
    job_title = Column(String(100))
    bio = Column(Text)
    avatar_url = Column(String(255))
    is_profile_complete = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with company
    company = relationship("Company", back_populates="owner", uselist=False)

class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    company_name = Column(String(100), nullable=False)
    industry = Column(String(50))
    company_size = Column(String(20))  # "1-10", "11-50", "51-200", "200+"
    website = Column(String(255))
    description = Column(Text)
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(50))
    country = Column(String(50))
    postal_code = Column(String(20))
    tax_id = Column(String(50))  # For business verification
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    owner = relationship("UserProfile", back_populates="company")
