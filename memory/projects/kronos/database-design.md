# Kronos Database Design Documentation

**Version:** 1.0  
**Last Updated:** 2026-01-26  
**Database:** PostgreSQL 15+

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           KRONOS DATABASE SCHEMA                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐         ┌──────────────────┐                          │
│  │ client_instances │◄────────┤      users       │                          │
│  │──────────────────│   1:N   │──────────────────│                          │
│  │ id (PK)          │         │ id (PK)          │                          │
│  │ name             │         │ client_instance_id│                          │
│  │ slug             │         │ email            │                          │
│  │ industry         │         │ password_hash    │                          │
│  │ settings (JSON)  │         │ role             │                          │
│  │ branding (JSON)  │         │ is_active        │                          │
│  └──────────────────┘         └────────┬─────────┘                          │
│           │                            │                                     │
│           │ 1:N                        │ 1:1                                 │
│           ▼                            ▼                                     │
│  ┌──────────────────┐         ┌──────────────────┐                          │
│  │      leads       │─────────►│     clients      │                          │
│  │──────────────────│  conv.  │──────────────────│                          │
│  │ id (PK)          │         │ id (PK)          │                          │
│  │ client_instance_id│         │ client_instance_id│                          │
│  │ user_id (FK)     │         │ user_id (FK)     │                          │
│  │ name             │         │ lead_id (FK)     │                          │
│  │ email, phone     │         │ business_name    │                          │
│  │ source           │         │ status           │                          │
│  │ status           │         │ lifetime_value   │                          │
│  │ lead_score       │         │ retention_risk   │                          │
│  │ is_price_shopper │         │ last_interaction │                          │
│  └────────┬─────────┘         └────────┬─────────┘                          │
│           │                            │                                     │
│           │ 1:N                        │ 1:N                                 │
│           ▼                            ▼                                     │
│  ┌──────────────────┐         ┌──────────────────┐                          │
│  │    messages      │         │      files       │                          │
│  │──────────────────│         │──────────────────│                          │
│  │ id (PK)          │         │ id (PK)          │                          │
│  │ client_instance_id│         │ client_instance_id│                          │
│  │ lead_id (FK)     │         │ client_id (FK)   │                          │
│  │ client_id (FK)   │         │ message_id (FK)  │                          │
│  │ channel          │         │ filename         │                          │
│  │ category         │         │ storage_path     │                          │
│  │ thread_id        │         │ is_encrypted     │                          │
│  │ body             │         │ year             │                          │
│  │ retention_until  │         │ retention_until  │                          │
│  └──────────────────┘         └──────────────────┘                          │
│           │                            │                                     │
│           │                            │                                     │
│  ┌──────────────────┐         ┌──────────────────┐                          │
│  │      tasks       │         │    audit_logs    │                          │
│  │──────────────────│         │──────────────────│                          │
│  │ id (PK)          │         │ id (PK)          │                          │
│  │ client_id (FK)   │         │ user_id (FK)     │                          │
│  │ lead_id (FK)     │         │ action           │                          │
│  │ assigned_to (FK) │         │ resource_type    │                          │
│  │ title            │         │ resource_id      │                          │
│  │ status           │         │ old_values (JSON)│                          │
│  │ priority         │         │ new_values (JSON)│                          │
│  │ due_date         │         │ ip_address       │                          │
│  └──────────────────┘         └──────────────────┘                          │
│                                                                              │
│  ═══════════════════════════════════════════════════════════════════════    │
│                            TAX MODULE TABLES                                 │
│  ═══════════════════════════════════════════════════════════════════════    │
│                                                                              │
│  ┌──────────────────┐         ┌──────────────────┐                          │
│  │   tax_returns    │◄────────┤  tax_organizers  │                          │
│  │──────────────────│   1:1   │──────────────────│                          │
│  │ id (PK)          │         │ id (PK)          │                          │
│  │ client_id (FK)   │         │ client_id (FK)   │                          │
│  │ tax_year         │         │ tax_return_id(FK)│                          │
│  │ status           │         │ tax_year         │                          │
│  │ filed_at         │         │ status           │                          │
│  │ preparer_id (FK) │         │ sent_at          │                          │
│  │ refund_amount    │         │ opened_at        │                          │
│  └────────┬─────────┘         │ completed_at     │                          │
│           │                   │ sections (JSON)  │                          │
│           │ 1:N               └──────────────────┘                          │
│           ▼                                                                  │
│  ┌──────────────────┐                                                        │
│  │  tax_documents   │                                                        │
│  │──────────────────│                                                        │
│  │ id (PK)          │                                                        │
│  │ tax_return_id(FK)│                                                        │
│  │ file_id (FK)     │                                                        │
│  │ document_type    │                                                        │
│  │ extracted_data   │                                                        │
│  │ is_verified      │                                                        │
│  └──────────────────┘                                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Table Descriptions

### Core Tables

#### client_instances
Multi-tenant container. Each tax practice/law firm/medical office gets one instance.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | VARCHAR(255) | Instance name ("Laura's Tax Practice") |
| slug | VARCHAR(100) | URL-safe identifier |
| industry | VARCHAR(50) | Industry module: 'tax', 'law', 'medical' |
| settings | JSONB | Instance configuration |
| branding | JSONB | Logo, colors, domain |

#### users
Authentication and identity for all user types.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| client_instance_id | UUID | FK to client_instances |
| email | VARCHAR(255) | Login email |
| email_encrypted | BYTEA | WISP: Encrypted PII option |
| role | ENUM | admin, staff, client, lead |
| is_active | BOOLEAN | Account status |

#### leads
Potential clients before conversion.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| source | VARCHAR(100) | 'website', 'referral', 'google', 'flyer' |
| status | ENUM | new, contacted, qualified, converted, dead |
| lead_score | INTEGER | AI-calculated 0-100 |
| is_price_shopper | BOOLEAN | Flagged by AI qualifier |
| qualification_answers | JSONB | Responses to qualifier questions |

#### clients
Active client relationships (converted from leads).

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| lead_id | UUID | Original lead record |
| lifetime_value | DECIMAL | Total revenue from client |
| retention_risk_score | INTEGER | 0-100, higher = more risk |
| risk_factors | JSONB | AI-identified churn signals |
| next_followup_date | DATE | Scheduled touchpoint |

#### messages
All communications (email, SMS, portal, phone).

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| channel | ENUM | email, sms, web, phone, portal |
| category | ENUM | prospective, client, office, spam, other |
| category_confidence | DECIMAL | AI classification confidence |
| thread_id | UUID | Message threading |
| retention_until | DATE | WISP: 3-year retention date |

#### files
Document storage with encryption support.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| storage_path | VARCHAR | S3/storage path |
| is_encrypted | BOOLEAN | WISP: Encryption status |
| encryption_key_id | VARCHAR | Key reference |
| year | INTEGER | Tax year organization |
| retention_until | DATE | WISP: Retention date |

#### tasks
Todo items, reminders, organizer tasks.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| task_type | VARCHAR | 'followup', 'organizer', 'document_request' |
| status | ENUM | pending, in_progress, completed, cancelled |
| priority | ENUM | low, medium, high, urgent |
| is_recurring | BOOLEAN | Repeating task |
| recurrence_rule | VARCHAR | iCal RRULE format |

#### audit_logs
WISP compliance - all system actions logged.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Actor |
| action | VARCHAR | 'login', 'view', 'create', 'update', 'delete' |
| resource_type | VARCHAR | Table/entity affected |
| old_values | JSONB | Previous state |
| new_values | JSONB | New state |
| is_security_event | BOOLEAN | Flag for security review |

---

### Tax Module Tables

#### tax_returns
Annual tax return records per client.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| client_id | UUID | FK to clients |
| tax_year | INTEGER | Filing year |
| status | ENUM | not_started → filed pipeline |
| preparer_id | UUID | Assigned tax preparer |
| filed_at | TIMESTAMPTZ | Filing timestamp |
| refund_amount | DECIMAL | Calculated refund |

#### tax_organizers
Questionnaires sent to clients to gather tax info.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tax_return_id | UUID | FK to tax_returns |
| status | ENUM | not_sent, sent, opened, in_progress, completed |
| sent_at | TIMESTAMPTZ | When sent |
| opened_at | TIMESTAMPTZ | Client opened it |
| completed_at | TIMESTAMPTZ | Client finished |
| sections | JSONB | Organizer sections & progress |
| responses | JSONB | Client's answers |

#### tax_documents
Documents linked to tax returns (W2s, 1099s, etc.).

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tax_return_id | UUID | FK to tax_returns |
| file_id | UUID | FK to files |
| document_type | VARCHAR | 'w2', '1099', 'receipt', 'prior_return' |
| extracted_data | JSONB | AI-extracted fields |
| is_verified | BOOLEAN | Preparer verified accuracy |

---

## WISP Compliance Features

### 1. Encryption at Rest
- `*_encrypted` columns for PII (email, phone, address)
- Files stored with encryption flag
- `encryption_key_id` tracks which key was used

### 2. Access Logging
- `audit_logs` table captures all data access
- Includes IP address, user agent
- Security events flagged for review

### 3. 3-Year Retention
- `retention_until` column on messages, files, tax_returns
- `deleted_at` soft deletes (never hard delete within retention)
- `archived_at` for archival workflow

### 4. Data Minimization
- JSONB for flexible fields (no excessive columns)
- Clear purpose for each data point

---

## Common Queries

### Get all unread messages by category (Daily Digest)
```sql
SELECT 
    category,
    COUNT(*) as count,
    array_agg(id ORDER BY received_at DESC) as message_ids
FROM messages
WHERE client_instance_id = $1
  AND status = 'unread'
  AND deleted_at IS NULL
GROUP BY category;
```

### Lead scoring dashboard
```sql
SELECT 
    l.id,
    l.name,
    l.email,
    l.source,
    l.lead_score,
    l.is_price_shopper,
    l.created_at,
    l.status
FROM leads l
WHERE l.client_instance_id = $1
  AND l.status NOT IN ('converted', 'dead')
  AND l.deleted_at IS NULL
ORDER BY l.lead_score DESC, l.created_at DESC
LIMIT 50;
```

### Tax organizer tracking
```sql
SELECT 
    o.id,
    c.contact_name,
    c.email,
    o.status,
    o.sent_at,
    o.opened_at,
    o.completed_at,
    o.reminder_count
FROM tax_organizers o
JOIN clients c ON o.client_id = c.id
WHERE o.client_instance_id = $1
  AND o.tax_year = $2
  AND o.deleted_at IS NULL
ORDER BY 
    CASE o.status 
        WHEN 'not_sent' THEN 1
        WHEN 'sent' THEN 2
        WHEN 'opened' THEN 3
        WHEN 'in_progress' THEN 4
        WHEN 'completed' THEN 5
    END;
```

### At-risk clients (retention)
```sql
SELECT 
    c.id,
    c.contact_name,
    c.email,
    c.retention_risk_score,
    c.risk_factors,
    c.last_interaction_at,
    c.lifetime_value
FROM clients c
WHERE c.client_instance_id = $1
  AND c.status = 'active'
  AND c.retention_risk_score >= 50
  AND c.deleted_at IS NULL
ORDER BY c.retention_risk_score DESC;
```

### Full-text message search
```sql
SELECT 
    m.id,
    m.subject,
    m.body,
    m.category,
    m.received_at,
    ts_rank(to_tsvector('english', m.body), query) as rank
FROM messages m,
     plainto_tsquery('english', $2) query
WHERE m.client_instance_id = $1
  AND to_tsvector('english', m.body) @@ query
  AND m.deleted_at IS NULL
ORDER BY rank DESC, m.received_at DESC
LIMIT 20;
```

### Client tax history
```sql
SELECT 
    tr.tax_year,
    tr.status,
    tr.return_type,
    tr.filed_at,
    tr.refund_amount,
    tr.amount_owed,
    o.status as organizer_status,
    COUNT(td.id) as document_count
FROM tax_returns tr
LEFT JOIN tax_organizers o ON o.tax_return_id = tr.id
LEFT JOIN tax_documents td ON td.tax_return_id = tr.id
WHERE tr.client_id = $1
  AND tr.deleted_at IS NULL
GROUP BY tr.id, o.id
ORDER BY tr.tax_year DESC;
```

---

## Data Retention Strategy

### Retention Periods
| Data Type | Retention | Reason |
|-----------|-----------|--------|
| Tax returns | 7 years | IRS audit period |
| Tax documents | 7 years | Supporting documentation |
| Client communications | 3 years | WISP requirement |
| Audit logs | 7 years | Compliance |
| Lead data | 2 years | GDPR-like best practice |
| Analytics | 5 years | Business intelligence |

### Archival Process
1. Daily job identifies records past retention_until
2. Records moved to archive tables (append `_archive`)
3. Original records soft-deleted (deleted_at set)
4. Quarterly: Hard delete from archive after legal hold review

### Soft Delete Pattern
```sql
-- All queries filter: WHERE deleted_at IS NULL
-- Delete operation:
UPDATE table SET deleted_at = NOW() WHERE id = $1;

-- Restore if needed:
UPDATE table SET deleted_at = NULL WHERE id = $1;
```

---

## Index Strategy

### Primary Access Patterns
1. **By client_instance_id** - Multi-tenant isolation
2. **By status** - Workflow filtering (leads, returns, organizers)
3. **By date** - Time-based queries (recent messages, due dates)
4. **Full-text search** - Message body/subject search

### Partial Indexes
Exclude soft-deleted records from indexes:
```sql
CREATE INDEX idx_leads_deleted ON leads(deleted_at) WHERE deleted_at IS NULL;
```

### JSONB Indexes
For frequently queried JSON fields:
```sql
CREATE INDEX idx_analytics_dimensions ON analytics USING gin(dimensions);
```

---

## Migration Notes

### Adding New Industry Modules
1. Create industry-specific tables (like tax_* tables)
2. Add industry value to client_instances.industry
3. No changes to core tables required

### Schema Versioning
- Use sequential migration files: `001_initial.sql`, `002_add_column.sql`
- Never modify existing migrations
- Include rollback scripts

---

*This documentation should be updated with any schema changes.*
