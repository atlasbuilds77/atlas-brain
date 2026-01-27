# Kronos Architecture - Modular Industry Platform

**Version:** 1.0 (Laura Pilot Foundation)
**Date:** 2026-01-26

---

## CORE PHILOSOPHY

**Build Once, Clone Infinitely**

Every component is industry-agnostic at its core. Industry-specific logic is PLUGGABLE, not hardcoded.

---

## SYSTEM LAYERS

### Layer 1: CORE ENGINE (Universal)
**What it does:** Handles all platform fundamentals
**Industry specificity:** NONE - works for any industry

Components:
- User authentication & sessions
- Database models (clients, leads, messages, files)
- API gateway & routing
- Security & encryption (WISP-compliant baseline)
- Data retention & archiving
- Daily digest engine
- Notification system
- Analytics & reporting engine

**Built once. Never touched again (except updates).**

---

### Layer 2: INDUSTRY MODULES (Pluggable)
**What it does:** Industry-specific business logic
**Industry specificity:** HIGH - swap per client

Components for TAX (Laura):
- Tax organizer templates
- IRS compliance rules (3-year retention, WISP)
- Lead qualifier questions (tax-specific)
- Client lifecycle (onboarding → filing → retention)
- Tax software integrations (if needed)
- Industry terminology & workflows

Components for LAW (future):
- Case intake forms
- Attorney-client privilege rules
- Court date tracking
- Legal document templates
- Bar association compliance

Components for MEDICAL (future):
- HIPAA compliance
- EMR integration
- Appointment scheduling
- Patient intake forms
- Insurance verification

**Each industry = new module. Core engine unchanged.**

---

### Layer 3: CLIENT INTERFACE (Customizable)
**What it does:** How clients interact with system
**Industry specificity:** BRANDING only

Options:
- Web dashboard (custom domain, branding)
- Email interface (send/receive commands via email)
- SMS/iMessage (text-based interaction)
- API (for integrations)

**Same interface code. Different branding/domain per client.**

---

## DATA MODEL (Universal Schema)

### Core Tables (Industry-Agnostic)

**Users**
- id, email, name, role (admin/client/lead)
- created_at, last_active
- auth tokens

**Leads**
- id, name, email, phone, source
- status (new/qualified/converted/dead)
- lead_score (AI-calculated)
- assigned_to, created_at, converted_at
- notes, tags

**Clients** (extends Leads)
- id, user_id (fk)
- client_since, status (active/inactive/churned)
- lifetime_value, retention_risk_score
- last_interaction, next_followup

**Messages**
- id, from, to, channel (email/sms/web)
- subject, body, timestamp
- thread_id, status (read/unread/archived)
- category (prospective/client/office/other)
- attachments[]

**Files**
- id, client_id, filename, path
- uploaded_at, year (for tax), category
- encrypted (boolean), retention_until

**Tasks** (for organizers, reminders, etc.)
- id, client_id, type, status
- due_date, completed_at, assigned_to
- template_id (for organizers)

**Analytics**
- id, metric, value, timestamp
- dimensions (lead_source, client_type, etc.)

---

### Industry-Specific Tables (Pluggable)

**TAX Module:**
- tax_returns (id, client_id, year, status, filed_date)
- tax_organizers (id, client_id, year, sent_date, status)
- tax_documents (id, return_id, type, path)

**LAW Module:**
- cases (id, client_id, type, status, court_date)
- case_documents (id, case_id, type, path)
- billable_hours (id, case_id, hours, rate)

**MEDICAL Module:**
- appointments (id, client_id, date, type, status)
- prescriptions (id, client_id, medication, dosage)
- insurance (id, client_id, provider, policy_number)

**Industry tables extend core. Core never changes.**

---

## AI COMPONENTS (Universal with Industry Context)

### 1. Lead Qualifier Bot
**Core logic:** Score leads based on responses
**Industry context:** Questions differ per industry

Tax questions:
- "What tax services do you need?"
- "Have you filed in the past?"
- "Are you shopping for price or service?"

Law questions:
- "What type of legal issue?"
- "Have you consulted attorney before?"
- "What's your timeline?"

**Same scoring algorithm. Different questions.**

---

### 2. Email Organizer
**Core logic:** Categorize incoming messages
**Industry context:** Categories differ per industry

Tax categories:
- Prospective (new leads)
- Active Client (current tax work)
- Office (admin, billing)
- Spam

Law categories:
- New Case Inquiry
- Active Case Communication
- Court Notices
- Billing

**Same NLP engine. Different labels.**

---

### 3. Daily Digest
**Core logic:** Aggregate messages, summarize
**Industry context:** Prioritization differs

Tax priorities during busy season:
1. Client questions blocking filing
2. Missing documents
3. New leads (lower priority)

Law priorities:
1. Court deadlines
2. Client emergencies
3. New consultations

**Same aggregation. Different sorting.**

---

### 4. Retention Predictor
**Core logic:** ML model predicts churn risk
**Industry context:** Signals differ per industry

Tax churn signals:
- Didn't return after 2 years
- Complained about price
- Slow to provide documents

Law churn signals:
- Unhappy with case outcome
- Billing disputes
- Poor communication response

**Same model architecture. Different features.**

---

## FEATURE MATRIX

| Feature | Core Engine | Industry Module | Client Branding |
|---------|-------------|-----------------|-----------------|
| User Auth | ✅ | ❌ | ❌ |
| Database | ✅ | ⚙️ (extends) | ❌ |
| Lead Scoring | ✅ | ⚙️ (context) | ❌ |
| Email Sorting | ✅ | ⚙️ (categories) | ❌ |
| Daily Digest | ✅ | ⚙️ (priorities) | ❌ |
| File Storage | ✅ | ⚙️ (structure) | ❌ |
| Compliance | ✅ | ⚙️ (rules) | ❌ |
| Retention Tracking | ✅ | ⚙️ (signals) | ❌ |
| Web Interface | ✅ | ❌ | ⚙️ (branding) |
| API | ✅ | ❌ | ❌ |

**Legend:**
- ✅ = Universal (build once)
- ⚙️ = Pluggable (swap per industry)
- ❌ = Not used

---

## DEPLOYMENT ARCHITECTURE

### Single-Tenant (Laura Pilot)
```
Laura's Instance
├── Core Engine (v1.0)
├── Tax Module (v1.0)
└── Laura Branding
```

### Multi-Tenant (Production)
```
Kronos Platform
├── Core Engine (v1.0)
├── Industry Modules
│   ├── Tax (v1.0)
│   ├── Law (v1.1)
│   └── Medical (v1.0)
└── Client Instances
    ├── Laura (Tax)
    ├── Law Firm A (Law)
    ├── Doctor B (Medical)
    └── Accountant C (Tax - reuses module)
```

**Each client = isolated instance**
**Shared: Core engine + their industry module**
**Unique: Data, branding, domain**

---

## TECH STACK (Recommended)

### Backend
- **Language:** Python (Flask/FastAPI) or Node.js (Express)
- **Database:** PostgreSQL (relational + JSONB for flexibility)
- **Cache:** Redis (sessions, rate limiting)
- **Queue:** Celery or BullMQ (async tasks)
- **Storage:** S3-compatible (encrypted files)

### AI/ML
- **NLP:** OpenAI API (GPT-4) or Claude
- **Embeddings:** text-embedding-3-small (email categorization)
- **ML Models:** scikit-learn (retention prediction)

### Frontend
- **Framework:** React or Next.js
- **UI:** Tailwind CSS
- **Dashboard:** Chart.js or Recharts

### Infrastructure
- **Hosting:** AWS/GCP/Azure
- **CDN:** CloudFlare
- **Email:** SendGrid or AWS SES
- **SMS:** Twilio
- **Monitoring:** Sentry + LogRocket

---

## BUILD SEQUENCE (Laura Pilot)

### Phase 1: MVP Core (Week 1-2)
1. Database schema (core + tax tables)
2. User auth + sessions
3. Lead capture form (website integration)
4. Basic email ingestion (IMAP)
5. Simple web dashboard (view leads, clients, messages)

### Phase 2: AI Features (Week 3)
1. Lead qualifier bot (tax questions)
2. Email categorizer (prospective/client/office)
3. Daily digest (morning summary)

### Phase 3: Tax-Specific (Week 4)
1. Tax organizer templates
2. Organizer tracking (sent/opened/completed)
3. Retention analytics
4. WISP compliance (encryption, logging, retention)

### Phase 4: Polish & Deploy (End of January)
1. Testing with Laura
2. Bug fixes
3. Performance optimization
4. Training Laura on system
5. Go live before Feb 1

---

## REUSABILITY CHECKLIST

Before building ANY feature, ask:

1. **Is this industry-agnostic?** → Core Engine
2. **Is this industry-specific logic?** → Industry Module
3. **Is this just branding?** → Client Interface

If mixing layers = BAD ARCHITECTURE. Refactor immediately.

**Goal:** Every feature built for Laura should be 80% reusable for next client.

---

## SUCCESS METRICS

### For Laura (Pilot)
- Lead response time: <5 min automated reply
- Email sorting accuracy: >90%
- Daily digest delivery: 6am every day
- Tax organizer tracking: Real-time status
- Retention prediction: 75%+ accuracy

### For Kronos (Platform)
- New industry module: <2 weeks to build
- New client onboarding: <1 day
- Core engine stability: 99.9% uptime
- Reuse ratio: 80%+ code shared across clients

---

*This architecture is the foundation. Every decision respects modularity. Build smart once, profit forever.*
