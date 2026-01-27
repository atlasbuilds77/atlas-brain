"""
Client Endpoints
/api/clients (CRUD), /api/clients/{id}/risk
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from typing import Optional
import structlog

from app.db.session import get_db
from app.models.client import Client, ClientStatus
from app.schemas.client import (
    ClientCreate, ClientUpdate, Client as ClientSchema,
    ClientList, ClientRisk
)
from app.core.security import get_current_user_id
from app.services.ai_service import AIService

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("", response_model=ClientList)
async def list_clients(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status: Optional[ClientStatus] = None,
    search: Optional[str] = None,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    List all clients (paginated)
    
    - Supports filtering by status
    - Supports search
    - Returns paginated results
    """
    # Build query
    query = select(Client)
    
    if status:
        query = query.where(Client.status == status)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Add pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    query = query.order_by(Client.client_since.desc())
    
    # Execute query
    result = await db.execute(query)
    clients = result.scalars().all()
    
    return ClientList(
        items=clients,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.post("", response_model=ClientSchema, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new client"""
    new_client = Client(**client_data.model_dump())
    
    db.add(new_client)
    await db.commit()
    await db.refresh(new_client)
    
    logger.info("Client created", client_id=new_client.id)
    
    return new_client


@router.get("/{client_id}", response_model=ClientSchema)
async def get_client(
    client_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get client by ID"""
    result = await db.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return client


@router.put("/{client_id}", response_model=ClientSchema)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Update client"""
    result = await db.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Update fields
    update_data = client_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
    
    await db.commit()
    await db.refresh(client)
    
    logger.info("Client updated", client_id=client_id)
    
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Delete client"""
    result = await db.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    await db.execute(delete(Client).where(Client.id == client_id))
    await db.commit()
    
    logger.info("Client deleted", client_id=client_id)


@router.post("/{client_id}/risk", response_model=ClientRisk)
async def assess_client_risk(
    client_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Assess client retention risk using AI
    
    - Analyzes client behavior and history
    - Returns risk score (0-1) and factors
    - Updates client record with new risk score
    """
    result = await db.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Calculate risk
    ai_service = AIService()
    risk_result = await ai_service.assess_client_risk(client)
    
    # Update client
    client.retention_risk_score = risk_result.risk_score
    await db.commit()
    
    logger.info("Client risk assessed", client_id=client_id, risk_score=risk_result.risk_score)
    
    return risk_result
