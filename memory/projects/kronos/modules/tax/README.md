# Kronos Tax Module (Layer 2)

**Version:** 1.0  
**Industry:** Tax Preparation  
**Built for:** Laura's Tax Practice  
**Status:** Production-Ready

---

## Overview

The Tax Module is a **pluggable industry-specific layer** for the Kronos platform. It provides complete tax practice management including tax organizer workflows, client lifecycle tracking, WISP compliance, and lead source analytics.

---

## Architecture

This module follows Kronos Layer 2 architecture:
- **Extends** Core Engine (Layer 1) - does NOT duplicate core functionality
- **Provides** tax-specific business logic, templates, and workflows
- **Integrates** seamlessly with any Kronos instance

---

## Features

### 1. Tax Organizer System
- Pre-built templates for different tax situations (W2, 1099, Business, Rental, etc.)
- Send/track/remind workflow automation
- Real-time status dashboard (Sent/Opened/Completed/Not Started)
- Auto-reminders for incomplete organizers
- Integration with secure portals (Encyro support)

### 2. Client Lifecycle Management
- Onboarding workflow (new client setup)
- Filing status tracking (pending → in-progress → filed → extended)
- Retention monitoring (flagging non-returning clients)
- Win-back campaigns (automated re-engagement)
- Multi-year client history

### 3. WISP Compliance
- 3-year email retention automation (IRS requirement)
- Encryption for sensitive files (tax documents, SSN, etc.)
- Access logging (who accessed what, when)
- Incident tracking (security events)
- Auto-timeout for inactive sessions
- Compliance reporting

### 4. Lead Source Tracking
- Tag by source (flyer, Google, website, referral)
- ROI reporting per source
- Conversion tracking (lead → client)
- Cost-per-acquisition analytics
- Source-specific follow-up workflows

---

## Module Structure

```
tax/
├── README.md                    # This file
├── config/
│   ├── module.json              # Module metadata & configuration
│   └── settings.py              # Tax-specific settings
├── models/
│   ├── tax_return.py            # Tax return data model
│   ├── tax_organizer.py         # Organizer data model
│   ├── tax_document.py          # Document classification
│   └── client_tax_profile.py   # Client tax-specific profile
├── services/
│   ├── organizer_service.py     # Organizer management logic
│   ├── lifecycle_service.py     # Client lifecycle workflows
│   ├── compliance_service.py    # WISP compliance automation
│   └── lead_tracking_service.py # Lead source analytics
├── templates/
│   ├── organizers/              # Tax organizer templates
│   ├── emails/                  # Tax-specific email templates
│   └── documents/               # Document templates
├── workflows/
│   ├── onboarding.py            # New client onboarding
│   ├── filing_workflow.py       # Tax filing process
│   ├── reminder_workflow.py     # Auto-reminder logic
│   └── winback_workflow.py      # Client retention campaigns
├── compliance/
│   ├── wisp_policy.md           # WISP documentation
│   ├── retention_rules.py       # 3-year retention logic
│   └── encryption_config.py     # Encryption standards
├── tests/
│   └── test_scenarios.md        # Testing scenarios
└── integrations/
    └── encyro.py                # Encyro secure portal integration
```

---

## Installation

1. **Ensure Core Engine (Layer 1) is installed**
2. **Copy tax module to modules directory:**
   ```bash
   cp -r modules/tax /path/to/kronos/modules/
   ```
3. **Run module installation:**
   ```bash
   python kronos.py module:install tax
   ```
4. **Configure tax-specific settings:**
   Edit `modules/tax/config/settings.py`

---

## Configuration

Key settings in `config/settings.py`:

```python
TAX_MODULE_CONFIG = {
    # Organizer settings
    "organizer_reminder_days": [7, 3, 1],  # Days before deadline
    "organizer_default_deadline": 30,       # Days from send date
    
    # Filing deadlines
    "tax_season_start": "01-15",
    "tax_deadline_personal": "04-15",
    "tax_deadline_extension": "10-15",
    
    # Retention settings
    "retention_period_years": 3,            # WISP requirement
    "retention_check_frequency": "daily",
    
    # Win-back settings
    "winback_trigger_days": 365,            # 1 year no return
    "winback_campaign_interval": 30,        # Days between attempts
    
    # Lead source settings
    "lead_sources": ["flyer", "google", "website", "referral", "social"],
    "default_lead_source": "unknown"
}
```

---

## Usage Examples

### Send Tax Organizer

```python
from modules.tax.services.organizer_service import OrganizerService

organizer_service = OrganizerService()

# Send organizer to client
organizer = organizer_service.send_organizer(
    client_id=123,
    template="w2_employee",
    year=2025,
    deadline="2026-03-15"
)

# Check status
status = organizer_service.get_status(organizer.id)
print(f"Status: {status.status}")  # Sent/Opened/Completed/Not Started
```

### Track Client Lifecycle

```python
from modules.tax.services.lifecycle_service import LifecycleService

lifecycle = LifecycleService()

# Onboard new client
client = lifecycle.onboard_client(
    name="Jane Doe",
    email="jane@example.com",
    tax_situation="w2_employee",
    lead_source="website"
)

# Update filing status
lifecycle.update_filing_status(
    client_id=client.id,
    year=2025,
    status="in_progress"
)

# Check retention risk
risk = lifecycle.check_retention_risk(client.id)
if risk > 0.7:
    lifecycle.trigger_winback_campaign(client.id)
```

### WISP Compliance

```python
from modules.tax.services.compliance_service import ComplianceService

compliance = ComplianceService()

# Encrypt sensitive file
encrypted_path = compliance.encrypt_file(
    file_path="/uploads/client_ssn.pdf",
    client_id=123
)

# Log access
compliance.log_access(
    user_id=5,
    resource="tax_return_2025",
    client_id=123,
    action="view"
)

# Check retention compliance
compliance.enforce_retention_policy()  # Runs daily, archives old data
```

### Lead Source Analytics

```python
from modules.tax.services.lead_tracking_service import LeadTrackingService

tracking = LeadTrackingService()

# Tag lead
tracking.tag_lead(lead_id=456, source="google", campaign="tax_season_2026")

# Get ROI report
report = tracking.get_roi_report(year=2025)
for source in report:
    print(f"{source.name}: {source.conversion_rate}%, ${source.revenue}")
```

---

## Database Schema Extensions

This module extends Core Engine with tax-specific tables:

### tax_returns
```sql
CREATE TABLE tax_returns (
    id SERIAL PRIMARY KEY,
    client_id INT REFERENCES clients(id),
    year INT NOT NULL,
    status VARCHAR(50),  -- pending, in_progress, filed, extended
    filing_type VARCHAR(50),  -- personal, business, partnership, etc.
    filed_date DATE,
    extension_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### tax_organizers
```sql
CREATE TABLE tax_organizers (
    id SERIAL PRIMARY KEY,
    client_id INT REFERENCES clients(id),
    year INT NOT NULL,
    template VARCHAR(100),  -- w2_employee, self_employed, rental, etc.
    sent_date TIMESTAMP,
    opened_date TIMESTAMP,
    completed_date TIMESTAMP,
    deadline_date DATE,
    status VARCHAR(50),  -- not_started, sent, opened, completed
    reminder_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### tax_documents
```sql
CREATE TABLE tax_documents (
    id SERIAL PRIMARY KEY,
    return_id INT REFERENCES tax_returns(id),
    document_type VARCHAR(100),  -- w2, 1099, receipt, etc.
    file_id INT REFERENCES files(id),
    year INT,
    encrypted BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### client_tax_profiles
```sql
CREATE TABLE client_tax_profiles (
    id SERIAL PRIMARY KEY,
    client_id INT REFERENCES clients(id),
    tax_situation VARCHAR(100),  -- w2_employee, self_employed, business_owner, etc.
    filing_frequency VARCHAR(50),  -- annual, quarterly
    has_dependents BOOLEAN,
    has_business BOOLEAN,
    has_rentals BOOLEAN,
    preferred_contact VARCHAR(50),  -- email, phone, sms
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### wisp_access_logs
```sql
CREATE TABLE wisp_access_logs (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    client_id INT,
    resource_type VARCHAR(100),
    resource_id INT,
    action VARCHAR(50),  -- view, edit, delete, download
    ip_address VARCHAR(50),
    timestamp TIMESTAMP DEFAULT NOW()
);
```

### wisp_incidents
```sql
CREATE TABLE wisp_incidents (
    id SERIAL PRIMARY KEY,
    incident_type VARCHAR(100),  -- unauthorized_access, data_breach, suspicious_activity
    severity VARCHAR(50),  -- low, medium, high, critical
    description TEXT,
    affected_clients INT[],
    reported_by INT REFERENCES users(id),
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);
```

---

## API Endpoints

Tax module adds these endpoints to Core Engine:

### Organizers
- `POST /api/tax/organizers` - Send organizer
- `GET /api/tax/organizers/:id` - Get organizer status
- `GET /api/tax/organizers/client/:clientId` - List client organizers
- `PUT /api/tax/organizers/:id/complete` - Mark completed
- `POST /api/tax/organizers/:id/remind` - Send reminder

### Filing
- `POST /api/tax/returns` - Create tax return record
- `GET /api/tax/returns/:id` - Get return details
- `PUT /api/tax/returns/:id/status` - Update filing status
- `GET /api/tax/clients/:clientId/returns` - Client filing history

### Compliance
- `GET /api/tax/compliance/status` - WISP compliance dashboard
- `GET /api/tax/compliance/logs` - Access logs (filtered)
- `POST /api/tax/compliance/incident` - Report incident
- `GET /api/tax/compliance/retention` - Retention status

### Analytics
- `GET /api/tax/analytics/lead-sources` - Lead source ROI
- `GET /api/tax/analytics/retention` - Retention metrics
- `GET /api/tax/analytics/pipeline` - Filing pipeline status

---

## Testing

See `tests/test_scenarios.md` for comprehensive testing scenarios covering:
- Organizer workflow (send, track, remind, complete)
- Client lifecycle (onboarding, filing, retention, winback)
- WISP compliance (encryption, logging, retention)
- Lead tracking (tagging, conversion, ROI)

---

## Compliance Notes

This module is built to support **WISP (Written Information Security Plan)** compliance required by IRS for tax preparers:

✅ **3-year retention** - All client communications and documents retained for 3 years  
✅ **Encryption** - Sensitive files encrypted at rest (AES-256)  
✅ **Access logging** - All data access tracked with user, time, IP  
✅ **Incident tracking** - Security incidents logged and tracked  
✅ **Auto-timeout** - Inactive sessions automatically logged out  

See `compliance/wisp_policy.md` for full documentation.

---

## Customization

To customize for another tax practice:

1. **Templates:** Edit organizer templates in `templates/organizers/`
2. **Deadlines:** Adjust filing deadlines in `config/settings.py`
3. **Workflows:** Modify reminder/winback frequency in workflows
4. **Lead Sources:** Add practice-specific lead sources to config
5. **Branding:** All client-facing templates support variable replacement

---

## Support

For issues or questions:
- Check `tests/test_scenarios.md` for usage examples
- Review `compliance/wisp_policy.md` for compliance requirements
- See Core Engine documentation for base functionality

---

## Version History

- **1.0** (2026-01-26) - Initial release for Laura's Tax Practice
  - Tax organizer system
  - Client lifecycle management
  - WISP compliance automation
  - Lead source tracking

---

*Built for Kronos Platform - Modular Industry Automation*
