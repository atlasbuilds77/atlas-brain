-- ============================================================================
-- MIGRATION 002: Performance Indexes
-- Created: 2026-01-26
-- Description: Add all indexes for common query patterns
-- ============================================================================

BEGIN;

-- Check if already applied
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM schema_migrations WHERE version = '002') THEN
        RAISE EXCEPTION 'Migration 002 already applied';
    END IF;
END $$;

-- Users indexes
CREATE INDEX IF NOT EXISTS idx_users_client_instance ON users(client_instance_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_last_active ON users(last_active_at);
CREATE INDEX IF NOT EXISTS idx_users_deleted ON users(deleted_at) WHERE deleted_at IS NULL;

-- Leads indexes
CREATE INDEX IF NOT EXISTS idx_leads_client_instance ON leads(client_instance_id);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_source ON leads(source);
CREATE INDEX IF NOT EXISTS idx_leads_assigned ON leads(assigned_to);
CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(lead_score DESC);
CREATE INDEX IF NOT EXISTS idx_leads_created ON leads(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_leads_deleted ON leads(deleted_at) WHERE deleted_at IS NULL;

-- Clients indexes
CREATE INDEX IF NOT EXISTS idx_clients_client_instance ON clients(client_instance_id);
CREATE INDEX IF NOT EXISTS idx_clients_status ON clients(status);
CREATE INDEX IF NOT EXISTS idx_clients_retention_risk ON clients(retention_risk_score DESC);
CREATE INDEX IF NOT EXISTS idx_clients_next_followup ON clients(next_followup_date);
CREATE INDEX IF NOT EXISTS idx_clients_deleted ON clients(deleted_at) WHERE deleted_at IS NULL;

-- Messages indexes
CREATE INDEX IF NOT EXISTS idx_messages_client_instance ON messages(client_instance_id);
CREATE INDEX IF NOT EXISTS idx_messages_thread ON messages(thread_id);
CREATE INDEX IF NOT EXISTS idx_messages_client ON messages(client_id);
CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status);
CREATE INDEX IF NOT EXISTS idx_messages_category ON messages(category);
CREATE INDEX IF NOT EXISTS idx_messages_received ON messages(received_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_deleted ON messages(deleted_at) WHERE deleted_at IS NULL;

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_messages_body_search ON messages USING gin(to_tsvector('english', body));
CREATE INDEX IF NOT EXISTS idx_messages_subject_search ON messages USING gin(to_tsvector('english', subject));

-- Files indexes
CREATE INDEX IF NOT EXISTS idx_files_client_instance ON files(client_instance_id);
CREATE INDEX IF NOT EXISTS idx_files_client ON files(client_id);
CREATE INDEX IF NOT EXISTS idx_files_year ON files(year);
CREATE INDEX IF NOT EXISTS idx_files_deleted ON files(deleted_at) WHERE deleted_at IS NULL;

-- Tasks indexes
CREATE INDEX IF NOT EXISTS idx_tasks_client_instance ON tasks(client_instance_id);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned ON tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_due ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_deleted ON tasks(deleted_at) WHERE deleted_at IS NULL;

-- Audit logs indexes
CREATE INDEX IF NOT EXISTS idx_audit_client_instance ON audit_logs(client_instance_id);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_security ON audit_logs(is_security_event) WHERE is_security_event = TRUE;

-- Tax returns indexes
CREATE INDEX IF NOT EXISTS idx_tax_returns_client_instance ON tax_returns(client_instance_id);
CREATE INDEX IF NOT EXISTS idx_tax_returns_client ON tax_returns(client_id);
CREATE INDEX IF NOT EXISTS idx_tax_returns_year ON tax_returns(tax_year);
CREATE INDEX IF NOT EXISTS idx_tax_returns_status ON tax_returns(status);
CREATE INDEX IF NOT EXISTS idx_tax_returns_deleted ON tax_returns(deleted_at) WHERE deleted_at IS NULL;

-- Tax organizers indexes
CREATE INDEX IF NOT EXISTS idx_tax_organizers_client_instance ON tax_organizers(client_instance_id);
CREATE INDEX IF NOT EXISTS idx_tax_organizers_client ON tax_organizers(client_id);
CREATE INDEX IF NOT EXISTS idx_tax_organizers_status ON tax_organizers(status);
CREATE INDEX IF NOT EXISTS idx_tax_organizers_deleted ON tax_organizers(deleted_at) WHERE deleted_at IS NULL;

-- Tax documents indexes
CREATE INDEX IF NOT EXISTS idx_tax_documents_return ON tax_documents(tax_return_id);
CREATE INDEX IF NOT EXISTS idx_tax_documents_type ON tax_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_tax_documents_deleted ON tax_documents(deleted_at) WHERE deleted_at IS NULL;

-- Record migration
INSERT INTO schema_migrations (version, description) 
VALUES ('002', 'Performance indexes for all tables');

COMMIT;
