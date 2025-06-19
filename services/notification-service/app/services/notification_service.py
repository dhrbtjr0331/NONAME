from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models.notification import Notification, NotificationPreference, NotificationStatus, NotificationType
from app.schemas.notification import NotificationCreate, RFQCreatedEvent, QuoteSubmittedEvent, QuoteAcceptedEvent
from app.services.email_service import EmailService

class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.email_service = EmailService()
    
    async def create_notification(self, notification_data: NotificationCreate) -> Notification:
        """Create a new notification"""
        notification = Notification(**notification_data.dict())
        
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification
    
    async def send_notification(self, notification_id: int) -> bool:
        """Send a single notification"""
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        
        if not notification:
            return False
        
        if notification.status == NotificationStatus.SENT:
            return True  # Already sent
        
        # Attempt to send
        success = False
        notification.attempts += 1
        
        try:
            if notification.channel.value == "EMAIL":
                success = await self.email_service.send_email(
                    to_email=notification.recipient_email,
                    subject=notification.subject,
                    text_content=notification.message,
                    html_content=notification.html_content,
                    to_name=notification.recipient_name
                )
            
            if success:
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.utcnow()
                notification.error_message = None
            else:
                if notification.attempts >= notification.max_attempts:
                    notification.status = NotificationStatus.FAILED
                    notification.failed_at = datetime.utcnow()
                else:
                    notification.status = NotificationStatus.RETRY
                    notification.scheduled_at = datetime.utcnow() + timedelta(minutes=5)
                
        except Exception as e:
            notification.error_message = str(e)
            notification.last_error_at = datetime.utcnow()
            
            if notification.attempts >= notification.max_attempts:
                notification.status = NotificationStatus.FAILED
                notification.failed_at = datetime.utcnow()
            else:
                notification.status = NotificationStatus.RETRY
                notification.scheduled_at = datetime.utcnow() + timedelta(minutes=5)
        
        await self.db.commit()
        return success
    
    async def process_pending_notifications(self, batch_size: int = 100) -> int:
        """Process pending notifications in batches"""
        result = await self.db.execute(
            select(Notification)
            .where(
                and_(
                    or_(
                        Notification.status == NotificationStatus.PENDING,
                        Notification.status == NotificationStatus.RETRY
                    ),
                    Notification.scheduled_at <= datetime.utcnow()
                )
            )
            .limit(batch_size)
        )
        
        notifications = result.scalars().all()
        sent_count = 0
        
        for notification in notifications:
            success = await self.send_notification(notification.id)
            if success:
                sent_count += 1
        
        return sent_count
    
    async def get_user_preferences(self, user_id: int) -> Optional[NotificationPreference]:
        """Get user's notification preferences"""
        result = await self.db.execute(
            select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create_or_update_preferences(
        self, 
        user_id: int, 
        preferences: Dict[str, Any]
    ) -> NotificationPreference:
        """Create or update user notification preferences"""
        existing = await self.get_user_preferences(user_id)
        
        if existing:
            for key, value in preferences.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            prefs = existing
        else:
            prefs = NotificationPreference(user_id=user_id, **preferences)
            self.db.add(prefs)
        
        await self.db.commit()
        await self.db.refresh(prefs)
        return prefs
    
    async def should_send_notification(
        self, 
        user_id: int, 
        notification_type: NotificationType
    ) -> bool:
        """Check if user wants to receive this type of notification"""
        prefs = await self.get_user_preferences(user_id)
        
        if not prefs:
            return True  # Default to sending if no preferences set
        
        # Map notification types to preference fields
        pref_mapping = {
            NotificationType.RFQ_CREATED: prefs.email_rfq_created,
            NotificationType.QUOTE_SUBMITTED: prefs.email_quote_submitted,
            NotificationType.QUOTE_ACCEPTED: prefs.email_quote_accepted,
            NotificationType.QUOTE_REJECTED: prefs.email_quote_rejected,
            NotificationType.RFQ_CLOSED: prefs.email_rfq_closed,
            NotificationType.RFQ_DEADLINE_REMINDER: prefs.email_deadline_reminders,
        }
        
        return pref_mapping.get(notification_type, True)
    
    # Event handlers for different notification types
    async def handle_rfq_created(self, event: RFQCreatedEvent, supplier_emails: List[str]):
        """Create notifications for RFQ created event"""
        notifications_created = 0
        
        for supplier_email in supplier_emails:
            # For MVP, we don't have supplier_id mapping, so we'll use email
            # In production, you'd query user service to get supplier details
            
            context = {
                'rfq_id': event.rfq_id,
                'rfq_title': event.rfq_title,
                'product_category': event.product_category,
                'quantity': event.quantity,
                'unit': 'pieces',  # Default unit for now
                'quote_deadline': event.quote_deadline,
                'description': f"Request for {event.quantity} units in {event.product_category}",
                'supplier_name': supplier_email.split('@')[0].title(),  # Extract name from email
                'platform_url': 'http://localhost:3000'  # Frontend URL
            }
            
            # Render email template
            text_content, html_content = self.email_service.render_template(
                'rfq_created.html', 
                context
            )
            
            notification_data = NotificationCreate(
                recipient_user_id=0,  # Unknown for now
                recipient_email=supplier_email,
                recipient_name=context['supplier_name'],
                notification_type=NotificationType.RFQ_CREATED,
                subject=f"New RFQ: {event.rfq_title}",
                message=text_content,
                html_content=html_content,
                rfq_id=event.rfq_id,
                context_data=context
            )
            
            await self.create_notification(notification_data)
            notifications_created += 1
        
        return notifications_created
    
    async def handle_quote_submitted(self, event: QuoteSubmittedEvent):
        """Create notification for quote submitted event"""
        # Check if manufacturer wants to receive these notifications
        should_send = await self.should_send_notification(
            event.manufacturer_id, 
            NotificationType.QUOTE_SUBMITTED
        )
        
        if not should_send:
            return False
        
        context = {
            'quote_id': event.quote_id,
            'rfq_id': event.rfq_id,
            'rfq_title': event.rfq_title,
            'manufacturer_name': event.manufacturer_name,
            'supplier_name': event.supplier_name,
            'unit_price': event.unit_price,
            'total_price': event.total_price,
            'currency': event.currency,
            'lead_time_days': 30,  # Default for now
            'platform_url': 'http://localhost:3000'
        }
        
        text_content, html_content = self.email_service.render_template(
            'quote_submitted.html',
            context
        )
        
        notification_data = NotificationCreate(
            recipient_user_id=event.manufacturer_id,
            recipient_email=event.manufacturer_email,
            recipient_name=event.manufacturer_name,
            notification_type=NotificationType.QUOTE_SUBMITTED,
            subject=f"New Quote Received for {event.rfq_title}",
            message=text_content,
            html_content=html_content,
            rfq_id=event.rfq_id,
            quote_id=event.quote_id,
            context_data=context
        )
        
        notification = await self.create_notification(notification_data)
        return notification
    
    async def handle_quote_accepted(self, event: QuoteAcceptedEvent):
        """Create notification for quote accepted event"""
        should_send = await self.should_send_notification(
            event.supplier_id,
            NotificationType.QUOTE_ACCEPTED
        )
        
        if not should_send:
            return False
        
        context = {
            'quote_id': event.quote_id,
            'rfq_id': event.rfq_id,
            'rfq_title': event.rfq_title,
            'supplier_name': event.supplier_name,
            'manufacturer_name': event.manufacturer_name,
            'total_price': event.total_price,
            'currency': event.currency,
            'lead_time_days': 30,  # Default
            'payment_terms': 'Net 30',  # Default
            'platform_url': 'http://localhost:3000'
        }
        
        text_content, html_content = self.email_service.render_template(
            'quote_accepted.html',
            context
        )
        
        notification_data = NotificationCreate(
            recipient_user_id=event.supplier_id,
            recipient_email=event.supplier_email,
            recipient_name=event.supplier_name,
            notification_type=NotificationType.QUOTE_ACCEPTED,
            subject=f"🎉 Your Quote for {event.rfq_title} Was Accepted!",
            message=text_content,
            html_content=html_content,
            rfq_id=event.rfq_id,
            quote_id=event.quote_id,
            context_data=context
        )
        
        notification = await self.create_notification(notification_data)
        return notification
    
    async def get_notifications_for_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Notification]:
        """Get notifications for a specific user"""
        result = await self.db.execute(
            select(Notification)
            .where(Notification.recipient_user_id == user_id)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_notification_stats(self) -> Dict[str, int]:
        """Get notification statistics"""
        from sqlalchemy import func
        
        # Count by status
        result = await self.db.execute(
            select(Notification.status, func.count(Notification.id))
            .group_by(Notification.status)
        )
        
        stats = {status.value: 0 for status in NotificationStatus}
        for status, count in result.fetchall():
            stats[status.value] = count
        
        return stats