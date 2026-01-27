"""Analytics schemas - Request/Response models"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any


class AnalyticsBase(BaseModel):
    """Base analytics schema"""
    metric_name: str
    metric_value: float
    metric_unit: Optional[str] = None
    dimensions: Dict[str, Any] = Field(default_factory=dict)
    period_type: Optional[str] = None


class AnalyticsCreate(AnalyticsBase):
    """Schema for creating analytics record"""
    period_start: datetime
    period_end: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AnalyticsInDB(AnalyticsBase):
    """Schema for analytics in database"""
    id: int
    period_start: datetime
    period_end: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
    calculated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class Analytics(AnalyticsInDB):
    """Public analytics schema (response)"""
    pass


class DashboardMetrics(BaseModel):
    """Dashboard metrics summary"""
    # Lead metrics
    total_leads: int
    new_leads_this_month: int
    lead_conversion_rate: float
    avg_lead_score: float
    
    # Client metrics
    total_clients: int
    active_clients: int
    churned_clients: int
    avg_lifetime_value: float
    
    # Communication metrics
    unread_messages: int
    avg_response_time_hours: float
    messages_today: int
    
    # Risk metrics
    high_risk_clients: int
    clients_needing_followup: int
    
    # Timestamp
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class TimeSeriesData(BaseModel):
    """Time series data point"""
    timestamp: datetime
    value: float
    label: Optional[str] = None


class ChartData(BaseModel):
    """Chart data for dashboard"""
    chart_type: str  # line, bar, pie, etc.
    title: str
    data: List[TimeSeriesData]
    metadata: Dict[str, Any] = Field(default_factory=dict)
