from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class RfqDataSchema(BaseModel):
    product_name: Optional[str] = Field(None, description="name of the product that the user is requesting for quote")
    product_description: Optional[str] = Field(None, description="description of the product that the user is requesting for quote")
    product_category: Optional[str] = Field(None, description="category of the product that the user is requesting for quote")
    priority: Optional[str] = Field(None, description="priority of the request (high, medium, low)")
    quantity: Optional[int] = Field(None, description="quantity of the product that the user is requesting for quote")
    unit: Optional[str] = Field(None, description="unit of measurement for the quantity (e.g., pieces, kg, liters)")
    max_suppliers: Optional[int] = Field(None, description="maximum number of suppliers that submit the quote")
    min_price_per_unit: Optional[float] = Field(None, description="minimum price per unit that the user is willing to pay")
    max_price_per_unit: Optional[float] = Field(None, description="maximum price per unit that the user is willing to pay")
    currency: Optional[str] = Field(None, description="currency of the prices (e.g., USD, EUR)")
    quote_deadline: Optional[str] = Field(None, description="deadline for the quote submission")
    delivery_deadline: Optional[str] = Field(None, description="deadline for the product delivery")
    delivery_location: Optional[str] = Field(None, description="location where the product should be delivered")
    shipping_terms: Optional[str] = Field(None, description="terms of shipping (e.g., FOB, CIF)")
    technical_specifications: Optional[List[str]] = Field(None, description="technical specifications of the product in a list")
    quality_requirements: Optional[List[str]] = Field(None, description="quality requirements for the product in a list")
    required_certifications: Optional[List[str]] = Field(None, description="certifications required for the product in a list")