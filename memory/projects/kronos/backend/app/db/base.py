"""Import base and all models"""

from app.db.session import Base

# Import all models to ensure they're registered with Base
from app.models.user import User
from app.models.lead import Lead
from app.models.client import Client
from app.models.message import Message
from app.models.file import File
from app.models.task import Task
from app.models.analytics import Analytics

__all__ = ["Base", "User", "Lead", "Client", "Message", "File", "Task", "Analytics"]
