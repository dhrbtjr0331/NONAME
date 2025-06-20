import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from jinja2 import Environment, FileSystemLoader
import os
from app.config.settings import settings

class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME
        
        # Setup Jinja2 for email templates
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        text_content: str,
        html_content: Optional[str] = None,
        to_name: Optional[str] = None
    ) -> bool:
        """Send email asynchronously"""
        try:
            # Run email sending in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._send_email_sync,
                to_email, subject, text_content, html_content, to_name
            )
            return result
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False
    
    def _send_email_sync(
        self,
        to_email: str,
        subject: str,
        text_content: str,
        html_content: Optional[str] = None,
        to_name: Optional[str] = None
    ) -> bool:
        """Synchronous email sending"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = f"{to_name} <{to_email}>" if to_name else to_email
            msg['Subject'] = subject
            
            # Add text content
            text_part = MIMEText(text_content, 'plain')
            msg.attach(text_part)
            
            # Add HTML content if provided
            if html_content:
                html_part = MIMEText(html_content, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"SMTP Error: {e}")
            return False
    
    def render_template(self, template_name: str, context: dict) -> tuple[str, str]:
        """Render email template and return (text, html)"""
        try:
            template = self.jinja_env.get_template(template_name)
            html_content = template.render(**context)
            
            # Simple HTML to text conversion (strip tags)
            import re
            text_content = re.sub('<[^<]+?>', '', html_content)
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            return text_content, html_content
        except Exception as e:
            print(f"Template rendering failed: {e}")
            return "", ""