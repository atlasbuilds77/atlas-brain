"""
Lead Endpoints
/api/leads (CRUD), /api/leads/{id}/score
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from typing import Optional
import structlog

from app.db.session import get_db
from app.models.lead import Lead, LeadStatus
from app.schemas.lead import (
    LeadCreate, LeadUpdate, Lead as LeadSchema,
    LeadList, LeadScore
)
from app.core.security import get_current_user_id
from app.services.ai_service import AIService

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("", response_model=LeadList)
async def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status: Optional[LeadStatus] = None,
    search: Optional[str] = None,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    List all leads (paginated)
    
    - Supports filtering by status
    - Supports search by name/email
    - Returns paginated results
    """
    # Build query
    query = select(Lead)
    
    if status:
        query = query.where(Lead.status == status)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            (Lead.name.ilike(search_term)) |
            (Lead.email.ilike(search_term)) |
            (Lead.phone.ilike(search_term))
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Add pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    query = query.order_by(Lead.created_at.desc())
    
    # Execute query
    result = await db.execute(query)
    leads = result.scalars().all()
    
    return LeadList(
        items=leads,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.post("", response_model=LeadSchema, status_code=status.HTTP_201_CREATED)
async def create_lead(
    lead_data: LeadCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new lead
    
    - Creates lead record
    - Automatically calculates initial lead score
    """
    new_lead = Lead(**lead_data.model_dump())
    
    db.add(new_lead)
    await db.commit()
    await db.refresh(new_lead)
    
    # Calculate initial lead score (async task in production)
    try:
        ai_service = AIService()
        score_result = await ai_service.score_lead(new_lead)
        new_lead.lead_score = score_result.score
        await db.commit()
    except Exception as e:
        logger.warning("Failed to calculate lead score", lead_id=new_lead.id, error=str(e))
    
    logger.info("Lead created", lead_id=new_lead.id, name=new_lead.name)
    
    return new_lead


@router.get("/{lead_id}", response_model=LeadSchema)
async def get_lead(
    lead_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get lead by ID"""
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id)
    )
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    return lead


@router.put("/{lead_id}", response_model=LeadSchema)
async def update_lead(
    lead_id: int,
    lead_data: LeadUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Update lead"""
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id)
    )
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Update fields
    update_data = lead_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)
    
    await db.commit()
    await db.refresh(lead)
    
    logger.info("Lead updated", lead_id=lead_id)
    
    return lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Delete lead"""
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id)
    )
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    await db.execute(delete(Lead).where(Lead.id == lead_id))
    await db.commit()
    
    logger.info("Lead deleted", lead_id=lead_id)


@router.post("/{lead_id}/score", response_model=LeadScore)
async def score_lead(
    lead_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate lead score using AI
    
    - Analyzes lead data
    - Returns score (0-100) and factors
    - Updates lead record with new score
    """
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id)
    )
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Calculate score
    ai_service = AIService()
    score_result = await ai_service.score_lead(lead)
    
    # Update lead
    lead.lead_score = score_result.score
    await db.commit()
    
    logger.info("Lead scored", lead_id=lead_id, score=score_result.score)
    
    return score_result
