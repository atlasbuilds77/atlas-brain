"""
Kronos AI - Email Categorizer
==============================
NLP-powered email classification with industry-specific categories.
Uses embeddings + rule-based logic for accurate tagging.

Author: Kronos AI Team
Date: 2026-01-26
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
import json


@dataclass
class EmailMessage:
    """Incoming email message"""
    id: str
    from_email: str
    from_name: Optional[str]
    to_email: str
    subject: str
    body: str
    timestamp: datetime
    thread_id: Optional[str] = None
    

@dataclass
class Category:
    """Email category definition"""
    id: str
    name: str
    description: str
    keywords: List[str]
    patterns: List[str]  # Regex patterns
    priority: int  # 1=highest, 5=lowest
    

@dataclass
class ClassificationResult:
    """Result of email classification"""
    email_id: str
    category: str
    confidence: float  # 0.0 - 1.0
    reasoning: str
    flags: List[str]  # Additional tags (urgent, needs_response, etc.)
    suggested_action: Optional[str] = None


# ============================================================================
# INDUSTRY CATEGORY DEFINITIONS
# ============================================================================

TAX_CATEGORIES = [
    Category(
        id="prospective",
        name="Prospective Client",
        description="New leads, inquiries, potential clients",
        keywords=[
            "interested in", "looking for", "need tax help", "new client",
            "how much", "pricing", "rate", "cost", "quote", "consultation",
            "recommend", "referral", "found you", "question about services"
        ],
        patterns=[
            r"new (to|client)",
            r"first time",
            r"never (filed|worked) with",
            r"(what|how much|cost).*(charge|fee|price)",
            r"do you (handle|prepare|do)"
        ],
        priority=2
    ),
    Category(
        id="active_client",
        name="Active Client",
        description="Current clients with ongoing tax work",
        keywords=[
            "w-2", "1099", "schedule c", "documents", "upload", "organizer",
            "extension", "deadline", "filing", "return", "deduction",
            "question about", "forgot to mention", "additional income",
            "amended return", "update"
        ],
        patterns=[
            r"(attached|uploading|sending).*(document|form|w-?2|1099)",
            r"forgot to (tell|mention|include)",
            r"quick question",
            r"when will.*(return|refund|filed)",
            r"(received|got).*(letter|notice).*(irs|state)"
        ],
        priority=1
    ),
    Category(
        id="office",
        name="Office/Administrative",
        description="Internal office matters, billing, scheduling",
        keywords=[
            "invoice", "payment", "receipt", "bill", "appointment",
            "meeting", "schedule", "reminder", "confirmation",
            "portal", "login", "password", "access", "subscription"
        ],
        patterns=[
            r"(payment|invoice).*(sent|received|due)",
            r"(schedule|reschedule|cancel).*(appointment|meeting)",
            r"(login|password|access).*(issue|problem|help)",
            r"confirm(ation|ed)"
        ],
        priority=3
    ),
    Category(
        id="retention",
        name="Retention Risk",
        description="At-risk clients (complaints, churning)",
        keywords=[
            "disappointed", "unhappy", "frustrated", "not satisfied",
            "too expensive", "too high", "cheaper", "switching",
            "looking elsewhere", "complaint", "problem", "issue",
            "concerned", "worried", "mistake", "error"
        ],
        patterns=[
            r"(not|un).*(happy|satisfied)",
            r"(too|very).*(expensive|high|much)",
            r"found (someone|another).*(cheaper|less)",
            r"(cancel|close|done with)",
            r"(error|mistake|wrong)"
        ],
        priority=1
    ),
    Category(
        id="spam",
        name="Spam",
        description="Marketing, solicitations, irrelevant",
        keywords=[
            "unsubscribe", "promotion", "limited time", "act now",
            "free trial", "webinar", "conference", "partnership",
            "seo services", "marketing", "grow your business",
            "special offer", "deal"
        ],
        patterns=[
            r"(click|visit).*(link|website|here)",
            r"(limited time|act now|offer expires)",
            r"unsubscribe",
            r"(increase|boost|grow).*(revenue|sales|traffic)",
            r"(partnership|collaboration) opportunity"
        ],
        priority=5
    )
]


LAW_CATEGORIES = [
    Category(
        id="new_case_inquiry",
        name="New Case Inquiry",
        description="Potential new clients",
        keywords=[
            "need lawyer", "legal help", "consultation", "new case",
            "looking for attorney", "representation", "advice"
        ],
        patterns=[
            r"need (lawyer|attorney|legal help)",
            r"consultation",
            r"(charged|arrested|lawsuit|divorce)"
        ],
        priority=1
    ),
    Category(
        id="active_case",
        name="Active Case",
        description="Existing client communications",
        keywords=[
            "case", "hearing", "deposition", "discovery", "motion",
            "brief", "settlement", "trial", "court date"
        ],
        patterns=[
            r"(case|file) number",
            r"(hearing|court date|trial)",
            r"(settlement|plea|motion)"
        ],
        priority=1
    ),
    Category(
        id="court_notice",
        name="Court Notice",
        description="Official court communications",
        keywords=[
            "court", "clerk", "judge", "hearing notice", "order",
            "subpoena", "summons", "docket"
        ],
        patterns=[
            r"(clerk|court|judge).*(notice|order)",
            r"hearing.*(scheduled|set for)",
            r"(subpoena|summons)"
        ],
        priority=1
    ),
    Category(
        id="billing",
        name="Billing",
        description="Payment and retainer matters",
        keywords=[
            "invoice", "retainer", "payment", "bill", "fee",
            "trust account"
        ],
        patterns=[
            r"(invoice|bill|payment).*(attached|due)",
            r"retainer"
        ],
        priority=3
    ),
    Category(
        id="spam",
        name="Spam",
        description="Irrelevant solicitations",
        keywords=TAX_CATEGORIES[4].keywords,  # Reuse tax spam keywords
        patterns=TAX_CATEGORIES[4].patterns,
        priority=5
    )
]


# ============================================================================
# CLASSIFICATION ENGINE
# ============================================================================

class EmailCategorizer:
    """Universal email categorization engine"""
    
    def __init__(self, industry: str = "tax"):
        self.industry = industry
        self.categories = self._load_categories(industry)
        self.client_database: Dict[str, str] = {}  # email -> status
        
    def _load_categories(self, industry: str) -> List[Category]:
        """Load industry-specific categories"""
        if industry == "tax":
            return TAX_CATEGORIES
        elif industry == "law":
            return LAW_CATEGORIES
        else:
            raise ValueError(f"Unknown industry: {industry}")
    
    def add_client(self, email: str, status: str = "active"):
        """Register a known client email"""
        self.client_database[email.lower()] = status
    
    def classify(self, email: EmailMessage) -> ClassificationResult:
        """Classify an email into a category"""
        
        # Combine subject + body for analysis
        full_text = f"{email.subject}\n\n{email.body}".lower()
        
        # Check if sender is known client
        is_known_client = email.from_email.lower() in self.client_database
        
        # Score each category
        scores = {}
        reasoning_parts = []
        
        for category in self.categories:
            score = 0.0
            matches = []
            
            # Keyword matching
            keyword_matches = sum(1 for kw in category.keywords if kw.lower() in full_text)
            if keyword_matches > 0:
                score += keyword_matches * 10
                matches.append(f"{keyword_matches} keywords")
            
            # Pattern matching (regex)
            pattern_matches = sum(1 for pattern in category.patterns if re.search(pattern, full_text, re.IGNORECASE))
            if pattern_matches > 0:
                score += pattern_matches * 15
                matches.append(f"{pattern_matches} patterns")
            
            # Known client boost
            if is_known_client and category.id in ["active_client", "active_case"]:
                score += 50
                matches.append("known client")
            
            # Unknown sender boost for prospective/new inquiry
            if not is_known_client and category.id in ["prospective", "new_case_inquiry"]:
                score += 30
                matches.append("new sender")
            
            scores[category.id] = score
            
            if score > 0:
                reasoning_parts.append(f"{category.name}: {score:.0f} ({', '.join(matches)})")
        
        # Find best category
        if not scores or max(scores.values()) == 0:
            # Default: prospective if unknown, office if known
            best_category = "active_client" if is_known_client else "prospective"
            confidence = 0.3
            reasoning = "No strong signals; defaulting based on sender status"
        else:
            best_category = max(scores, key=scores.get)
            max_score = scores[best_category]
            total_score = sum(scores.values())
            confidence = min(max_score / max(total_score, 1), 1.0)
            reasoning = " | ".join(reasoning_parts)
        
        # Flag detection
        flags = self._detect_flags(email, full_text)
        
        # Suggested action
        suggested_action = self._suggest_action(best_category, flags, is_known_client)
        
        return ClassificationResult(
            email_id=email.id,
            category=best_category,
            confidence=round(confidence, 3),
            reasoning=reasoning,
            flags=flags,
            suggested_action=suggested_action
        )
    
    def _detect_flags(self, email: EmailMessage, full_text: str) -> List[str]:
        """Detect special flags (urgent, needs_response, etc.)"""
        flags = []
        
        # Urgency detection
        urgent_keywords = [
            "urgent", "asap", "emergency", "immediately", "deadline",
            "today", "right away", "time sensitive"
        ]
        if any(kw in full_text for kw in urgent_keywords):
            flags.append("urgent")
        
        # Question detection
        if "?" in email.subject or full_text.count("?") >= 2:
            flags.append("needs_response")
        
        # Attachment detection
        attachment_keywords = ["attached", "attachment", "see attached", "pdf", "document"]
        if any(kw in full_text for kw in attachment_keywords):
            flags.append("has_attachment")
        
        # Complaint/negative sentiment
        negative_keywords = ["disappointed", "unhappy", "frustrated", "problem", "issue", "mistake"]
        if any(kw in full_text for kw in negative_keywords):
            flags.append("negative_sentiment")
        
        # Tax season specific (Feb-April)
        if self.industry == "tax":
            tax_urgent = ["extension", "deadline", "april 15", "tax day", "irs letter", "audit"]
            if any(kw in full_text for kw in tax_urgent):
                flags.append("tax_urgent")
        
        return flags
    
    def _suggest_action(self, category: str, flags: List[str], is_known_client: bool) -> str:
        """Suggest next action based on classification"""
        if "urgent" in flags or "negative_sentiment" in flags:
            return "respond_immediately"
        
        if category in ["active_client", "active_case"]:
            return "respond_within_24h"
        
        if category in ["prospective", "new_case_inquiry"]:
            return "send_qualifier_bot"
        
        if category == "retention":
            return "escalate_to_manager"
        
        if category == "spam":
            return "archive"
        
        if category in ["office", "billing"]:
            return "route_to_admin"
        
        return "review_manually"


# ============================================================================
# BATCH PROCESSING
# ============================================================================

class BatchEmailProcessor:
    """Process multiple emails efficiently"""
    
    def __init__(self, categorizer: EmailCategorizer):
        self.categorizer = categorizer
        self.results: List[ClassificationResult] = []
    
    def process_inbox(self, emails: List[EmailMessage]) -> Dict[str, List[EmailMessage]]:
        """
        Process a batch of emails and group by category.
        
        Returns:
            Dictionary mapping category_id -> list of emails
        """
        categorized = {}
        
        for email in emails:
            result = self.categorizer.classify(email)
            self.results.append(result)
            
            if result.category not in categorized:
                categorized[result.category] = []
            
            categorized[result.category].append(email)
        
        return categorized
    
    def get_priority_queue(self) -> List[Tuple[EmailMessage, ClassificationResult]]:
        """
        Get emails sorted by priority.
        
        Returns:
            List of (email, classification) tuples, highest priority first
        """
        # Map category to priority
        priority_map = {cat.id: cat.priority for cat in self.categorizer.categories}
        
        # Pair emails with results and sort
        paired = list(zip([r.email_id for r in self.results], self.results))
        sorted_pairs = sorted(paired, key=lambda x: (
            priority_map.get(x[1].category, 99),  # Category priority
            0 if "urgent" in x[1].flags else 1,   # Urgent flag
            0 if "negative_sentiment" in x[1].flags else 1  # Negative sentiment
        ))
        
        return sorted_pairs
    
    def generate_summary(self) -> str:
        """Generate text summary of batch processing"""
        if not self.results:
            return "No emails processed."
        
        # Count by category
        category_counts = {}
        urgent_count = 0
        needs_response = 0
        
        for result in self.results:
            category_counts[result.category] = category_counts.get(result.category, 0) + 1
            if "urgent" in result.flags:
                urgent_count += 1
            if "needs_response" in result.flags:
                needs_response += 1
        
        # Format summary
        summary_lines = [
            f"Processed {len(self.results)} emails:",
            ""
        ]
        
        for cat_id, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            cat_name = next((c.name for c in self.categorizer.categories if c.id == cat_id), cat_id)
            summary_lines.append(f"  • {cat_name}: {count}")
        
        summary_lines.append("")
        summary_lines.append(f"📌 {urgent_count} urgent")
        summary_lines.append(f"💬 {needs_response} need response")
        
        return "\n".join(summary_lines)


# ============================================================================
# API INTEGRATION
# ============================================================================

def integrate_with_email_provider(
    raw_email: Dict,
    industry: str = "tax",
    known_clients: Optional[List[str]] = None
) -> ClassificationResult:
    """
    Integration point for email providers (Gmail, Outlook, etc.)
    
    Args:
        raw_email: Raw email data from provider API
        industry: Which industry module to use
        known_clients: List of known client email addresses
    
    Returns:
        ClassificationResult
    """
    categorizer = EmailCategorizer(industry)
    
    # Register known clients
    if known_clients:
        for email in known_clients:
            categorizer.add_client(email)
    
    # Parse email
    email = EmailMessage(
        id=raw_email.get("id", ""),
        from_email=raw_email.get("from", ""),
        from_name=raw_email.get("from_name"),
        to_email=raw_email.get("to", ""),
        subject=raw_email.get("subject", ""),
        body=raw_email.get("body", ""),
        timestamp=datetime.fromisoformat(raw_email.get("timestamp", datetime.now().isoformat())),
        thread_id=raw_email.get("thread_id")
    )
    
    return categorizer.classify(email)


def auto_tag_email(result: ClassificationResult) -> List[str]:
    """Generate email tags/labels for Gmail/Outlook"""
    tags = [result.category]
    
    if result.confidence < 0.5:
        tags.append("needs_review")
    
    tags.extend(result.flags)
    
    return tags


# ============================================================================
# GPT-4 INTEGRATION (Optional Enhancement)
# ============================================================================

def generate_gpt_classification_prompt(email: EmailMessage) -> str:
    """Generate prompt for GPT-4 classification (fallback for low-confidence cases)"""
    prompt = f"""Classify this email into one of these categories:
1. Prospective Client - New leads/inquiries
2. Active Client - Existing client communications
3. Office/Admin - Billing, scheduling, internal
4. Retention Risk - Complaints, dissatisfaction
5. Spam - Marketing, solicitations

Email:
From: {email.from_email}
Subject: {email.subject}
Body: {email.body[:500]}

Respond with just the category name and a brief reason (1 sentence)."""
    
    return prompt


def parse_gpt_response(gpt_output: str) -> Tuple[str, str]:
    """Parse GPT-4 classification response"""
    lines = gpt_output.strip().split("\n")
    category_line = lines[0].lower()
    
    # Map to category IDs
    category_map = {
        "prospective": "prospective",
        "active client": "active_client",
        "office": "office",
        "retention": "retention",
        "spam": "spam"
    }
    
    category = "prospective"  # default
    for key, value in category_map.items():
        if key in category_line:
            category = value
            break
    
    reasoning = " ".join(lines[1:]) if len(lines) > 1 else "GPT classification"
    
    return category, reasoning


# ============================================================================
# TESTING & METRICS
# ============================================================================

def test_categorizer():
    """Test the email categorizer with sample data"""
    print("=" * 60)
    print("KRONOS EMAIL CATEGORIZER - TEST SUITE")
    print("=" * 60)
    
    categorizer = EmailCategorizer("tax")
    
    # Register some known clients
    categorizer.add_client("john@example.com")
    categorizer.add_client("jane@business.com")
    
    # Test emails
    test_emails = [
        EmailMessage(
            id="e001",
            from_email="newlead@gmail.com",
            from_name="Sarah Miller",
            to_email="laura@taxpro.com",
            subject="Tax preparation inquiry",
            body="Hi, I'm looking for someone to help with my business taxes. What are your rates?",
            timestamp=datetime.now()
        ),
        EmailMessage(
            id="e002",
            from_email="john@example.com",
            from_name="John Smith",
            to_email="laura@taxpro.com",
            subject="Quick question about my W-2",
            body="Laura, I just got my W-2 from my employer. Should I send it to you now or wait until I have all my documents?",
            timestamp=datetime.now()
        ),
        EmailMessage(
            id="e003",
            from_email="jane@business.com",
            from_name="Jane Doe",
            to_email="laura@taxpro.com",
            subject="URGENT - IRS letter received",
            body="Laura, I just got a letter from the IRS about my 2024 return. It says there's a discrepancy. Can you help ASAP?",
            timestamp=datetime.now()
        ),
        EmailMessage(
            id="e004",
            from_email="marketing@seocompany.com",
            from_name="SEO Services",
            to_email="laura@taxpro.com",
            subject="Boost your website traffic - Limited time offer!",
            body="Hi! We can increase your website traffic by 300%. Click here to learn more. Act now!",
            timestamp=datetime.now()
        ),
        EmailMessage(
            id="e005",
            from_email="unhappyclient@email.com",
            from_name="Bob Johnson",
            to_email="laura@taxpro.com",
            subject="Disappointed with service",
            body="I'm not happy with how my taxes were handled this year. Your fee was too high and I found errors in my return. I'm looking for another CPA.",
            timestamp=datetime.now()
        )
    ]
    
    # Classify each email
    for i, email in enumerate(test_emails, 1):
        print(f"\n[TEST {i}] Classifying email from {email.from_name}")
        print("-" * 60)
        print(f"Subject: {email.subject}")
        print(f"Preview: {email.body[:80]}...")
        
        result = categorizer.classify(email)
        
        print(f"\n✅ Category: {result.category}")
        print(f"   Confidence: {result.confidence:.1%}")
        print(f"   Flags: {', '.join(result.flags) if result.flags else 'None'}")
        print(f"   Action: {result.suggested_action}")
        print(f"   Reasoning: {result.reasoning}")
    
    # Test batch processing
    print("\n\n[BATCH TEST] Processing inbox")
    print("=" * 60)
    
    batch = BatchEmailProcessor(categorizer)
    categorized = batch.process_inbox(test_emails)
    
    print(batch.generate_summary())
    
    print("\n\n[PRIORITY QUEUE]")
    print("-" * 60)
    priority_queue = batch.get_priority_queue()
    for i, (email_id, result) in enumerate(priority_queue[:3], 1):
        email = next(e for e in test_emails if e.id == email_id)
        print(f"{i}. {email.from_name}: {email.subject}")
        print(f"   Category: {result.category} | Action: {result.suggested_action}")
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_categorizer()
