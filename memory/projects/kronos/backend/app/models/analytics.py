"""Analytics model - Metrics and KPI tracking"""

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Index
from sqlalchemy.sql import func

from app.db.session import Base


class Analytics(Base):
    """Analytics model - metrics and KPI tracking"""
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Metric details
    metric_name = Column(String, nullable=False, index=True)  # lead_conversion_rate, response_time, etc.
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String)  # percentage, minutes, count, etc.
    
    # Dimensions (for filtering/grouping)
    dimensions = Column(JSON, default=dict)  # {"lead_source": "website", "month": "2024-01"}
    
    # Period
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False, index=True)
    period_type = Column(String)  # daily, weekly, monthly, yearly
    
    # Metadata
    metadata = Column(JSON, default=dict)  # Additional context
    
    # Timestamps
    calculated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_analytics_metric_period', 'metric_name', 'period_start', 'period_end'),
    )
    
    def __repr__(self):
        return f"<Analytics {self.metric_name}={self.metric_value}>"
