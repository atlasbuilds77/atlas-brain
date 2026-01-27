"""
Celery Tasks - Background task processing
Email ingestion, analytics calculation, etc.
"""

from celery import Celery
import structlog

from app.core.config import settings
from app.services.email_service import EmailService
from app.services.ai_service import AIService

logger = structlog.get_logger(__name__)

# Initialize Celery
celery_app = Celery(
    "kronos",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


@celery_app.task(name="tasks.fetch_emails")
def fetch_emails():
    """Periodic task to fetch new emails"""
    import asyncio
    
    logger.info("Running email fetch task")
    
    email_service = EmailService()
    
    # Run async function in sync context
    loop = asyncio.get_event_loop()
    emails = loop.run_until_complete(email_service.fetch_new_emails())
    
    if emails:
        loop.run_until_complete(email_service.save_emails_to_db(emails))
    
    return f"Fetched {len(emails)} emails"


@celery_app.task(name="tasks.calculate_daily_metrics")
def calculate_daily_metrics():
    """Calculate daily analytics metrics"""
    logger.info("Running daily metrics calculation")
    
    # This would calculate and store metrics in analytics table
    # Implementation depends on specific metrics needed
    
    return "Daily metrics calculated"


@celery_app.task(name="tasks.send_daily_digest")
def send_daily_digest():
    """Send daily digest to users"""
    logger.info("Running daily digest task")
    
    # This would generate and send daily digest emails
    # Implementation depends on digest format
    
    return "Daily digest sent"


@celery_app.task(name="tasks.cleanup_old_files")
def cleanup_old_files():
    """Clean up files past retention date"""
    logger.info("Running file cleanup task")
    
    # This would delete files past their retention_until date
    # Implementation depends on storage service
    
    return "File cleanup completed"


# Celery Beat Schedule (for periodic tasks)
celery_app.conf.beat_schedule = {
    'fetch-emails-every-5-minutes': {
        'task': 'tasks.fetch_emails',
        'schedule': 300.0,  # 5 minutes
    },
    'calculate-daily-metrics': {
        'task': 'tasks.calculate_daily_metrics',
        'schedule': {
            'hour': 0,
            'minute': 0,
        },
    },
    'send-daily-digest': {
        'task': 'tasks.send_daily_digest',
        'schedule': {
            'hour': 6,
            'minute': 0,
        },
    },
    'cleanup-old-files': {
        'task': 'tasks.cleanup_old_files',
        'schedule': {
            'hour': 2,
            'minute': 0,
        },
    },
}
