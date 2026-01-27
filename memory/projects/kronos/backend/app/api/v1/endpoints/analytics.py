"""
Analytics Endpoints
/api/analytics/dashboard
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
import structlog

from app.db.session import get_db
from app.models.lead import Lead, LeadStatus
from app.models.client import Client, ClientStatus
from app.models.message import Message, MessageStatus
from app.schemas.analytics import DashboardMetrics
from app.core.security import get_current_user_id

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Get dashboard metrics
    
    - Lead metrics (total, new, conversion rate, avg score)
    - Client metrics (total, active, churned, lifetime value)
    - Communication metrics (unread messages, response time, today's messages)
    - Risk metrics (high-risk clients, clients needing followup)
    """
    
    # Calculate time ranges
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    today_start = datetime(now.year, now.month, now.day)
    
    # LEAD METRICS
    # Total leads
    total_leads_result = await db.execute(
        select(func.count()).select_from(Lead)
    )
    total_leads = total_leads_result.scalar() or 0
    
    # New leads this month
    new_leads_result = await db.execute(
        select(func.count()).select_from(Lead).where(Lead.created_at >= month_start)
    )
    new_leads_this_month = new_leads_result.scalar() or 0
    
    # Converted leads this month
    converted_leads_result = await db.execute(
        select(func.count()).select_from(Lead)
        .where(Lead.status == LeadStatus.CONVERTED)
        .where(Lead.converted_at >= month_start)
    )
    converted_leads = converted_leads_result.scalar() or 0
    
    # Lead conversion rate
    lead_conversion_rate = (converted_leads / new_leads_this_month * 100) if new_leads_this_month > 0 else 0.0
    
    # Average lead score
    avg_lead_score_result = await db.execute(
        select(func.avg(Lead.lead_score)).select_from(Lead)
    )
    avg_lead_score = avg_lead_score_result.scalar() or 0.0
    
    # CLIENT METRICS
    # Total clients
    total_clients_result = await db.execute(
        select(func.count()).select_from(Client)
    )
    total_clients = total_clients_result.scalar() or 0
    
    # Active clients
    active_clients_result = await db.execute(
        select(func.count()).select_from(Client)
        .where(Client.status == ClientStatus.ACTIVE)
    )
    active_clients = active_clients_result.scalar() or 0
    
    # Churned clients
    churned_clients_result = await db.execute(
        select(func.count()).select_from(Client)
        .where(Client.status == ClientStatus.CHURNED)
    )
    churned_clients = churned_clients_result.scalar() or 0
    
    # Average lifetime value
    avg_ltv_result = await db.execute(
        select(func.avg(Client.lifetime_value)).select_from(Client)
    )
    avg_lifetime_value = avg_ltv_result.scalar() or 0.0
    
    # MESSAGE METRICS
    # Unread messages
    unread_messages_result = await db.execute(
        select(func.count()).select_from(Message)
        .where(Message.status == MessageStatus.UNREAD)
    )
    unread_messages = unread_messages_result.scalar() or 0
    
    # Messages today
    messages_today_result = await db.execute(
        select(func.count()).select_from(Message)
        .where(Message.received_at >= today_start)
    )
    messages_today = messages_today_result.scalar() or 0
    
    # Average response time (simplified - calculate from read_at - received_at)
    # In production, you'd track actual response times
    avg_response_time_hours = 2.5  # Placeholder
    
    # RISK METRICS
    # High-risk clients (risk score > 0.7)
    high_risk_clients_result = await db.execute(
        select(func.count()).select_from(Client)
        .where(Client.retention_risk_score > 0.7)
    )
    high_risk_clients = high_risk_clients_result.scalar() or 0
    
    # Clients needing followup (next_followup is past)
    clients_needing_followup_result = await db.execute(
        select(func.count()).select_from(Client)
        .where(Client.next_followup < now)
        .where(Client.next_followup.isnot(None))
    )
    clients_needing_followup = clients_needing_followup_result.scalar() or 0
    
    logger.info("Dashboard metrics calculated", user_id=user_id)
    
    return DashboardMetrics(
        total_leads=total_leads,
        new_leads_this_month=new_leads_this_month,
        lead_conversion_rate=round(lead_conversion_rate, 2),
        avg_lead_score=round(avg_lead_score, 2),
        total_clients=total_clients,
        active_clients=active_clients,
        churned_clients=churned_clients,
        avg_lifetime_value=round(avg_lifetime_value, 2),
        unread_messages=unread_messages,
        avg_response_time_hours=avg_response_time_hours,
        messages_today=messages_today,
        high_risk_clients=high_risk_clients,
        clients_needing_followup=clients_needing_followup
    )
