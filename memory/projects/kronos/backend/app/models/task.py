"""Task model - Organizers, reminders, and to-dos"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class TaskType(str, enum.Enum):
    """Task types"""
    ORGANIZER = "organizer"  # Tax organizer, intake form
    REMINDER = "reminder"  # Follow-up reminder
    TODO = "todo"  # General task
    DEADLINE = "deadline"  # Important deadline


class TaskStatus(str, enum.Enum):
    """Task status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class Task(Base):
    """Task model - organizers, reminders, deadlines"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Task details
    title = Column(String, nullable=False)
    description = Column(Text)
    type = Column(SQLEnum(TaskType), nullable=False, index=True)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False, index=True)
    
    # Associations
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True, index=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Template support (for organizers)
    template_id = Column(String, index=True)  # Reference to template
    template_data = Column(JSON, default=dict)  # Template-specific data
    
    # Scheduling
    due_date = Column(DateTime(timezone=True), index=True)
    reminder_date = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Tracking
    sent_at = Column(DateTime(timezone=True))  # For organizers
    opened_at = Column(DateTime(timezone=True))  # Track when client opened it
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String)  # RRULE format
    
    # Metadata
    priority = Column(Integer, default=3)  # 1-5
    tags = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="tasks")
    
    def __repr__(self):
        return f"<Task {self.title} - {self.status}>"
