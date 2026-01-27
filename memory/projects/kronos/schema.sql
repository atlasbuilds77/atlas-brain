-- ============================================================================
-- KRONOS DATABASE SCHEMA v1.0
-- PostgreSQL 15+
-- 
-- Modular industry platform - Core + Tax Module (Laura Pilot)
-- WISP-compliant, multi-tenant ready, 3-year retention support
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- ENUMS
-- ============================================================================

CREATE TYPE user_role AS ENUM ('admin', 'staff', 'client', 'lead');
CREATE TYPE lead_status AS ENUM ('new', 'contacted', 'qualified', 'converted', 'dead');
CREATE TYPE client_status AS ENUM ('active', 'inactive', 'churned');
CREATE TYPE message_channel AS ENUM ('email', 'sms', 'web', 'phone', 'portal');
CREATE TYPE message_status AS ENUM ('unread', 'read', 'archived', 'deleted');
CREATE TYPE message_category AS ENUM ('prospective', 'client', 'office', 'spam', 'other');
CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'completed', 'cancelled');
CREATE TYPE task_priority AS ENUM ('low', 'medium', 'high', 'urgent');
CREATE TYPE tax_return_status AS ENUM ('not_started', 'organizer_sent', 'docs_received', 'in_progress', 'review', 'filed', 'amended');
CREATE TYPE organizer_status AS ENUM ('not_sent', 'sent', 'opened', 'in_progress', 'completed');

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Multi-tenant: Client Instances (for platform scaling)
CREATE TABLE client_instances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    industry VARCHAR(50) NOT NULL DEFAULT 'tax',
    settings JSONB DEFAULT '{}',
    branding JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ NULL
);

-- Users (authentication & identity)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_instance_id UUID REFERENCES client_instances(id),
    email VARCHAR(255) NOT NULL,
    email_encrypted BYTEA,  -- WISP: encrypted PII storage option
    password_hash VARCHAR(255),
    name VARCHAR(255),
    phone VARCHAR(50),
    phone_encrypted BYTEA,  -- WISP: encrypted PII
    role user_role DEFAULT 'lead',
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    last_login_at TIMESTAMPTZ,
    last_active_at TIMESTAMPTZ,
    auth_token VARCHAR(255),
    token_expires_at TIMESTAMPTZ,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ NULL,
    
    CONSTRAINT unique_email_per_instance UNIQUE (client_instance_id, email)
);

-- Leads (potential clients)
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_instance_id UUID REFERENCES client_instances(id),
    user_id UUID REFERENCES users(id),
    
    -- Contact info
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    
    -- Lead tracking
    source VARCHAR(100),  -- 'website', 'referral', 'google', 'flyer', 'social'
    source_detail VARCHAR(255),  -- specific campaign, referrer name, etc.
    status lead_status DEFAULT 'new',
    lead_score INTEGER DEFAULT 0,  -- AI-calculated 0-100
    score_factors JSONB DEFAULT '{}',  -- breakdown of score
    
    -- Qualification
    is_price_shopper BOOLEAN DEFAULT FALSE,
    qualification_answers JSONB DEFAULT '{}',
    qualified_at TIMESTAMPTZ,
    qualified_by UUID REFERENCES users(id),
    
    -- Assignment
    assigned_to UUID REFERENCES users(id),
    
    -- Conversion
    converted_at TIMESTAMPTZ,
    converted_to_client_id UUID,  -- FK added after clients table
    conversion_value DECIMAL(12,2),
    
    -- Metadata
    notes TEXT,
    tags TEXT[],
    custom_fields JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ NULL
);

-- Clients (converted leads, active relationships)
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_instance_id UUID REFERENCES client_instances(id),
    user_id UUID REFERENCES users(id),
    lead_id UUID REFERENCES leads(id),
    
    -- Client info (may duplicate user for business entity clients)
    business_name VARCHAR(255),
    contact_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    address_encrypted BYTEA,  -- WISP: sensitive address data
    
    -- Status
    status client_status DEFAULT 'active',
    client_since DATE,
    
    -- Value metrics
    lifetime_value DECIMAL(12,2) DEFAULT 0,
    annual_value DECIMAL(12,2) DEFAULT 0,
    
    -- Retention
    retention_risk_score INTEGER DEFAULT 0,  -- 0-100, higher = more risk
    risk_factors JSONB DEFAULT '{}',
    last_service_date DATE,
    next_followup_date DATE,
    
    -- Interaction tracking
    last_interaction_at TIMESTAMPTZ,
    interaction_count INTEGER DEFAULT 0,
    
    -- Metadata
    notes TEXT,
    tags TEXT[],
    custom_fields JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ NULL
);

-- Add FK from leads to clients
ALTER TABLE leads ADD CONSTRAINT fk_leads_converted_client 
    FOREIGN KEY (converted_to_client_id) REFERENCES clients(id);

-- Messages (all communications)
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_instance_id UUID REFERENCES client_instances(id),
    
    -- Participants
    from_user_id UUID REFERENCES users(id),
    to_user_id UUID REFERENCES users(id),
    from_address VARCHAR(255),  -- external email/phone
    to_address VARCHAR(255),
    
    -- Related entities
    lead_id UUID REFERENCES leads(id),
    client_id UUID REFERENCES clients(id),
    
    -- Message content
    channel message_channel NOT NULL,
    subject VARCHAR(500),
    body TEXT,
    body_encrypted BYTEA,  -- WISP: for sensitive content
    body_html TEXT,
    
    -- Threading
    thread_id UUID,
    parent_message_id UUID REFERENCES messages(id),
    
    -- Status & categorization
    status message_status DEFAULT 'unread',
    category message_category DEFAULT 'other',
    category_confidence DECIMAL(3,2),  -- AI confidence 0.00-1.00
    is_inbound BOOLEAN DEFAULT TRUE,
    is_automated BOOLEAN DEFAULT FALSE,
    
    -- Attachments (stored in files table)
    attachment_count INTEGER DEFAULT 0,
    
    -- Metadata
    external_id VARCHAR(255),  -- email message-id, SMS sid, etc.
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    sent_at TIMESTAMPTZ,
    received_at TIMESTAMPTZ,
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ NULL,
    
    -- WISP: 3-year retention tracking
    retention_until DATE,
    archived_at TIMESTAMPTZ
);

-- Files (document storage)
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_instance_id UUID REFERENCES client_instances(id),
    
    -- Ownership
    user_id UUID REFERENCES users(id),
    client_id UUID REFERENCES clients(id),
    message_id UUID REFERENCES messages(id),
    
    -- File info
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255),
    mime_type VARCHAR(100),
    file_size BIGINT,
    
    -- Storage
    storage_path VARCHAR(500) NOT NULL,
    storage_bucket VARCHAR(100),
    checksum VARCHAR(64),  -- SHA-256
    
    -- Organization
    year INTEGER,  -- for tax year organization
    category VARCHAR(100),
    subcategory VARCHAR(100),
    
    -- Security (WISP)
    is_encrypted BOOLEAN DEFAULT TRUE,
    encryption_key_id VARCHAR(100),
    
    -- Retention (WISP)
    retention_until DATE,
    archived_at TIMESTAMPTZ,
    
    -- Metadata
    description TEXT,
    tags TEXT[],
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ NULL
);

-- Tasks (organizers, reminders, todos)
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_instance_id UUID REFERENCES client_instances(id),
    
    -- Assignment
    client_id UUID REFERENCES clients(id),
    lead_id UUID REFERENCES leads(id),
    assigned_to UUID REFERENCES users(id),
    created_by UUID REFERENCES users(id),
    
    -- Task details
    title VARCHAR(255) NOT NULL,
    description TEXT,
    task_type VARCHAR(50),  -- 'followup', 'organizer', 'document_request', 'review'
    
    -- Status & priority
    status task_status DEFAULT 'pending',
    priority task_priority DEFAULT 'medium',
    
    -- Scheduling
    due_date DATE,
    due_time TIME,
    reminder_at TIMESTAMPTZ,
    
    -- Completion
    completed_at TIMESTAMPTZ,
    completed_by UUID REFERENCES users(id),
    
    -- Templates
    template_id UUID,  -- references task_templates if used
    template_data JSONB DEFAULT '{}',
    
    -- Recurrence
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_rule VARCHAR(100),  -- iCal RRULE format
    parent_task_id UUID REFERENCES tasks(id),
    
    -- Metadata
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ NULL
);

-- Analytics (metrics & events)
CREATE TABLE analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_instance_id UUID REFERENCES client_instances(id),
    
    -- Metric identification
    metric_name VARCHAR(100) NOT NULL,
    metric_type VARCHAR(50),  -- 'counter', 'gauge', 'histogram'
    
    -- Value
    value_numeric DECIMAL(18,4),
    value_text VARCHAR(255),
    value_json JSONB,
    
    -- Dimensions (for filtering/grouping)
    dimensions JSONB DEFAULT '{}',
    
    -- Time
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    period_start TIMESTAMPTZ,
    period_end TIMESTAMPTZ,
    
    -- Source
    source VARCHAR(100),  -- 'system', 'ai', 'user'
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit Log (WISP compliance)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_instance_id UUID REFERENCES client_instances(id),
    
    -- Actor
    user_id UUID REFERENCES users(id),
    user_email VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    
    -- Action
    action VARCHAR(100) NOT NULL,  -- 'login', 'view', 'create', 'update', 'delete', 'export'
    resource_type VARCHAR(100),  -- 'client', 'message', 'file', etc.
    resource_id UUID,
    
    -- Details
    old_values JSONB,
    new_values JSONB,
    description TEXT,
    
    -- Security
    severity VARCHAR(20) DEFAULT 'info',  -- 'info', 'warning', 'critical'
    is_security_event BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- TAX MODULE TABLES
-- ============================================================================

-- Tax Returns
CREATE TABLE tax_returns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_instance_id UUID REFERENCES client_instances(id),
    client_id UUID REFERENCES clients(id) NOT NULL,
    
    -- Tax year info
    tax_year INTEGER NOT NULL,
    return_type VARCHAR(20) DEFAULT 'individual',  -- 'individual', 'business', 'trust'
    
    -- Status tracking
    status tax_return_status DEFAULT 'not_started',
    status_changed_at TIMESTAMPTZ,
    
    -- Key dates
    organizer_sent_at TIMESTAMPTZ,
    documents_received_at TIMESTAMPTZ,
    preparation_started_at TIMESTAMPTZ,
    review_started_at TIMESTAMPTZ,
    filed_at TIMESTAMPTZ,
    
    -- Filing details
    filing_method VARCHAR(50),  -- 'efile', 'paper'
    confirmation_number VARCHAR(100),
    
    -- Financial summary
    total_income DECIMAL(12,2),
    total_deductions DECIMAL(12,2),
    tax_liability DECIMAL(12,2),
    refund_amount DECIMAL(12,2),
    amount_owed DECIMAL(12,2),
    
    -- Assignment
    preparer_id UUID REFERENCES users(id),
    reviewer_id UUID REFERENCES users(id),
    
    -- Metadata
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ NULL,
    
    -- WISP: 3-year retention
    retention_until DATE,
    
    CONSTRAINT unique_client_tax_year UNIQUE (client_id, tax_year, return_type)
);

-- Tax Organizers
CREATE TABLE tax_organizers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_instance_id UUID REFERENCES client_instances(id),
    client_id UUID REFERENCES clients(id) NOT NULL,
    tax_return_id UUID REFERENCES tax_returns(id),
    
    -- Tax year
    tax_year INTEGER NOT NULL,
    
    -- Template
    template_name VARCHAR(100),
    template_version VARCHAR(20),
    
    -- Status tracking
    status organizer_status DEFAULT 'not_sent',
    
    -- Delivery tracking
    sent_at TIMESTAMPTZ,
    sent_method VARCHAR(50),  -- 'email', 'portal', 'mail'
    sent_to VARCHAR(255),
    
    -- Engagement tracking
    opened_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    -- Reminder tracking
    last_reminder_at TIMESTAMPTZ,
    reminder_count INTEGER DEFAULT 0,
    next_reminder_at TIMESTAMPTZ,
    
    -- Content
    sections JSONB DEFAULT '[]',  -- organizer sections & completion status
    responses JSONB DEFAULT '{}',  -- client's responses
    
    -- Access
    access_token VARCHAR(255),
    access_expires_at TIMESTAMPTZ,
    
    -- Metadata
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ NULL
);

-- Tax Documents
CREATE TABLE tax_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_instance_id UUID REFERENCES client_instances(id),
    tax_return_id UUID REFERENCES tax_returns(id),
    client_id UUID REFERENCES clients(id),
    file_id UUID REFERENCES files(id),
    
    -- Document classification
    document_type VARCHAR(100) NOT NULL,  -- 'w2', '1099', 'receipt', 'prior_return', etc.
    document_subtype VARCHAR(100),
    tax_year INTEGER,
    
    -- Source
    source VARCHAR(50),  -- 'client_upload', 'irs', 'employer', 'generated'
    
    -- Verification
    is_verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMPTZ,
    verified_by UUID REFERENCES users(id),
    
    -- Data extraction
    extracted_data JSONB DEFAULT '{}',  -- AI-extracted fields
    extraction_confidence DECIMAL(3,2),
    
    -- Metadata
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ NULL
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Users
CREATE INDEX idx_users_client_instance ON users(client_instance_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_last_active ON users(last_active_at);
CREATE INDEX idx_users_deleted ON users(deleted_at) WHERE deleted_at IS NULL;

-- Leads
CREATE INDEX idx_leads_client_instance ON leads(client_instance_id);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_source ON leads(source);
CREATE INDEX idx_leads_assigned ON leads(assigned_to);
CREATE INDEX idx_leads_score ON leads(lead_score DESC);
CREATE INDEX idx_leads_created ON leads(created_at DESC);
CREATE INDEX idx_leads_deleted ON leads(deleted_at) WHERE deleted_at IS NULL;

-- Clients
CREATE INDEX idx_clients_client_instance ON clients(client_instance_id);
CREATE INDEX idx_clients_status ON clients(status);
CREATE INDEX idx_clients_retention_risk ON clients(retention_risk_score DESC);
CREATE INDEX idx_clients_next_followup ON clients(next_followup_date);
CREATE INDEX idx_clients_last_service ON clients(last_service_date);
CREATE INDEX idx_clients_deleted ON clients(deleted_at) WHERE deleted_at IS NULL;

-- Messages
CREATE INDEX idx_messages_client_instance ON messages(client_instance_id);
CREATE INDEX idx_messages_thread ON messages(thread_id);
CREATE INDEX idx_messages_client ON messages(client_id);
CREATE INDEX idx_messages_lead ON messages(lead_id);
CREATE INDEX idx_messages_status ON messages(status);
CREATE INDEX idx_messages_category ON messages(category);
CREATE INDEX idx_messages_channel ON messages(channel);
CREATE INDEX idx_messages_received ON messages(received_at DESC);
CREATE INDEX idx_messages_retention ON messages(retention_until);
CREATE INDEX idx_messages_deleted ON messages(deleted_at) WHERE deleted_at IS NULL;

-- Full-text search on messages
CREATE INDEX idx_messages_body_search ON messages USING gin(to_tsvector('english', body));
CREATE INDEX idx_messages_subject_search ON messages USING gin(to_tsvector('english', subject));

-- Files
CREATE INDEX idx_files_client_instance ON files(client_instance_id);
CREATE INDEX idx_files_client ON files(client_id);
CREATE INDEX idx_files_year ON files(year);
CREATE INDEX idx_files_category ON files(category);
CREATE INDEX idx_files_retention ON files(retention_until);
CREATE INDEX idx_files_deleted ON files(deleted_at) WHERE deleted_at IS NULL;

-- Tasks
CREATE INDEX idx_tasks_client_instance ON tasks(client_instance_id);
CREATE INDEX idx_tasks_client ON tasks(client_id);
CREATE INDEX idx_tasks_assigned ON tasks(assigned_to);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due ON tasks(due_date);
CREATE INDEX idx_tasks_type ON tasks(task_type);
CREATE INDEX idx_tasks_deleted ON tasks(deleted_at) WHERE deleted_at IS NULL;

-- Analytics
CREATE INDEX idx_analytics_client_instance ON analytics(client_instance_id);
CREATE INDEX idx_analytics_metric ON analytics(metric_name);
CREATE INDEX idx_analytics_recorded ON analytics(recorded_at DESC);
CREATE INDEX idx_analytics_dimensions ON analytics USING gin(dimensions);

-- Audit Logs
CREATE INDEX idx_audit_client_instance ON audit_logs(client_instance_id);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_security ON audit_logs(is_security_event) WHERE is_security_event = TRUE;

-- Tax Returns
CREATE INDEX idx_tax_returns_client_instance ON tax_returns(client_instance_id);
CREATE INDEX idx_tax_returns_client ON tax_returns(client_id);
CREATE INDEX idx_tax_returns_year ON tax_returns(tax_year);
CREATE INDEX idx_tax_returns_status ON tax_returns(status);
CREATE INDEX idx_tax_returns_preparer ON tax_returns(preparer_id);
CREATE INDEX idx_tax_returns_deleted ON tax_returns(deleted_at) WHERE deleted_at IS NULL;

-- Tax Organizers
CREATE INDEX idx_tax_organizers_client_instance ON tax_organizers(client_instance_id);
CREATE INDEX idx_tax_organizers_client ON tax_organizers(client_id);
CREATE INDEX idx_tax_organizers_year ON tax_organizers(tax_year);
CREATE INDEX idx_tax_organizers_status ON tax_organizers(status);
CREATE INDEX idx_tax_organizers_next_reminder ON tax_organizers(next_reminder_at);
CREATE INDEX idx_tax_organizers_deleted ON tax_organizers(deleted_at) WHERE deleted_at IS NULL;

-- Tax Documents
CREATE INDEX idx_tax_documents_client_instance ON tax_documents(client_instance_id);
CREATE INDEX idx_tax_documents_return ON tax_documents(tax_return_id);
CREATE INDEX idx_tax_documents_client ON tax_documents(client_id);
CREATE INDEX idx_tax_documents_type ON tax_documents(document_type);
CREATE INDEX idx_tax_documents_year ON tax_documents(tax_year);
CREATE INDEX idx_tax_documents_deleted ON tax_documents(deleted_at) WHERE deleted_at IS NULL;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER tr_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER tr_leads_updated_at BEFORE UPDATE ON leads FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER tr_clients_updated_at BEFORE UPDATE ON clients FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER tr_messages_updated_at BEFORE UPDATE ON messages FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER tr_files_updated_at BEFORE UPDATE ON files FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER tr_tasks_updated_at BEFORE UPDATE ON tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER tr_tax_returns_updated_at BEFORE UPDATE ON tax_returns FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER tr_tax_organizers_updated_at BEFORE UPDATE ON tax_organizers FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER tr_tax_documents_updated_at BEFORE UPDATE ON tax_documents FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Active leads with scoring
CREATE VIEW v_active_leads AS
SELECT 
    l.*,
    u.email as assigned_email,
    u.name as assigned_name
FROM leads l
LEFT JOIN users u ON l.assigned_to = u.id
WHERE l.deleted_at IS NULL 
  AND l.status NOT IN ('converted', 'dead');

-- Client retention overview
CREATE VIEW v_client_retention AS
SELECT 
    c.id,
    c.client_instance_id,
    c.contact_name,
    c.email,
    c.status,
    c.client_since,
    c.lifetime_value,
    c.retention_risk_score,
    c.last_interaction_at,
    c.next_followup_date,
    CASE 
        WHEN c.retention_risk_score >= 70 THEN 'high_risk'
        WHEN c.retention_risk_score >= 40 THEN 'medium_risk'
        ELSE 'low_risk'
    END as risk_level,
    DATE_PART('day', NOW() - c.last_interaction_at) as days_since_interaction
FROM clients c
WHERE c.deleted_at IS NULL;

-- Tax return dashboard
CREATE VIEW v_tax_return_dashboard AS
SELECT 
    tr.id,
    tr.client_instance_id,
    tr.tax_year,
    tr.status,
    tr.return_type,
    c.contact_name as client_name,
    c.email as client_email,
    u.name as preparer_name,
    tr.filed_at,
    tr.refund_amount,
    tr.amount_owed,
    CASE 
        WHEN tr.status = 'filed' THEN 'complete'
        WHEN tr.status IN ('review', 'in_progress') THEN 'in_progress'
        ELSE 'pending'
    END as progress_status
FROM tax_returns tr
JOIN clients c ON tr.client_id = c.id
LEFT JOIN users u ON tr.preparer_id = u.id
WHERE tr.deleted_at IS NULL;

-- Organizer tracking
CREATE VIEW v_organizer_tracking AS
SELECT 
    o.id,
    o.client_instance_id,
    o.tax_year,
    o.status,
    c.contact_name as client_name,
    c.email as client_email,
    o.sent_at,
    o.opened_at,
    o.completed_at,
    o.reminder_count,
    o.next_reminder_at,
    CASE 
        WHEN o.status = 'completed' THEN 'done'
        WHEN o.status = 'in_progress' THEN 'working'
        WHEN o.status = 'opened' THEN 'viewed'
        WHEN o.status = 'sent' THEN 'waiting'
        ELSE 'not_sent'
    END as engagement_status
FROM tax_organizers o
JOIN clients c ON o.client_id = c.id
WHERE o.deleted_at IS NULL;

-- Daily digest summary
CREATE VIEW v_daily_digest AS
SELECT 
    m.client_instance_id,
    m.category,
    COUNT(*) as message_count,
    COUNT(*) FILTER (WHERE m.status = 'unread') as unread_count,
    MAX(m.received_at) as latest_message_at
FROM messages m
WHERE m.deleted_at IS NULL
  AND m.received_at >= CURRENT_DATE
GROUP BY m.client_instance_id, m.category;
