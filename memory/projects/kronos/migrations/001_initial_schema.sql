-- ============================================================================
-- MIGRATION 001: Initial Schema
-- Created: 2026-01-26
-- Description: Create all core and tax module tables
-- Run: psql -d kronos -f 001_initial_schema.sql
-- ============================================================================

BEGIN;

-- Track migrations
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(50) PRIMARY KEY,
    applied_at TIMESTAMPTZ DEFAULT NOW(),
    description TEXT
);

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Run the main schema
\i ../schema.sql

-- Record migration
INSERT INTO schema_migrations (version, description) 
VALUES ('001', 'Initial schema - core tables and tax module');

COMMIT;
