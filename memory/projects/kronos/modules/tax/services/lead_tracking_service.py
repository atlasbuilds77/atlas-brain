"""
Lead Tracking Service
Kronos Tax Module - Lead source tracking and ROI analytics
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum

from ..config.settings import LEAD_SOURCE_CONFIG


class LeadStatus(Enum):
    """Lead status values."""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL_SENT = "proposal_sent"
    CONVERTED = "converted"
    LOST = "lost"
    DEAD = "dead"


@dataclass
class LeadSource:
    """Lead source definition."""
    id: str
    name: str
    category: str  # online, offline, referral, retention
    is_active: bool = True
    
    # Cost tracking
    monthly_cost: float = 0.0
    cost_per_lead: float = 0.0
    
    # Performance metrics (calculated)
    total_leads: int = 0
    converted_leads: int = 0
    conversion_rate: float = 0.0
    total_revenue: float = 0.0
    roi: float = 0.0


@dataclass
class LeadSourceTag:
    """Tag linking a lead to its source."""
    id: Optional[int] = None
    lead_id: int = 0
    source_id: str = ""
    campaign: Optional[str] = None
    medium: Optional[str] = None  # e.g., cpc, organic, direct
    keyword: Optional[str] = None  # For paid search
    landing_page: Optional[str] = None
    referrer_id: Optional[int] = None  # For referral tracking
    created_at: datetime = field(default_factory=datetime.now)
    
    # Attribution
    first_touch: bool = True  # First touchpoint?
    attribution_weight: float = 1.0


@dataclass
class Campaign:
    """Marketing campaign for tracking."""
    id: Optional[int] = None
    name: str = ""
    source_id: str = ""
    start_date: date = None
    end_date: date = None
    budget: float = 0.0
    actual_spend: float = 0.0
    
    # Performance
    leads_generated: int = 0
    conversions: int = 0
    revenue: float = 0.0
    
    # Status
    is_active: bool = True
    
    @property
    def roi(self) -> float:
        """Calculate campaign ROI."""
        if self.actual_spend == 0:
            return 0.0
        return ((self.revenue - self.actual_spend) / self.actual_spend) * 100
    
    @property
    def cost_per_lead(self) -> float:
        """Calculate cost per lead."""
        if self.leads_generated == 0:
            return 0.0
        return self.actual_spend / self.leads_generated
    
    @property
    def cost_per_acquisition(self) -> float:
        """Calculate cost per acquisition."""
        if self.conversions == 0:
            return 0.0
        return self.actual_spend / self.conversions


class LeadTrackingService:
    """
    Service for tracking lead sources and calculating ROI.
    
    Handles:
    - Tagging leads by source
    - Campaign tracking
    - Conversion tracking
    - ROI analytics
    """
    
    def __init__(self, db=None):
        """
        Initialize lead tracking service.
        
        Args:
            db: Database connection
        """
        self.db = db
        self.config = LEAD_SOURCE_CONFIG
        self._sources = {s["id"]: LeadSource(**s) for s in self.config["sources"]}
    
    # =========================================================================
    # LEAD TAGGING
    # =========================================================================
    
    def tag_lead(
        self,
        lead_id: int,
        source: str,
        campaign: str = None,
        medium: str = None,
        keyword: str = None,
        landing_page: str = None,
        referrer_id: int = None
    ) -> LeadSourceTag:
        """
        Tag a lead with its source.
        
        Args:
            lead_id: Lead ID
            source: Source ID (google, website, referral, etc.)
            campaign: Campaign name (optional)
            medium: Medium (cpc, organic, etc.)
            keyword: Search keyword (for paid)
            landing_page: Landing page URL
            referrer_id: Client ID for referrals
            
        Returns:
            Created LeadSourceTag
        """
        # Validate source
        if source not in self._sources:
            source = self.config["default_source"]
        
        tag = LeadSourceTag(
            lead_id=lead_id,
            source_id=source,
            campaign=campaign,
            medium=medium,
            keyword=keyword,
            landing_page=landing_page,
            referrer_id=referrer_id,
        )
        
        if self.db:
            tag.id = self._save_tag(tag)
        
        return tag
    
    def get_lead_source(self, lead_id: int) -> Optional[LeadSourceTag]:
        """Get source tag for a lead."""
        if self.db:
            return self._load_lead_tag(lead_id)
        return None
    
    def update_lead_source(
        self,
        lead_id: int,
        source: str,
        **kwargs
    ) -> LeadSourceTag:
        """Update lead source tag."""
        tag = self.get_lead_source(lead_id)
        
        if tag is None:
            return self.tag_lead(lead_id, source, **kwargs)
        
        tag.source_id = source
        for key, value in kwargs.items():
            if hasattr(tag, key):
                setattr(tag, key, value)
        
        if self.db:
            self._update_tag(tag)
        
        return tag
    
    def auto_detect_source(
        self,
        referrer_url: str = None,
        utm_source: str = None,
        utm_medium: str = None,
        utm_campaign: str = None
    ) -> Tuple[str, Dict[str, str]]:
        """
        Auto-detect lead source from referrer/UTM parameters.
        
        Args:
            referrer_url: HTTP referrer
            utm_source: UTM source parameter
            utm_medium: UTM medium parameter
            utm_campaign: UTM campaign parameter
            
        Returns:
            Tuple of (source_id, metadata_dict)
        """
        metadata = {
            "campaign": utm_campaign,
            "medium": utm_medium,
        }
        
        # Priority 1: UTM parameters
        if utm_source:
            if "google" in utm_source.lower():
                return "google", metadata
            elif "facebook" in utm_source.lower():
                return "social", metadata
            elif "yelp" in utm_source.lower():
                return "yelp", metadata
            else:
                # Try to match to known source
                for source_id in self._sources:
                    if source_id in utm_source.lower():
                        return source_id, metadata
        
        # Priority 2: Referrer URL
        if referrer_url:
            referrer_lower = referrer_url.lower()
            if "google" in referrer_lower:
                return "google", metadata
            elif "facebook" in referrer_lower or "instagram" in referrer_lower:
                return "social", metadata
            elif "yelp" in referrer_lower:
                return "yelp", metadata
            # Check if from own website (internal)
            # This would be "website" source
        
        # Default to website if came from contact form
        if utm_medium == "form":
            return "website", metadata
        
        return self.config["default_source"], metadata
    
    # =========================================================================
    # CONVERSION TRACKING
    # =========================================================================
    
    def record_conversion(
        self,
        lead_id: int,
        client_id: int,
        revenue: float = 0.0
    ) -> Dict[str, Any]:
        """
        Record lead conversion to client.
        
        Args:
            lead_id: Lead ID
            client_id: New client ID
            revenue: Initial revenue amount
            
        Returns:
            Conversion record
        """
        conversion = {
            "lead_id": lead_id,
            "client_id": client_id,
            "converted_at": datetime.now(),
            "revenue": revenue,
        }
        
        # Get source for attribution
        tag = self.get_lead_source(lead_id)
        if tag:
            conversion["source_id"] = tag.source_id
            conversion["campaign"] = tag.campaign
            
            # Update campaign stats if applicable
            if tag.campaign:
                self._update_campaign_conversion(tag.campaign, revenue)
        
        if self.db:
            self._save_conversion(conversion)
        
        return conversion
    
    def update_client_revenue(
        self,
        client_id: int,
        revenue: float
    ):
        """
        Update total revenue for a client (for ROI tracking).
        
        Args:
            client_id: Client ID
            revenue: Additional revenue to add
        """
        if self.db:
            # Get original lead
            lead_id = self._get_lead_id_for_client(client_id)
            if lead_id:
                tag = self.get_lead_source(lead_id)
                if tag:
                    self._add_source_revenue(tag.source_id, revenue)
                    if tag.campaign:
                        self._add_campaign_revenue(tag.campaign, revenue)
    
    def get_conversion_rate(
        self,
        source: str = None,
        campaign: str = None,
        start_date: date = None,
        end_date: date = None
    ) -> float:
        """
        Calculate conversion rate.
        
        Args:
            source: Filter by source
            campaign: Filter by campaign
            start_date: Period start
            end_date: Period end
            
        Returns:
            Conversion rate as percentage
        """
        if self.db:
            total_leads = self._count_leads(
                source=source,
                campaign=campaign,
                start_date=start_date,
                end_date=end_date
            )
            conversions = self._count_conversions(
                source=source,
                campaign=campaign,
                start_date=start_date,
                end_date=end_date
            )
            
            if total_leads > 0:
                return (conversions / total_leads) * 100
        
        return 0.0
    
    # =========================================================================
    # CAMPAIGN MANAGEMENT
    # =========================================================================
    
    def create_campaign(
        self,
        name: str,
        source: str,
        start_date: date,
        end_date: date = None,
        budget: float = 0.0
    ) -> Campaign:
        """
        Create a marketing campaign for tracking.
        
        Args:
            name: Campaign name
            source: Lead source ID
            start_date: Campaign start
            end_date: Campaign end
            budget: Campaign budget
            
        Returns:
            Created Campaign
        """
        campaign = Campaign(
            name=name,
            source_id=source,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
        )
        
        if self.db:
            campaign.id = self._save_campaign(campaign)
        
        return campaign
    
    def update_campaign_spend(
        self,
        campaign_name: str,
        spend: float
    ):
        """Update campaign actual spend."""
        if self.db:
            self._add_campaign_spend(campaign_name, spend)
    
    def get_campaign_performance(
        self,
        campaign_name: str
    ) -> Optional[Campaign]:
        """Get campaign with performance metrics."""
        if self.db:
            return self._load_campaign_with_stats(campaign_name)
        return None
    
    def get_active_campaigns(self) -> List[Campaign]:
        """Get all active campaigns."""
        if self.db:
            return self._load_active_campaigns()
        return []
    
    # =========================================================================
    # ROI REPORTING
    # =========================================================================
    
    def get_roi_report(
        self,
        year: int = None,
        start_date: date = None,
        end_date: date = None
    ) -> Dict[str, Any]:
        """
        Generate ROI report by lead source.
        
        Args:
            year: Filter by year (shortcut for full year)
            start_date: Custom period start
            end_date: Custom period end
            
        Returns:
            Comprehensive ROI report
        """
        # Set date range
        if year:
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
        elif start_date is None:
            start_date = date.today() - timedelta(days=365)
            end_date = date.today()
        
        report = {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "summary": {
                "total_leads": 0,
                "total_conversions": 0,
                "total_revenue": 0.0,
                "total_cost": 0.0,
                "overall_roi": 0.0,
                "overall_conversion_rate": 0.0,
            },
            "by_source": [],
            "by_campaign": [],
            "top_performers": [],
            "underperformers": [],
        }
        
        if self.db:
            # Get stats by source
            source_stats = self._get_source_stats(start_date, end_date)
            
            for source_id, stats in source_stats.items():
                source = self._sources.get(source_id)
                if source:
                    source_data = {
                        "id": source_id,
                        "name": source.name,
                        "category": source.category,
                        "leads": stats["leads"],
                        "conversions": stats["conversions"],
                        "conversion_rate": (
                            (stats["conversions"] / stats["leads"]) * 100 
                            if stats["leads"] > 0 else 0
                        ),
                        "revenue": stats["revenue"],
                        "cost": stats["cost"],
                        "roi": (
                            ((stats["revenue"] - stats["cost"]) / stats["cost"]) * 100
                            if stats["cost"] > 0 else 0
                        ),
                        "cost_per_lead": (
                            stats["cost"] / stats["leads"]
                            if stats["leads"] > 0 else 0
                        ),
                        "cost_per_acquisition": (
                            stats["cost"] / stats["conversions"]
                            if stats["conversions"] > 0 else 0
                        ),
                    }
                    report["by_source"].append(source_data)
                    
                    # Update summary
                    report["summary"]["total_leads"] += stats["leads"]
                    report["summary"]["total_conversions"] += stats["conversions"]
                    report["summary"]["total_revenue"] += stats["revenue"]
                    report["summary"]["total_cost"] += stats["cost"]
            
            # Calculate overall metrics
            if report["summary"]["total_leads"] > 0:
                report["summary"]["overall_conversion_rate"] = (
                    report["summary"]["total_conversions"] / 
                    report["summary"]["total_leads"]
                ) * 100
            
            if report["summary"]["total_cost"] > 0:
                report["summary"]["overall_roi"] = (
                    (report["summary"]["total_revenue"] - report["summary"]["total_cost"]) /
                    report["summary"]["total_cost"]
                ) * 100
            
            # Sort for top performers (by ROI)
            sorted_sources = sorted(
                report["by_source"],
                key=lambda x: x["roi"],
                reverse=True
            )
            report["top_performers"] = sorted_sources[:3]
            report["underperformers"] = sorted_sources[-3:]
            
            # Get campaign stats
            campaign_stats = self._get_campaign_stats(start_date, end_date)
            report["by_campaign"] = campaign_stats
        
        return report
    
    def get_source_comparison(
        self,
        sources: List[str] = None,
        metric: str = "conversion_rate"
    ) -> List[Dict[str, Any]]:
        """
        Compare sources by specific metric.
        
        Args:
            sources: List of source IDs to compare (all if None)
            metric: Metric to compare (conversion_rate, roi, cost_per_lead)
            
        Returns:
            Sorted list of sources by metric
        """
        if sources is None:
            sources = list(self._sources.keys())
        
        results = []
        
        if self.db:
            for source_id in sources:
                stats = self._get_source_stats_single(source_id)
                if stats:
                    results.append({
                        "source_id": source_id,
                        "source_name": self._sources[source_id].name,
                        "value": stats.get(metric, 0),
                        "leads": stats.get("leads", 0),
                        "conversions": stats.get("conversions", 0),
                    })
        
        # Sort by metric
        results.sort(key=lambda x: x["value"], reverse=True)
        
        return results
    
    # =========================================================================
    # LEAD SOURCE MANAGEMENT
    # =========================================================================
    
    def get_available_sources(self) -> List[LeadSource]:
        """Get all configured lead sources."""
        return list(self._sources.values())
    
    def add_custom_source(
        self,
        id: str,
        name: str,
        category: str = "other"
    ) -> LeadSource:
        """Add a custom lead source."""
        source = LeadSource(
            id=id,
            name=name,
            category=category,
        )
        self._sources[id] = source
        
        if self.db:
            self._save_source(source)
        
        return source
    
    def set_source_cost(
        self,
        source_id: str,
        monthly_cost: float = None,
        cost_per_lead: float = None
    ):
        """
        Set cost information for a source.
        
        Args:
            source_id: Source ID
            monthly_cost: Fixed monthly cost
            cost_per_lead: Variable cost per lead
        """
        if source_id in self._sources:
            if monthly_cost is not None:
                self._sources[source_id].monthly_cost = monthly_cost
            if cost_per_lead is not None:
                self._sources[source_id].cost_per_lead = cost_per_lead
            
            if self.db:
                self._update_source(self._sources[source_id])
    
    # =========================================================================
    # LEAD SCORING
    # =========================================================================
    
    def calculate_lead_score(
        self,
        lead_id: int,
        base_score: float = 50.0
    ) -> float:
        """
        Calculate lead score with source quality adjustment.
        
        Args:
            lead_id: Lead ID
            base_score: Base score from lead qualification
            
        Returns:
            Adjusted lead score (0-100)
        """
        score = base_score
        
        # Get source
        tag = self.get_lead_source(lead_id)
        
        if tag:
            # Apply source quality multiplier
            quality_scores = self.config["scoring"]["source_quality"]
            multiplier = quality_scores.get(tag.source_id, 1.0)
            score *= multiplier
        
        # Cap at 100
        return min(score, 100.0)
    
    # =========================================================================
    # ANALYTICS
    # =========================================================================
    
    def get_lead_funnel(
        self,
        source: str = None,
        start_date: date = None,
        end_date: date = None
    ) -> Dict[str, int]:
        """
        Get lead funnel by status.
        
        Returns:
            Dict with count at each funnel stage
        """
        funnel = {
            "new": 0,
            "contacted": 0,
            "qualified": 0,
            "proposal_sent": 0,
            "converted": 0,
            "lost": 0,
        }
        
        if self.db:
            funnel = self._get_funnel_stats(source, start_date, end_date)
        
        return funnel
    
    def get_trending_sources(
        self,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get source trends (comparing recent period to previous).
        
        Args:
            period_days: Number of days for comparison
            
        Returns:
            Trend data by source
        """
        end_date = date.today()
        mid_date = end_date - timedelta(days=period_days)
        start_date = mid_date - timedelta(days=period_days)
        
        trends = {
            "period_days": period_days,
            "sources": [],
        }
        
        if self.db:
            # Get stats for both periods
            previous_stats = self._get_source_stats(start_date, mid_date)
            current_stats = self._get_source_stats(mid_date, end_date)
            
            for source_id in self._sources:
                prev = previous_stats.get(source_id, {"leads": 0, "conversions": 0})
                curr = current_stats.get(source_id, {"leads": 0, "conversions": 0})
                
                # Calculate change
                lead_change = curr["leads"] - prev["leads"]
                lead_change_pct = (
                    (lead_change / prev["leads"]) * 100 
                    if prev["leads"] > 0 else 0
                )
                
                trends["sources"].append({
                    "source_id": source_id,
                    "source_name": self._sources[source_id].name,
                    "previous_leads": prev["leads"],
                    "current_leads": curr["leads"],
                    "change": lead_change,
                    "change_percentage": lead_change_pct,
                    "trend": "up" if lead_change > 0 else ("down" if lead_change < 0 else "flat"),
                })
        
        # Sort by change
        trends["sources"].sort(key=lambda x: x["change_percentage"], reverse=True)
        
        return trends
    
    # =========================================================================
    # DATABASE STUBS
    # =========================================================================
    
    def _save_tag(self, tag: LeadSourceTag) -> int:
        """Save lead source tag."""
        return 0
    
    def _load_lead_tag(self, lead_id: int) -> Optional[LeadSourceTag]:
        """Load lead source tag."""
        return None
    
    def _update_tag(self, tag: LeadSourceTag):
        """Update lead source tag."""
        pass
    
    def _save_conversion(self, conversion: Dict):
        """Save conversion record."""
        pass
    
    def _get_lead_id_for_client(self, client_id: int) -> Optional[int]:
        """Get original lead ID for client."""
        return None
    
    def _add_source_revenue(self, source_id: str, revenue: float):
        """Add revenue to source tracking."""
        pass
    
    def _add_campaign_revenue(self, campaign: str, revenue: float):
        """Add revenue to campaign tracking."""
        pass
    
    def _count_leads(self, **filters) -> int:
        """Count leads with filters."""
        return 0
    
    def _count_conversions(self, **filters) -> int:
        """Count conversions with filters."""
        return 0
    
    def _save_campaign(self, campaign: Campaign) -> int:
        """Save campaign."""
        return 0
    
    def _add_campaign_spend(self, campaign: str, spend: float):
        """Add spend to campaign."""
        pass
    
    def _update_campaign_conversion(self, campaign: str, revenue: float):
        """Update campaign with conversion."""
        pass
    
    def _load_campaign_with_stats(self, name: str) -> Optional[Campaign]:
        """Load campaign with stats."""
        return None
    
    def _load_active_campaigns(self) -> List[Campaign]:
        """Load active campaigns."""
        return []
    
    def _get_source_stats(self, start: date, end: date) -> Dict[str, Dict]:
        """Get stats by source for date range."""
        return {}
    
    def _get_source_stats_single(self, source_id: str) -> Optional[Dict]:
        """Get stats for single source."""
        return None
    
    def _get_campaign_stats(self, start: date, end: date) -> List[Dict]:
        """Get campaign stats for date range."""
        return []
    
    def _get_funnel_stats(self, source: str, start: date, end: date) -> Dict[str, int]:
        """Get funnel statistics."""
        return {}
    
    def _save_source(self, source: LeadSource):
        """Save custom source."""
        pass
    
    def _update_source(self, source: LeadSource):
        """Update source."""
        pass
