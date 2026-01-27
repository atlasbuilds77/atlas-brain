"""
Kronos AI - Daily Digest Generator
===================================
Aggregates messages across channels and generates prioritized morning summaries.
Industry-aware priority sorting.

Author: Kronos AI Team
Date: 2026-01-26
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json


class MessageChannel(Enum):
    """Communication channels"""
    EMAIL = "email"
    SMS = "sms"
    WEB = "web"
    PHONE = "phone"
    PORTAL = "portal"


class MessageType(Enum):
    """Message types"""
    INQUIRY = "inquiry"
    RESPONSE = "response"
    QUESTION = "question"
    UPDATE = "update"
    DOCUMENT = "document"
    COMPLAINT = "complaint"
    REMINDER = "reminder"


@dataclass
class Message:
    """Universal message object across all channels"""
    id: str
    channel: MessageChannel
    from_contact: str
    from_name: Optional[str]
    to_contact: str
    subject: Optional[str]
    body: str
    timestamp: datetime
    category: Optional[str] = None  # From email categorizer
    message_type: Optional[MessageType] = None
    flags: List[str] = field(default_factory=list)
    is_read: bool = False
    thread_id: Optional[str] = None
    

@dataclass
class DigestSection:
    """A section in the daily digest"""
    title: str
    priority: int
    messages: List[Message]
    summary: Optional[str] = None
    action_items: List[str] = field(default_factory=list)


@dataclass
class DailyDigest:
    """Complete daily digest"""
    date: datetime
    industry: str
    sections: List[DigestSection]
    total_messages: int
    urgent_count: int
    needs_response_count: int
    generated_at: datetime
    

# ============================================================================
# INDUSTRY-SPECIFIC PRIORITY RULES
# ============================================================================

class PriorityRules:
    """Base priority rules (override per industry)"""
    
    @staticmethod
    def calculate_priority(message: Message, context: Dict) -> int:
        """
        Calculate message priority (1=highest, 10=lowest).
        Override this in industry-specific subclasses.
        """
        priority = 5  # Default medium priority
        
        # Flag-based adjustments
        if "urgent" in message.flags:
            priority -= 3
        if "negative_sentiment" in message.flags:
            priority -= 2
        if "needs_response" in message.flags:
            priority -= 1
        
        # Category-based adjustments
        if message.category == "spam":
            priority = 10
        elif message.category in ["active_client", "active_case"]:
            priority -= 1
        
        # Time sensitivity
        age_hours = (datetime.now() - message.timestamp).total_seconds() / 3600
        if age_hours > 48:
            priority -= 1  # Older messages get slight boost
        
        return max(1, min(priority, 10))


class TaxPriorityRules(PriorityRules):
    """Tax industry priority rules"""
    
    @staticmethod
    def calculate_priority(message: Message, context: Dict) -> int:
        """Tax-specific priority calculation"""
        priority = 5
        
        # During tax season (Feb-April), active clients are TOP priority
        is_tax_season = context.get("is_tax_season", False)
        
        if is_tax_season:
            # Tax season priorities
            if message.category == "active_client":
                priority = 1  # Highest priority
            elif "tax_urgent" in message.flags:  # IRS letters, deadlines
                priority = 1
            elif message.category == "prospective":
                priority = 4  # Lower during busy season
        else:
            # Off-season priorities
            if message.category == "active_client":
                priority = 2
            elif message.category == "prospective":
                priority = 2  # More attention to new leads
            elif message.category == "retention":
                priority = 1  # Prevent churn
        
        # Universal urgent flags
        if "urgent" in message.flags:
            priority = max(1, priority - 2)
        if "negative_sentiment" in message.flags:
            priority = max(1, priority - 2)
        
        # Document-related messages
        if "has_attachment" in message.flags and message.category == "active_client":
            priority = 2  # Documents need prompt review
        
        # Questions require responses
        if "needs_response" in message.flags:
            priority = max(2, priority - 1)
        
        # Spam goes to bottom
        if message.category == "spam":
            priority = 10
        
        return max(1, min(priority, 10))


class LawPriorityRules(PriorityRules):
    """Law industry priority rules"""
    
    @staticmethod
    def calculate_priority(message: Message, context: Dict) -> int:
        """Law-specific priority calculation"""
        priority = 5
        
        # Court deadlines are ALWAYS highest priority
        if message.category == "court_notice" or "court" in message.flags:
            priority = 1
        
        # Active cases
        elif message.category == "active_case":
            if "urgent" in message.flags:
                priority = 1
            else:
                priority = 2
        
        # New inquiries
        elif message.category == "new_case_inquiry":
            priority = 3  # Important but not blocking
        
        # Billing
        elif message.category == "billing":
            priority = 4
        
        # Complaints
        if "negative_sentiment" in message.flags:
            priority = max(1, priority - 2)
        
        # Spam
        if message.category == "spam":
            priority = 10
        
        return max(1, min(priority, 10))


# ============================================================================
# DIGEST GENERATOR
# ============================================================================

class DigestGenerator:
    """Generates daily digest from messages"""
    
    def __init__(self, industry: str = "tax"):
        self.industry = industry
        self.priority_rules = self._load_priority_rules(industry)
        
    def _load_priority_rules(self, industry: str) -> PriorityRules:
        """Load industry-specific priority rules"""
        if industry == "tax":
            return TaxPriorityRules()
        elif industry == "law":
            return LawPriorityRules()
        else:
            return PriorityRules()
    
    def generate(
        self,
        messages: List[Message],
        context: Optional[Dict] = None
    ) -> DailyDigest:
        """
        Generate a daily digest from messages.
        
        Args:
            messages: List of messages to include
            context: Additional context (e.g., is_tax_season, user preferences)
        
        Returns:
            DailyDigest object
        """
        if context is None:
            context = {}
        
        # Add default context
        context.setdefault("is_tax_season", self._is_tax_season())
        
        # Calculate priorities
        prioritized = []
        for msg in messages:
            priority = self.priority_rules.calculate_priority(msg, context)
            prioritized.append((priority, msg))
        
        # Sort by priority
        prioritized.sort(key=lambda x: (x[0], x[1].timestamp))
        
        # Group into sections
        sections = self._create_sections(prioritized, context)
        
        # Count flags
        urgent_count = sum(1 for msg in messages if "urgent" in msg.flags)
        needs_response = sum(1 for msg in messages if "needs_response" in msg.flags)
        
        return DailyDigest(
            date=datetime.now().date(),
            industry=self.industry,
            sections=sections,
            total_messages=len(messages),
            urgent_count=urgent_count,
            needs_response_count=needs_response,
            generated_at=datetime.now()
        )
    
    def _is_tax_season(self) -> bool:
        """Check if we're in tax season (Feb-April)"""
        month = datetime.now().month
        return month in [2, 3, 4]
    
    def _create_sections(
        self,
        prioritized: List[Tuple[int, Message]],
        context: Dict
    ) -> List[DigestSection]:
        """Group messages into digest sections"""
        sections = []
        
        # Section 1: Urgent/Action Required (Priority 1-2)
        urgent_messages = [msg for pri, msg in prioritized if pri <= 2]
        if urgent_messages:
            sections.append(DigestSection(
                title="🚨 Urgent - Action Required",
                priority=1,
                messages=urgent_messages,
                summary=f"{len(urgent_messages)} messages need immediate attention",
                action_items=[
                    f"Respond to {msg.from_name or msg.from_contact}: {msg.subject or 'Message'}"
                    for msg in urgent_messages[:5]
                ]
            ))
        
        # Section 2: Active Work (Priority 3-4)
        active_messages = [msg for pri, msg in prioritized if 3 <= pri <= 4]
        if active_messages:
            sections.append(DigestSection(
                title="💼 Active Work",
                priority=2,
                messages=active_messages,
                summary=f"{len(active_messages)} ongoing client matters"
            ))
        
        # Section 3: New Inquiries (Prospective)
        new_messages = [
            msg for pri, msg in prioritized
            if msg.category in ["prospective", "new_case_inquiry"] and pri >= 3
        ]
        if new_messages:
            sections.append(DigestSection(
                title="🆕 New Inquiries",
                priority=3,
                messages=new_messages,
                summary=f"{len(new_messages)} potential new clients"
            ))
        
        # Section 4: Administrative
        admin_messages = [
            msg for pri, msg in prioritized
            if msg.category in ["office", "billing"] and pri >= 4
        ]
        if admin_messages:
            sections.append(DigestSection(
                title="📋 Administrative",
                priority=4,
                messages=admin_messages,
                summary=f"{len(admin_messages)} office/billing items"
            ))
        
        # Section 5: Low Priority
        low_priority = [msg for pri, msg in prioritized if pri >= 7 and msg.category != "spam"]
        if low_priority:
            sections.append(DigestSection(
                title="📌 Low Priority",
                priority=5,
                messages=low_priority,
                summary=f"{len(low_priority)} items for later review"
            ))
        
        return sections
    
    def format_as_email(self, digest: DailyDigest) -> Tuple[str, str]:
        """
        Format digest as email (subject, body).
        
        Returns:
            (subject, html_body)
        """
        # Email subject
        date_str = digest.date.strftime("%B %d, %Y")
        subject = f"📬 Daily Digest - {date_str}"
        
        if digest.urgent_count > 0:
            subject = f"🚨 Daily Digest ({digest.urgent_count} urgent) - {date_str}"
        
        # Email body (HTML)
        html_parts = [
            f"<h1>Daily Digest - {date_str}</h1>",
            f"<p><strong>Total Messages:</strong> {digest.total_messages}</p>"
        ]
        
        if digest.urgent_count > 0:
            html_parts.append(f"<p style='color: red;'><strong>⚠️ {digest.urgent_count} URGENT messages</strong></p>")
        
        if digest.needs_response_count > 0:
            html_parts.append(f"<p><strong>💬 {digest.needs_response_count} need response</strong></p>")
        
        html_parts.append("<hr>")
        
        # Render each section
        for section in digest.sections:
            html_parts.append(f"<h2>{section.title}</h2>")
            html_parts.append(f"<p><em>{section.summary}</em></p>")
            
            if section.action_items:
                html_parts.append("<ul>")
                for item in section.action_items:
                    html_parts.append(f"<li>{item}</li>")
                html_parts.append("</ul>")
            
            # List messages
            html_parts.append("<ul>")
            for msg in section.messages[:10]:  # Limit to 10 per section
                sender = msg.from_name or msg.from_contact
                subject = msg.subject or "(no subject)"
                channel_icon = {
                    MessageChannel.EMAIL: "✉️",
                    MessageChannel.SMS: "💬",
                    MessageChannel.WEB: "🌐",
                    MessageChannel.PHONE: "📞",
                    MessageChannel.PORTAL: "🔐"
                }.get(msg.channel, "📨")
                
                flags_str = ""
                if msg.flags:
                    flags_str = f" <span style='color: orange;'>[{', '.join(msg.flags)}]</span>"
                
                html_parts.append(
                    f"<li>{channel_icon} <strong>{sender}:</strong> {subject}{flags_str}</li>"
                )
            
            if len(section.messages) > 10:
                html_parts.append(f"<li><em>... and {len(section.messages) - 10} more</em></li>")
            
            html_parts.append("</ul>")
        
        # Footer
        html_parts.append("<hr>")
        html_parts.append(f"<p><small>Generated at {digest.generated_at.strftime('%I:%M %p')}</small></p>")
        
        html_body = "\n".join(html_parts)
        
        return subject, html_body
    
    def format_as_text(self, digest: DailyDigest) -> str:
        """Format digest as plain text"""
        date_str = digest.date.strftime("%B %d, %Y")
        
        lines = [
            "=" * 60,
            f"DAILY DIGEST - {date_str}",
            "=" * 60,
            "",
            f"Total Messages: {digest.total_messages}",
        ]
        
        if digest.urgent_count > 0:
            lines.append(f"🚨 URGENT: {digest.urgent_count} messages")
        
        if digest.needs_response_count > 0:
            lines.append(f"💬 Need Response: {digest.needs_response_count}")
        
        lines.append("")
        lines.append("-" * 60)
        
        for section in digest.sections:
            lines.append("")
            lines.append(section.title)
            lines.append("-" * 60)
            lines.append(section.summary or "")
            
            if section.action_items:
                lines.append("\nACTIONS:")
                for item in section.action_items:
                    lines.append(f"  • {item}")
            
            lines.append("\nMESSAGES:")
            for msg in section.messages[:10]:
                sender = msg.from_name or msg.from_contact
                subject = msg.subject or "(no subject)"
                flags_str = f" [{', '.join(msg.flags)}]" if msg.flags else ""
                lines.append(f"  • {sender}: {subject}{flags_str}")
            
            if len(section.messages) > 10:
                lines.append(f"  ... and {len(section.messages) - 10} more")
        
        lines.append("")
        lines.append("=" * 60)
        lines.append(f"Generated: {digest.generated_at.strftime('%I:%M %p')}")
        lines.append("=" * 60)
        
        return "\n".join(lines)


# ============================================================================
# SCHEDULED DELIVERY
# ============================================================================

class DigestScheduler:
    """Schedule and deliver daily digests"""
    
    def __init__(self, generator: DigestGenerator):
        self.generator = generator
        self.delivery_time = "06:00"  # 6am default
        
    def set_delivery_time(self, time_str: str):
        """Set daily delivery time (HH:MM format)"""
        self.delivery_time = time_str
    
    def fetch_messages_since_last_digest(
        self,
        message_source,  # Database/API connection
        last_digest_time: datetime
    ) -> List[Message]:
        """
        Fetch all messages since last digest.
        This is a template - implement based on your data source.
        """
        # Example implementation:
        # return message_source.query(
        #     timestamp__gte=last_digest_time,
        #     is_archived=False
        # )
        raise NotImplementedError("Implement message fetching from your data source")
    
    def send_digest(self, digest: DailyDigest, recipient_email: str):
        """
        Send digest via email.
        This is a template - implement based on your email provider.
        """
        subject, html_body = self.generator.format_as_email(digest)
        
        # Example implementation:
        # email_service.send(
        #     to=recipient_email,
        #     subject=subject,
        #     html=html_body
        # )
        
        print(f"[SCHEDULER] Would send digest to {recipient_email}")
        print(f"Subject: {subject}")
        raise NotImplementedError("Implement email sending via your provider")


# ============================================================================
# API INTEGRATION
# ============================================================================

def generate_digest_for_user(
    user_id: str,
    industry: str,
    time_range: timedelta = timedelta(days=1),
    context: Optional[Dict] = None
) -> DailyDigest:
    """
    Generate digest for a specific user.
    
    Args:
        user_id: User identifier
        industry: Industry type
        time_range: How far back to look for messages
        context: Additional context
    
    Returns:
        DailyDigest object
    """
    generator = DigestGenerator(industry)
    
    # Fetch messages (implement based on your data source)
    # messages = fetch_user_messages(user_id, since=datetime.now() - time_range)
    
    # For testing:
    messages = []
    
    return generator.generate(messages, context)


# ============================================================================
# TESTING & METRICS
# ============================================================================

def test_digest_generator():
    """Test the digest generator with sample data"""
    print("=" * 60)
    print("KRONOS DAILY DIGEST - TEST SUITE")
    print("=" * 60)
    
    # Create sample messages
    now = datetime.now()
    
    test_messages = [
        Message(
            id="m001",
            channel=MessageChannel.EMAIL,
            from_contact="urgent@client.com",
            from_name="Jane Urgent",
            to_contact="laura@taxpro.com",
            subject="URGENT - IRS audit notice",
            body="Laura, I just received an audit notice from the IRS. I need help immediately!",
            timestamp=now - timedelta(hours=2),
            category="active_client",
            flags=["urgent", "needs_response", "tax_urgent"]
        ),
        Message(
            id="m002",
            channel=MessageChannel.EMAIL,
            from_contact="newlead@gmail.com",
            from_name="John Prospect",
            to_contact="laura@taxpro.com",
            subject="Tax preparation inquiry",
            body="Hi, I'm looking for someone to help with my business taxes.",
            timestamp=now - timedelta(hours=5),
            category="prospective",
            flags=["needs_response"]
        ),
        Message(
            id="m003",
            channel=MessageChannel.SMS,
            from_contact="+1234567890",
            from_name="Bob Client",
            to_contact="+1987654321",
            subject=None,
            body="Got my W-2, should I send it now?",
            timestamp=now - timedelta(hours=1),
            category="active_client",
            flags=["needs_response"]
        ),
        Message(
            id="m004",
            channel=MessageChannel.EMAIL,
            from_contact="unhappy@email.com",
            from_name="Sarah Unhappy",
            to_contact="laura@taxpro.com",
            subject="Disappointed with service",
            body="I'm not happy with the fees. Looking for another CPA.",
            timestamp=now - timedelta(hours=3),
            category="retention",
            flags=["negative_sentiment", "needs_response"]
        ),
        Message(
            id="m005",
            channel=MessageChannel.EMAIL,
            from_contact="admin@portal.com",
            from_name="Encyro",
            to_contact="laura@taxpro.com",
            subject="Client uploaded documents",
            body="Mike Johnson uploaded 3 documents to the secure portal.",
            timestamp=now - timedelta(hours=4),
            category="active_client",
            flags=["has_attachment"]
        ),
        Message(
            id="m006",
            channel=MessageChannel.EMAIL,
            from_contact="spam@marketing.com",
            from_name="SEO Company",
            to_contact="laura@taxpro.com",
            subject="Boost your website NOW!",
            body="Limited time offer! Click here to increase traffic by 500%!",
            timestamp=now - timedelta(hours=6),
            category="spam",
            flags=[]
        ),
        Message(
            id="m007",
            channel=MessageChannel.WEB,
            from_contact="contact_form",
            from_name="Alice New",
            to_contact="laura@taxpro.com",
            subject="Website inquiry",
            body="Submitted contact form asking about tax planning services.",
            timestamp=now - timedelta(hours=8),
            category="prospective",
            flags=[]
        )
    ]
    
    # Generate digest
    print("\n[TEST 1] Tax Industry - Tax Season")
    print("-" * 60)
    
    tax_generator = DigestGenerator("tax")
    tax_digest = tax_generator.generate(
        test_messages,
        context={"is_tax_season": True}
    )
    
    print(tax_generator.format_as_text(tax_digest))
    
    # Test 2: Off-season
    print("\n\n[TEST 2] Tax Industry - Off Season")
    print("-" * 60)
    
    offseason_digest = tax_generator.generate(
        test_messages,
        context={"is_tax_season": False}
    )
    
    print(tax_generator.format_as_text(offseason_digest))
    
    # Test 3: Law industry
    print("\n\n[TEST 3] Law Industry")
    print("-" * 60)
    
    law_messages = [
        Message(
            id="m101",
            channel=MessageChannel.EMAIL,
            from_contact="court@state.gov",
            from_name="Court Clerk",
            to_contact="attorney@law.com",
            subject="Hearing Notice - Case #12345",
            body="Your hearing is scheduled for next Monday at 9am.",
            timestamp=now - timedelta(hours=1),
            category="court_notice",
            flags=["court", "urgent"]
        ),
        Message(
            id="m102",
            channel=MessageChannel.EMAIL,
            from_contact="client@case.com",
            from_name="Client Smith",
            to_contact="attorney@law.com",
            subject="Question about my case",
            body="What's the status of my divorce case?",
            timestamp=now - timedelta(hours=2),
            category="active_case",
            flags=["needs_response"]
        )
    ]
    
    law_generator = DigestGenerator("law")
    law_digest = law_generator.generate(law_messages)
    
    print(law_generator.format_as_text(law_digest))
    
    # Test 4: Email formatting
    print("\n\n[TEST 4] Email HTML Format")
    print("-" * 60)
    
    subject, html = tax_generator.format_as_email(tax_digest)
    print(f"Subject: {subject}\n")
    print("HTML Preview (first 500 chars):")
    print(html[:500] + "...")
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_digest_generator()
