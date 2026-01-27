"""
Message Endpoints
/api/messages (CRUD), /api/messages/categorize
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from typing import Optional
import structlog

from app.db.session import get_db
from app.models.message import Message, MessageStatus, MessageCategory
from app.schemas.message import (
    MessageCreate, MessageUpdate, Message as MessageSchema,
    MessageList, MessageCategorize
)
from app.core.security import get_current_user_id
from app.services.ai_service import AIService

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("", response_model=MessageList)
async def list_messages(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status: Optional[MessageStatus] = None,
    category: Optional[MessageCategory] = None,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    List all messages (paginated)
    
    - Supports filtering by status and category
    - Returns paginated results
    """
    # Build query
    query = select(Message)
    
    if status:
        query = query.where(Message.status == status)
    
    if category:
        query = query.where(Message.category == category)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Add pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    query = query.order_by(Message.received_at.desc())
    
    # Execute query
    result = await db.execute(query)
    messages = result.scalars().all()
    
    return MessageList(
        items=messages,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.post("", response_model=MessageSchema, status_code=status.HTTP_201_CREATED)
async def create_message(
    message_data: MessageCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new message
    
    - Creates message record
    - Automatically categorizes using AI
    """
    new_message = Message(**message_data.model_dump())
    
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    
    # Categorize message (async task in production)
    try:
        ai_service = AIService()
        categorization = await ai_service.categorize_message(new_message)
        new_message.category = categorization.category
        new_message.sentiment_score = categorization.sentiment_score
        new_message.priority_score = categorization.priority_score
        new_message.ai_summary = categorization.summary
        await db.commit()
    except Exception as e:
        logger.warning("Failed to categorize message", message_id=new_message.id, error=str(e))
    
    logger.info("Message created", message_id=new_message.id)
    
    return new_message


@router.get("/{message_id}", response_model=MessageSchema)
async def get_message(
    message_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get message by ID"""
    result = await db.execute(
        select(Message).where(Message.id == message_id)
    )
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Mark as read if unread
    if message.status == MessageStatus.UNREAD:
        from datetime import datetime
        message.status = MessageStatus.READ
        message.read_at = datetime.utcnow()
        await db.commit()
    
    return message


@router.put("/{message_id}", response_model=MessageSchema)
async def update_message(
    message_id: int,
    message_data: MessageUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Update message"""
    result = await db.execute(
        select(Message).where(Message.id == message_id)
    )
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Update fields
    update_data = message_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(message, field, value)
    
    await db.commit()
    await db.refresh(message)
    
    logger.info("Message updated", message_id=message_id)
    
    return message


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Delete message"""
    result = await db.execute(
        select(Message).where(Message.id == message_id)
    )
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    await db.execute(delete(Message).where(Message.id == message_id))
    await db.commit()
    
    logger.info("Message deleted", message_id=message_id)


@router.post("/categorize", response_model=MessageCategorize)
async def categorize_message(
    message_id: int = Query(..., description="Message ID to categorize"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Categorize a message using AI
    
    - Analyzes message content
    - Returns category, sentiment, priority
    - Updates message record
    """
    result = await db.execute(
        select(Message).where(Message.id == message_id)
    )
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Categorize
    ai_service = AIService()
    categorization = await ai_service.categorize_message(message)
    
    # Update message
    message.category = categorization.category
    message.sentiment_score = categorization.sentiment_score
    message.priority_score = categorization.priority_score
    message.ai_summary = categorization.summary
    await db.commit()
    
    logger.info("Message categorized", message_id=message_id, category=categorization.category)
    
    return categorization
