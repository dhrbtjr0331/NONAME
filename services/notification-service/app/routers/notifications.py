from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.config.database import get_db
from app.utils.auth_dependencies import get_current_user_info
from app.schemas.notification import (
    NotificationCreate, NotificationResponse, NotificationListItem,
    NotificationPreferenceUpdate, NotificationPreferenceResponse,
    RFQCreatedEvent, QuoteSubmittedEvent, QuoteAcceptedEvent
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_data: NotificationCreate,
    current_user = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db)
):
    """Create a new notification (admin/system use)"""
    notification_service = NotificationService(db)
    notification = await notification_service.create_notification(notification_data)
    return NotificationResponse.from_orm(notification)

@router.get("/my-notifications", response_model=List[NotificationListItem])
async def get_my_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db)
):
    """Get notifications for current user"""
    notification_service = NotificationService(db)
    notifications = await notification_service.get_notifications_for_user(
        user_id=current_user.user_id,
        skip=skip,
        limit=limit
    )
    return [NotificationListItem.from_orm(notification) for notification in notifications]

@router.get("/preferences", response_model=NotificationPreferenceResponse)
async def get_notification_preferences(
    current_user = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db)
):
    """Get user's notification preferences"""
    notification_service = NotificationService(db)
    preferences = await notification_service.get_user_preferences(current_user.user_id)
    
    if not preferences:
        # Create default preferences
        default_prefs = {
            'email_rfq_created': True,
            'email_quote_submitted': True,
            'email_quote_accepted': True,
            'email_quote_rejected': True,
            'email_rfq_closed': True,
            'email_deadline_reminders': True,
            'sms_enabled': False,
            'push_enabled': True
        }
        preferences = await notification_service.create_or_update_preferences(
            current_user.user_id, 
            default_prefs
        )
    
    return NotificationPreferenceResponse.from_orm(preferences)

@router.put("/preferences", response_model=NotificationPreferenceResponse)
async def update_notification_preferences(
    preference_update: NotificationPreferenceUpdate,
    current_user = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db)
):
    """Update user's notification preferences"""
    notification_service = NotificationService(db)
    update_data = preference_update.dict(exclude_unset=True)
    
    preferences = await notification_service.create_or_update_preferences(
        current_user.user_id,
        update_data
    )
    
    return NotificationPreferenceResponse.from_orm(preferences)

# Event webhook endpoints (called by other services)
@router.post("/events/rfq-created")
async def handle_rfq_created_event(
    event: RFQCreatedEvent,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Handle RFQ created event (webhook from quote-service)"""
    notification_service = NotificationService(db)
    
    # For MVP, we'll use a hardcoded list of supplier emails
    # In production, this would query user-service for suppliers in the category
    supplier_emails = [
        "supplier1@example.com",
        "supplier2@example.com",
        "supplier3@example.com"
    ]
    
    # Create notifications in background
    background_tasks.add_task(
        notification_service.handle_rfq_created,
        event,
        supplier_emails
    )
    
    return {"message": "RFQ created notifications queued"}

@router.post("/events/quote-submitted")
async def handle_quote_submitted_event(
    event: QuoteSubmittedEvent,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Handle quote submitted event (webhook from quote-service)"""
    notification_service = NotificationService(db)
    
    # Create notification in background
    background_tasks.add_task(
        notification_service.handle_quote_submitted,
        event
    )
    
    return {"message": "Quote submitted notification queued"}

@router.post("/events/quote-accepted")
async def handle_quote_accepted_event(
    event: QuoteAcceptedEvent,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Handle quote accepted event (webhook from quote-service)"""
    notification_service = NotificationService(db)
    
    # Create notification in background
    background_tasks.add_task(
        notification_service.handle_quote_accepted,
        event
    )
    
    return {"message": "Quote accepted notification queued"}

@router.post("/process-pending")
async def process_pending_notifications(
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user_info),  # Admin only in production
    db: AsyncSession = Depends(get_db)
):
    """Process pending notifications (admin endpoint)"""
    notification_service = NotificationService(db)
    
    background_tasks.add_task(
        notification_service.process_pending_notifications
    )
    
    return {"message": "Processing pending notifications"}

@router.get("/stats")
async def get_notification_stats(
    current_user = Depends(get_current_user_info),  # Admin only in production
    db: AsyncSession = Depends(get_db)
):
    """Get notification statistics (admin endpoint)"""
    notification_service = NotificationService(db)
    stats = await notification_service.get_notification_stats()
    return stats

@router.post("/send/{notification_id}")
async def send_notification(
    notification_id: int,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user_info),  # Admin only in production
    db: AsyncSession = Depends(get_db)
):
    """Manually send a specific notification (admin endpoint)"""
    notification_service = NotificationService(db)
    
    background_tasks.add_task(
        notification_service.send_notification,
        notification_id
    )
    
    return {"message": f"Notification {notification_id} queued for sending"}