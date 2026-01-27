-- ============================================================================
-- ROLLBACK 001: Remove Initial Schema
-- WARNING: This will delete all data!
-- ============================================================================

BEGIN;

-- Drop views first
DROP VIEW IF EXISTS v_daily_digest;
DROP VIEW IF EXISTS v_organizer_tracking;
DROP VIEW IF EXISTS v_tax_return_dashboard;
DROP VIEW IF EXISTS v_client_retention;
DROP VIEW IF EXISTS v_active_leads;

-- Drop triggers
DROP TRIGGER IF EXISTS tr_users_updated_at ON users;
DROP TRIGGER IF EXISTS tr_leads_updated_at ON leads;
DROP TRIGGER IF EXISTS tr_clients_updated_at ON clients;
DROP TRIGGER IF EXISTS tr_messages_updated_at ON messages;
DROP TRIGGER IF EXISTS tr_files_updated_at ON files;
DROP TRIGGER IF EXISTS tr_tasks_updated_at ON tasks;
DROP TRIGGER IF EXISTS tr_tax_returns_updated_at ON tax_returns;
DROP TRIGGER IF EXISTS tr_tax_organizers_updated_at ON tax_organizers;
DROP TRIGGER IF EXISTS tr_tax_documents_updated_at ON tax_documents;

DROP FUNCTION IF EXISTS update_updated_at();

-- Drop tax module tables
DROP TABLE IF EXISTS tax_documents CASCADE;
DROP TABLE IF EXISTS tax_organizers CASCADE;
DROP TABLE IF EXISTS tax_returns CASCADE;

-- Drop core tables (reverse dependency order)
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS analytics CASCADE;
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS files CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS clients CASCADE;
DROP TABLE IF EXISTS leads CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS client_instances CASCADE;

-- Drop enums
DROP TYPE IF EXISTS organizer_status;
DROP TYPE IF EXISTS tax_return_status;
DROP TYPE IF EXISTS task_priority;
DROP TYPE IF EXISTS task_status;
DROP TYPE IF EXISTS message_category;
DROP TYPE IF EXISTS message_status;
DROP TYPE IF EXISTS message_channel;
DROP TYPE IF EXISTS client_status;
DROP TYPE IF EXISTS lead_status;
DROP TYPE IF EXISTS user_role;

-- Remove migration record
DELETE FROM schema_migrations WHERE version IN ('001', '002');

COMMIT;
