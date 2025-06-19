from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    RFQ_CREATED = "RFQ_CREATED"
    QUOTE_SUBMITTED = "QUOTE_SUBMITTED"
    QUOTE_UPDATED = "QUOTE_UPDATED"
    QUOTE_ACCEPTED = "QUOTE_ACCEPTED"
    QUOTE_REJECTED = "QUOTE_REJECTED"
    RFQ_CLOSED = "RFQ_CLOSED"
    RFQ_DEADLINE_REMINDER = "RFQ_DEADLINE_REMINDER"

class NotificationStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    RETRY = "RETRY"

class NotificationChannel(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"
    IN_APP = "IN_APP"

class NotificationCreate(BaseModel):
    recipient_user_id: int
    recipient_email: EmailStr
    recipient_name: Optional[str] = None
    notification_type: NotificationType
    channel: NotificationChannel = NotificationChannel.EMAIL
    subject: str
    message: str
    html_content: Optional[str] = None
    rfq_id: Optional[int] = None
    quote_id: Optional[int] = None
    context_data: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[datetime] = None

class NotificationResponse(BaseModel):
    id: int
    recipient_user_id: int
    recipient_email: str
    recipient_name: Optional[str]
    notification_type: NotificationType
    channel: NotificationChannel
    subject: str
    message: str
    rfq_id: Optional[int]
    quote_id: Optional[int]
    status: NotificationStatus
    attempts: int
    scheduled_at: datetime
    sent_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class NotificationListItem(BaseModel):
    id: int
    recipient_email: str
    notification_type: NotificationType
    subject: str
    status: NotificationStatus
    attempts: int
    scheduled_at: datetime
    sent_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class NotificationPreferenceUpdate(BaseModel):
    email_rfq_created: Optional[bool] = None
    email_quote_submitted: Optional[bool] = None
    email_quote_accepted: Optional[bool] = None
    email_quote_rejected: Optional[bool] = None
    email_rfq_closed: Optional[bool] = None
    email_deadline_reminders: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None

class NotificationPreferenceResponse(BaseModel):
    id: int
    user_id: int
    email_rfq_created: bool
    email_quote_submitted: bool
    email_quote_accepted: bool
    email_quote_rejected: bool
    email_rfq_closed: bool
    email_deadline_reminders: bool
    sms_enabled: bool
    push_enabled: bool
    
    class Config:
        from_attributes = True

# Event schemas for inter-service communication
class RFQCreatedEvent(BaseModel):
    rfq_id: int
    rfq_title: str
    manufacturer_id: int
    manufacturer_email: str
    manufacturer_name: str
    product_category: str
    quantity: int
    quote_deadline: datetime

class QuoteSubmittedEvent(BaseModel):
    quote_id: int
    rfq_id: int
    rfq_title: str
    supplier_id: int
    supplier_email: str
    supplier_name: str
    manufacturer_id: int
    manufacturer_email: str
    manufacturer_name: str
    unit_price: float
    total_price: float
    currency: str

class QuoteAcceptedEvent(BaseModel):
    quote_id: int
    rfq_id: int
    rfq_title: str
    supplier_id: int
    supplier_email: str
    supplier_name: str
    manufacturer_id: int
    manufacturer_email: str
    manufacturer_name: str
    total_price: float
    currency: str