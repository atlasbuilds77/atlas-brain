"""
Email Service - IMAP ingestion and SMTP sending
Handles email fetching, parsing, and sending
"""

import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
import structlog
import asyncio
from datetime import datetime
import smtplib

from app.core.config import settings
from app.models.message import Message, MessageChannel
from app.db.session import AsyncSessionLocal

logger = structlog.get_logger(__name__)


class EmailService:
    """Email ingestion and sending service"""
    
    def __init__(self):
        """Initialize email service"""
        self.imap_host = settings.IMAP_HOST
        self.imap_port = settings.IMAP_PORT
        self.imap_username = settings.IMAP_USERNAME
        self.imap_password = settings.IMAP_PASSWORD
        self.imap_use_ssl = settings.IMAP_USE_SSL
        
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_use_tls = settings.SMTP_USE_TLS
    
    async def fetch_new_emails(self, folder: str = "INBOX") -> List[Dict[str, Any]]:
        """
        Fetch new emails from IMAP server
        
        Args:
            folder: IMAP folder to check (default: INBOX)
        
        Returns:
            List of parsed email messages
        """
        if not self.imap_username or not self.imap_password:
            logger.warning("IMAP credentials not configured")
            return []
        
        try:
            # Connect to IMAP server
            if self.imap_use_ssl:
                mail = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
            else:
                mail = imaplib.IMAP4(self.imap_host, self.imap_port)
            
            # Login
            mail.login(self.imap_username, self.imap_password)
            
            # Select folder
            mail.select(folder)
            
            # Search for unseen messages
            status, messages = mail.search(None, 'UNSEEN')
            
            if status != 'OK':
                logger.error("Failed to search for emails")
                return []
            
            email_ids = messages[0].split()
            parsed_emails = []
            
            # Fetch each email
            for email_id in email_ids[-10:]:  # Limit to last 10 new emails
                try:
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    
                    if status != 'OK':
                        continue
                    
                    # Parse email
                    raw_email = msg_data[0][1]
                    email_message = email.message_from_bytes(raw_email)
                    
                    parsed_email = await self._parse_email(email_message)
                    parsed_emails.append(parsed_email)
                    
                except Exception as e:
                    logger.error("Failed to parse email", email_id=email_id, error=str(e))
            
            # Close connection
            mail.close()
            mail.logout()
            
            logger.info("Fetched emails", count=len(parsed_emails))
            
            return parsed_emails
            
        except Exception as e:
            logger.error("Failed to fetch emails", error=str(e))
            return []
    
    async def _parse_email(self, email_message) -> Dict[str, Any]:
        """Parse email message into dict"""
        
        # Extract basic fields
        subject = email_message.get('Subject', '')
        from_address = email.utils.parseaddr(email_message.get('From', ''))[1]
        to_address = email.utils.parseaddr(email_message.get('To', ''))[1]
        message_id = email_message.get('Message-ID', '')
        in_reply_to = email_message.get('In-Reply-To', '')
        date_str = email_message.get('Date', '')
        
        # Parse date
        try:
            sent_at = email.utils.parsedate_to_datetime(date_str)
        except:
            sent_at = datetime.utcnow()
        
        # Extract body
        body = ""
        html_body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass
                
                elif content_type == "text/html":
                    try:
                        html_body = part.get_payload(decode=True).decode()
                    except:
                        pass
        else:
            try:
                body = email_message.get_payload(decode=True).decode()
            except:
                body = str(email_message.get_payload())
        
        return {
            "from_address": from_address,
            "to_address": to_address,
            "subject": subject,
            "body": body,
            "html_body": html_body,
            "message_id": message_id,
            "in_reply_to": in_reply_to,
            "sent_at": sent_at,
            "channel": MessageChannel.EMAIL
        }
    
    async def save_emails_to_db(self, emails: List[Dict[str, Any]]):
        """Save fetched emails to database"""
        
        if not emails:
            return
        
        async with AsyncSessionLocal() as db:
            try:
                for email_data in emails:
                    # Check if message already exists (by message_id)
                    from sqlalchemy import select
                    
                    message_id = email_data.get('message_id')
                    if message_id:
                        result = await db.execute(
                            select(Message).where(Message.in_reply_to == message_id)
                        )
                        existing = result.scalar_one_or_none()
                        if existing:
                            continue  # Skip duplicates
                    
                    # Create message
                    message = Message(
                        from_address=email_data['from_address'],
                        to_address=email_data['to_address'],
                        subject=email_data.get('subject'),
                        body=email_data.get('body'),
                        html_body=email_data.get('html_body'),
                        in_reply_to=email_data.get('message_id'),
                        sent_at=email_data['sent_at'],
                        channel=email_data['channel']
                    )
                    
                    db.add(message)
                
                await db.commit()
                
                logger.info("Emails saved to database", count=len(emails))
                
            except Exception as e:
                logger.error("Failed to save emails", error=str(e))
                await db.rollback()
    
    async def send_email(
        self,
        to_address: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        from_address: Optional[str] = None
    ) -> bool:
        """
        Send email via SMTP
        
        Args:
            to_address: Recipient email
            subject: Email subject
            body: Plain text body
            html_body: HTML body (optional)
            from_address: Sender email (default from settings)
        
        Returns:
            True if sent successfully
        """
        if not self.smtp_username or not self.smtp_password:
            logger.warning("SMTP credentials not configured")
            return False
        
        from_address = from_address or settings.SMTP_FROM_EMAIL
        
        try:
            # Create message
            if html_body:
                msg = MIMEMultipart('alternative')
                msg.attach(MIMEText(body, 'plain'))
                msg.attach(MIMEText(html_body, 'html'))
            else:
                msg = MIMEText(body, 'plain')
            
            msg['Subject'] = subject
            msg['From'] = f"{settings.SMTP_FROM_NAME} <{from_address}>"
            msg['To'] = to_address
            
            # Connect to SMTP server
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls()
                
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info("Email sent", to=to_address, subject=subject)
            
            return True
            
        except Exception as e:
            logger.error("Failed to send email", error=str(e))
            return False
    
    async def start_email_ingestion_loop(self):
        """
        Background task to continuously fetch new emails
        Run this as a Celery task or background process
        """
        logger.info("Starting email ingestion loop")
        
        while True:
            try:
                # Fetch new emails
                emails = await self.fetch_new_emails()
                
                # Save to database
                if emails:
                    await self.save_emails_to_db(emails)
                
                # Wait before next check
                await asyncio.sleep(settings.IMAP_CHECK_INTERVAL)
                
            except Exception as e:
                logger.error("Email ingestion loop error", error=str(e))
                await asyncio.sleep(60)  # Wait 1 minute on error
