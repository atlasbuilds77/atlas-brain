"""
Tax Module Settings
Kronos Platform - Industry Module Configuration

All tax-specific settings configurable per instance.
"""

from datetime import date
from typing import List, Dict, Any

# =============================================================================
# TAX ORGANIZER SETTINGS
# =============================================================================

ORGANIZER_CONFIG = {
    # Days before deadline to send reminders (countdown)
    "reminder_days": [14, 7, 3, 1],
    
    # Default days from send date to deadline
    "default_deadline_days": 30,
    
    # Maximum reminders before escalation
    "max_reminders": 5,
    
    # Escalation: notify admin after max reminders
    "escalate_after_max": True,
    
    # Reminder email send time (24h format)
    "reminder_send_hour": 9,
    
    # Auto-resend if not opened after X days
    "auto_resend_days": 7,
}

# Available organizer templates
ORGANIZER_TEMPLATES = [
    "w2_employee",           # Standard W-2 employee
    "self_employed",         # 1099/freelance income
    "small_business",        # Business owner (Schedule C)
    "rental_property",       # Rental income (Schedule E)
    "investment_income",     # Stocks, dividends, capital gains
    "retirement",            # Retirement income, RMDs
    "first_time_filer",      # New tax filers
    "multi_state",           # Multiple state returns
    "expat",                 # US citizens abroad
    "high_net_worth",        # Complex returns, multiple schedules
]

# =============================================================================
# TAX FILING SETTINGS
# =============================================================================

FILING_CONFIG = {
    # Tax year (current filing season)
    "current_tax_year": date.today().year - 1,
    
    # Key dates (MM-DD format, year added dynamically)
    "season_start": "01-15",
    "w2_deadline": "01-31",
    "deadline_personal": "04-15",
    "deadline_extension": "10-15",
    "deadline_business": "03-15",
    "deadline_business_ext": "09-15",
    
    # Filing statuses
    "statuses": [
        "not_started",
        "organizer_sent",
        "documents_pending",
        "in_progress",
        "review",
        "ready_to_file",
        "filed",
        "extended",
        "amended",
    ],
    
    # Filing types
    "filing_types": [
        "personal",
        "business",
        "partnership",
        "s_corp",
        "c_corp",
        "trust",
        "estate",
        "nonprofit",
    ],
}

# =============================================================================
# CLIENT LIFECYCLE SETTINGS
# =============================================================================

LIFECYCLE_CONFIG = {
    # Onboarding stages
    "onboarding_stages": [
        "intake",              # Initial contact
        "qualification",       # Needs assessment
        "engagement_signed",   # Agreement signed
        "profile_complete",    # Tax profile filled
        "documents_uploaded",  # Initial docs received
        "active",              # Ready for service
    ],
    
    # Client statuses
    "client_statuses": [
        "prospect",
        "new_client",
        "active",
        "seasonal",           # Returns during tax season only
        "inactive",           # No activity > 1 year
        "churned",            # Confirmed left
        "winback",            # Re-engagement attempted
    ],
    
    # Retention risk thresholds
    "retention_risk": {
        "low": 0.3,
        "medium": 0.5,
        "high": 0.7,
        "critical": 0.9,
    },
    
    # Days of no contact before flagging
    "inactivity_warning_days": 365,
    "inactivity_critical_days": 545,  # 1.5 years
}

# =============================================================================
# WIN-BACK CAMPAIGN SETTINGS
# =============================================================================

WINBACK_CONFIG = {
    # Trigger win-back after X days of no return
    "trigger_days": 365,
    
    # Campaign touches
    "campaign_sequence": [
        {"day": 0, "type": "email", "template": "winback_initial"},
        {"day": 7, "type": "email", "template": "winback_value"},
        {"day": 21, "type": "email", "template": "winback_offer"},
        {"day": 45, "type": "email", "template": "winback_final"},
    ],
    
    # Stop campaign if client responds
    "stop_on_response": True,
    
    # Mark as churned after campaign completes with no response
    "mark_churned_after": True,
    
    # Exclude VIP clients from automated campaigns
    "exclude_vip": True,
}

# =============================================================================
# WISP COMPLIANCE SETTINGS
# =============================================================================

WISP_CONFIG = {
    # Data retention period (IRS requirement)
    "retention_years": 3,
    
    # Archive method after retention period
    "post_retention_action": "archive",  # archive, delete, anonymize
    
    # Encryption settings
    "encryption": {
        "algorithm": "AES-256-GCM",
        "key_rotation_days": 90,
        "encrypt_at_rest": True,
        "encrypt_in_transit": True,
    },
    
    # Access logging
    "access_logging": {
        "enabled": True,
        "log_views": True,
        "log_edits": True,
        "log_downloads": True,
        "log_exports": True,
        "retention_days": 1095,  # 3 years
    },
    
    # Session security
    "session": {
        "timeout_minutes": 30,
        "extend_on_activity": True,
        "max_session_hours": 12,
        "require_mfa": True,
    },
    
    # Incident response
    "incidents": {
        "auto_detect": True,
        "notify_admin_immediately": True,
        "severity_levels": ["low", "medium", "high", "critical"],
        "escalation_hours": {"high": 4, "critical": 1},
    },
    
    # Sensitive data patterns (for auto-detection)
    "sensitive_patterns": [
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
        r"\b\d{2}-\d{7}\b",         # EIN
        r"\b\d{9}\b",               # ITIN
    ],
}

# =============================================================================
# LEAD SOURCE TRACKING SETTINGS
# =============================================================================

LEAD_SOURCE_CONFIG = {
    # Available lead sources
    "sources": [
        {"id": "flyer", "name": "Flyer Mailing", "category": "offline"},
        {"id": "google", "name": "Google Search", "category": "online"},
        {"id": "website", "name": "Website Form", "category": "online"},
        {"id": "referral", "name": "Client Referral", "category": "referral"},
        {"id": "social", "name": "Social Media", "category": "online"},
        {"id": "yelp", "name": "Yelp", "category": "online"},
        {"id": "phone", "name": "Phone Call", "category": "offline"},
        {"id": "walkin", "name": "Walk-in", "category": "offline"},
        {"id": "returning", "name": "Returning Client", "category": "retention"},
        {"id": "unknown", "name": "Unknown", "category": "other"},
    ],
    
    # Default source if not specified
    "default_source": "unknown",
    
    # Track marketing campaigns
    "track_campaigns": True,
    
    # Cost tracking (for ROI)
    "track_costs": True,
    
    # Attribution window (days)
    "attribution_window_days": 30,
    
    # Lead scoring factors
    "scoring": {
        "source_quality": {
            "referral": 1.5,      # High quality
            "returning": 1.4,
            "website": 1.0,
            "google": 0.9,
            "social": 0.7,
            "flyer": 0.6,
            "unknown": 0.5,
        },
    },
}

# =============================================================================
# EMAIL TEMPLATES SETTINGS
# =============================================================================

EMAIL_CONFIG = {
    # Default from name
    "from_name": "{{practice_name}}",
    
    # Reply-to address
    "reply_to": "{{practice_email}}",
    
    # Email categories
    "categories": [
        "organizer",
        "reminder",
        "filing_update",
        "document_request",
        "winback",
        "welcome",
        "thank_you",
    ],
    
    # Signature template
    "signature": """
Best regards,
{{preparer_name}}
{{practice_name}}
{{practice_phone}}
""",
}

# =============================================================================
# INTEGRATION SETTINGS
# =============================================================================

INTEGRATIONS = {
    # Encyro secure portal
    "encyro": {
        "enabled": True,
        "use_for_organizers": True,
        "use_for_documents": True,
        "api_version": "v2",
    },
    
    # Tax software (future)
    "tax_software": {
        "enabled": False,
        "provider": None,  # "lacerte", "proseries", "ultratax", "drake"
    },
}

# =============================================================================
# DASHBOARD SETTINGS
# =============================================================================

DASHBOARD_CONFIG = {
    # Organizer status widget
    "organizer_widget": {
        "show_counts": True,
        "show_percentages": True,
        "highlight_overdue": True,
    },
    
    # Filing pipeline widget
    "pipeline_widget": {
        "stages": ["not_started", "in_progress", "review", "filed"],
        "show_deadlines": True,
    },
    
    # Lead source widget
    "lead_widget": {
        "show_roi": True,
        "show_conversion": True,
        "period": "current_season",
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_current_tax_year() -> int:
    """Returns the tax year for current filing season."""
    today = date.today()
    # If before April 15, we're filing for previous year
    # If after, we're preparing for current year
    if today.month < 5:
        return today.year - 1
    return today.year


def get_deadline_date(deadline_type: str = "personal") -> date:
    """Returns the filing deadline date for current year."""
    year = date.today().year
    deadlines = {
        "personal": f"{year}-04-15",
        "extension": f"{year}-10-15",
        "business": f"{year}-03-15",
        "business_ext": f"{year}-09-15",
    }
    return date.fromisoformat(deadlines.get(deadline_type, deadlines["personal"]))


def is_busy_season() -> bool:
    """Returns True if currently in tax busy season (Feb-Apr)."""
    month = date.today().month
    return 2 <= month <= 4


# =============================================================================
# EXPORT CONFIGURATION
# =============================================================================

TAX_MODULE_CONFIG = {
    "organizer": ORGANIZER_CONFIG,
    "filing": FILING_CONFIG,
    "lifecycle": LIFECYCLE_CONFIG,
    "winback": WINBACK_CONFIG,
    "wisp": WISP_CONFIG,
    "lead_source": LEAD_SOURCE_CONFIG,
    "email": EMAIL_CONFIG,
    "integrations": INTEGRATIONS,
    "dashboard": DASHBOARD_CONFIG,
}
