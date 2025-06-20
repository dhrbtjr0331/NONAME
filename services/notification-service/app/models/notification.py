from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, JSON
from sqlalchemy.sql import func
import enum
from app.models import Base

class NotificationType(enum.Enum):
    RFQ_CREATED = "RFQ_CREATED"
    QUOTE_SUBMITTED = "QUOTE_SUBMITTED"
    QUOTE_UPDATED = "QUOTE_UPDATED"
    QUOTE_ACCEPTED = "QUOTE_ACCEPTED"
    QUOTE_REJECTED = "QUOTE_REJECTED"
    RFQ_CLOSED = "RFQ_CLOSED"
    RFQ_DEADLINE_REMINDER = "RFQ_DEADLINE_REMINDER"

class NotificationStatus(enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    RETRY = "RETRY"

class NotificationChannel(enum.Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"
    IN_APP = "IN_APP"

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Recipient Info
    recipient_user_id = Column(Integer, nullable=False, index=True)
    recipient_email = Column(String(255), nullable=False)
    recipient_name = Column(String(100))
    
    # Notification Details
    notification_type = Column(Enum(NotificationType), nullable=False, index=True)
    channel = Column(Enum(NotificationChannel), default=NotificationChannel.EMAIL)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    html_content = Column(Text)  # For rich HTML emails
    
    # Related Entity References
    rfq_id = Column(Integer, index=True)  # References RFQ if applicable
    quote_id = Column(Integer, index=True)  # References Quote if applicable
    
    # Metadata
    context_data = Column(JSON)  # Additional data for templates
    
    # Status & Tracking
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING, index=True)
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    
    # Timestamps
    scheduled_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True))
    failed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Error tracking
    error_message = Column(Text)
    last_error_at = Column(DateTime(timezone=True))

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    
    # Email preferences
    email_rfq_created = Column(Boolean, default=True)
    email_quote_submitted = Column(Boolean, default=True)
    email_quote_accepted = Column(Boolean, default=True)
    email_quote_rejected = Column(Boolean, default=True)
    email_rfq_closed = Column(Boolean, default=True)
    email_deadline_reminders = Column(Boolean, default=True)
    
    # Future: SMS, Push preferences
    sms_enabled = Column(Boolean, default=False)
    push_enabled = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())