"""
AI Service - Lead scoring, message categorization, risk assessment
Uses OpenAI API for AI capabilities
"""

from typing import Dict, Any, Optional
import structlog
from openai import AsyncOpenAI

from app.core.config import settings
from app.schemas.lead import LeadScore
from app.schemas.client import ClientRisk
from app.schemas.message import MessageCategorize
from app.models.lead import Lead
from app.models.client import Client
from app.models.message import Message, MessageCategory

logger = structlog.get_logger(__name__)


class AIService:
    """AI service for scoring, categorization, and analysis"""
    
    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def score_lead(self, lead: Lead) -> LeadScore:
        """
        Score a lead (0-100)
        
        Factors:
        - Has email/phone: +20 points each
        - Has company: +10 points
        - Source quality (referral > website > other)
        - Custom fields (industry-specific)
        """
        score = 0.0
        factors = {}
        
        # Contact info
        if lead.email:
            score += 20
            factors["has_email"] = 20
        
        if lead.phone:
            score += 20
            factors["has_phone"] = 20
        
        # Company
        if lead.company:
            score += 10
            factors["has_company"] = 10
        
        # Source quality
        source_scores = {
            "referral": 30,
            "website": 20,
            "social": 15,
            "email": 15,
            "phone": 10,
            "other": 5
        }
        source_score = source_scores.get(lead.source.value, 5)
        score += source_score
        factors["source_quality"] = source_score
        
        # Notes presence (shows engagement)
        if lead.notes and len(lead.notes) > 20:
            score += 10
            factors["has_notes"] = 10
        
        # Clamp to 0-100
        score = max(0, min(100, score))
        
        # Recommendation
        if score >= 70:
            recommendation = "High priority - contact immediately"
        elif score >= 50:
            recommendation = "Medium priority - follow up within 24 hours"
        else:
            recommendation = "Low priority - qualify further"
        
        logger.info("Lead scored", lead_id=lead.id, score=score)
        
        return LeadScore(
            lead_id=lead.id,
            score=score,
            factors=factors,
            recommendation=recommendation
        )
    
    async def assess_client_risk(self, client: Client) -> ClientRisk:
        """
        Assess client churn risk (0-1)
        
        Factors:
        - Time since last interaction
        - Lifetime value (higher = lower risk)
        - Status (inactive/churned = high risk)
        - Missed followups
        """
        risk_score = 0.0
        factors = {}
        
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        
        # Status risk
        if client.status.value == "churned":
            risk_score = 1.0
            factors["status"] = "churned"
        elif client.status.value == "inactive":
            risk_score = 0.7
            factors["status"] = "inactive"
        else:
            # Calculate based on other factors
            
            # Time since last interaction
            if client.last_interaction:
                days_since_interaction = (now - client.last_interaction).days
                if days_since_interaction > 90:
                    risk_score += 0.4
                    factors["inactive_days"] = days_since_interaction
                elif days_since_interaction > 60:
                    risk_score += 0.2
                    factors["inactive_days"] = days_since_interaction
            else:
                risk_score += 0.3
                factors["no_interaction"] = True
            
            # Missed followups
            if client.next_followup and client.next_followup < now:
                days_overdue = (now - client.next_followup).days
                if days_overdue > 30:
                    risk_score += 0.3
                    factors["followup_overdue_days"] = days_overdue
                elif days_overdue > 7:
                    risk_score += 0.1
                    factors["followup_overdue_days"] = days_overdue
            
            # Lifetime value (inverse relationship with risk)
            if client.lifetime_value < 1000:
                risk_score += 0.2
                factors["low_ltv"] = client.lifetime_value
        
        # Clamp to 0-1
        risk_score = max(0, min(1, risk_score))
        
        # Risk level
        if risk_score >= 0.7:
            risk_level = "high"
        elif risk_score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Recommendations
        recommendations = []
        if risk_score >= 0.7:
            recommendations.append("Immediate outreach required")
            recommendations.append("Schedule retention call")
        elif risk_score >= 0.4:
            recommendations.append("Follow up within this week")
            recommendations.append("Send check-in email")
        else:
            recommendations.append("Continue normal cadence")
        
        logger.info("Client risk assessed", client_id=client.id, risk_score=risk_score)
        
        return ClientRisk(
            client_id=client.id,
            risk_score=risk_score,
            risk_level=risk_level,
            factors=factors,
            recommendations=recommendations
        )
    
    async def categorize_message(self, message: Message) -> MessageCategorize:
        """
        Categorize a message using AI (if available) or rules
        
        Categories:
        - PROSPECTIVE: New lead inquiries
        - CLIENT: Active client communication
        - OFFICE: Internal/admin
        - SPAM: Spam/marketing
        - OTHER: Unknown
        """
        
        # Simple rule-based categorization (can be enhanced with AI)
        category = MessageCategory.OTHER
        confidence = 0.6
        sentiment_score = 0
        priority_score = 3
        summary = None
        
        subject = (message.subject or "").lower()
        body = (message.body or "").lower()
        content = f"{subject} {body}"
        
        # Keywords for categorization
        if any(word in content for word in ["new client", "inquiry", "interested", "quote", "services"]):
            category = MessageCategory.PROSPECTIVE
            confidence = 0.8
            priority_score = 5
        elif any(word in content for word in ["question", "urgent", "need help", "issue"]):
            category = MessageCategory.CLIENT
            confidence = 0.7
            priority_score = 4
        elif any(word in content for word in ["invoice", "payment", "billing", "admin"]):
            category = MessageCategory.OFFICE
            confidence = 0.7
            priority_score = 2
        elif any(word in content for word in ["unsubscribe", "marketing", "newsletter", "promotion"]):
            category = MessageCategory.SPAM
            confidence = 0.9
            priority_score = 1
        
        # Sentiment analysis (simple)
        positive_words = ["thank", "great", "excellent", "appreciate", "happy"]
        negative_words = ["complaint", "unhappy", "disappointed", "issue", "problem"]
        
        positive_count = sum(1 for word in positive_words if word in content)
        negative_count = sum(1 for word in negative_words if word in content)
        
        if positive_count > negative_count:
            sentiment_score = 1
        elif negative_count > positive_count:
            sentiment_score = -1
        
        # Generate summary (first 100 chars of body)
        if message.body:
            summary = message.body[:100] + "..." if len(message.body) > 100 else message.body
        
        logger.info("Message categorized", 
                   message_id=message.id, 
                   category=category.value, 
                   confidence=confidence)
        
        return MessageCategorize(
            message_id=message.id,
            category=category,
            confidence=confidence,
            sentiment_score=sentiment_score,
            priority_score=priority_score,
            summary=summary
        )
    
    async def generate_daily_digest(self, messages: list) -> str:
        """Generate daily digest summary (placeholder)"""
        
        if not messages:
            return "No new messages today."
        
        digest = f"Daily Digest - {len(messages)} new messages\n\n"
        
        # Group by category
        by_category = {}
        for msg in messages:
            category = msg.category.value
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(msg)
        
        # Summarize each category
        for category, msgs in by_category.items():
            digest += f"\n{category.upper()}: {len(msgs)} messages\n"
            for msg in msgs[:3]:  # Top 3
                digest += f"  - {msg.subject or '(no subject)'} from {msg.from_address}\n"
        
        return digest
