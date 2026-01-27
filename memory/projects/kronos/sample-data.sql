-- ============================================================================
-- KRONOS SAMPLE DATA
-- For development and testing
-- ============================================================================

BEGIN;

-- ============================================================================
-- CLIENT INSTANCE (Laura's Tax Practice)
-- ============================================================================

INSERT INTO client_instances (id, name, slug, industry, settings, branding) VALUES
('11111111-1111-1111-1111-111111111111', 
 'Laura''s Tax Practice', 
 'laura-tax', 
 'tax',
 '{"timezone": "America/Los_Angeles", "busy_season_start": "02-01", "busy_season_end": "04-15"}',
 '{"primary_color": "#2563eb", "logo_url": null}');

-- ============================================================================
-- USERS
-- ============================================================================

-- Laura (Admin)
INSERT INTO users (id, client_instance_id, email, name, phone, role, is_active, email_verified) VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
 '11111111-1111-1111-1111-111111111111',
 'laura@taxprep.example.com',
 'Laura Johnson',
 '555-0100',
 'admin',
 true,
 true);

-- Staff member
INSERT INTO users (id, client_instance_id, email, name, phone, role, is_active) VALUES
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
 '11111111-1111-1111-1111-111111111111',
 'assistant@taxprep.example.com',
 'Tax Assistant',
 '555-0101',
 'staff',
 true);

-- ============================================================================
-- LEADS (Various stages)
-- ============================================================================

-- New lead (just came in)
INSERT INTO leads (id, client_instance_id, name, email, phone, source, source_detail, status, lead_score) VALUES
('11111111-0001-0000-0000-000000000001',
 '11111111-1111-1111-1111-111111111111',
 'John Smith',
 'john.smith@email.com',
 '555-1001',
 'website',
 'Contact form - Tax Services page',
 'new',
 0);

-- Qualified lead (good prospect)
INSERT INTO leads (id, client_instance_id, name, email, phone, source, status, lead_score, qualification_answers, qualified_at) VALUES
('11111111-0001-0000-0000-000000000002',
 '11111111-1111-1111-1111-111111111111',
 'Sarah Williams',
 'sarah.w@email.com',
 '555-1002',
 'referral',
 'qualified',
 85,
 '{"needs": "personal + small business", "timeline": "asap", "prior_preparer": "yes", "budget_sensitive": false}',
 NOW() - interval '2 days');

-- Price shopper (flagged)
INSERT INTO leads (id, client_instance_id, name, email, phone, source, status, lead_score, is_price_shopper, qualification_answers) VALUES
('11111111-0001-0000-0000-000000000003',
 '11111111-1111-1111-1111-111111111111',
 'Mike Price',
 'cheapest@email.com',
 '555-1003',
 'google',
 'contacted',
 25,
 true,
 '{"first_question": "How much do you charge?", "comparing": "3 other preparers", "budget_sensitive": true}');

-- Dead lead
INSERT INTO leads (id, client_instance_id, name, email, source, status, lead_score, notes) VALUES
('11111111-0001-0000-0000-000000000004',
 '11111111-1111-1111-1111-111111111111',
 'No Response Nancy',
 'ghost@email.com',
 'flyer',
 'dead',
 0,
 'No response after 3 follow-ups');

-- ============================================================================
-- CLIENTS (Active relationships)
-- ============================================================================

-- Long-term client
INSERT INTO clients (id, client_instance_id, lead_id, contact_name, email, phone, status, client_since, lifetime_value, annual_value, retention_risk_score, last_interaction_at, tags) VALUES
('22222222-0001-0000-0000-000000000001',
 '11111111-1111-1111-1111-111111111111',
 NULL,
 'Robert Chen',
 'robert.chen@email.com',
 '555-2001',
 'active',
 '2020-01-15',
 2500.00,
 500.00,
 10,
 NOW() - interval '5 days',
 ARRAY['vip', 'business-owner']);

-- Medium-term client
INSERT INTO clients (id, client_instance_id, contact_name, email, phone, status, client_since, lifetime_value, annual_value, retention_risk_score, last_interaction_at) VALUES
('22222222-0001-0000-0000-000000000002',
 '11111111-1111-1111-1111-111111111111',
 'Emily Davis',
 'emily.d@email.com',
 '555-2002',
 'active',
 '2023-02-01',
 750.00,
 250.00,
 25,
 NOW() - interval '30 days');

-- At-risk client (hasn't returned)
INSERT INTO clients (id, client_instance_id, contact_name, email, phone, status, client_since, lifetime_value, retention_risk_score, risk_factors, last_interaction_at, last_service_date) VALUES
('22222222-0001-0000-0000-000000000003',
 '11111111-1111-1111-1111-111111111111',
 'David Wilson',
 'david.wilson@email.com',
 '555-2003',
 'active',
 '2022-03-01',
 500.00,
 75,
 '{"missed_last_year": true, "complained_about_price": true, "slow_document_provider": true}',
 NOW() - interval '400 days',
 '2023-04-10');

-- New client (just converted)
INSERT INTO clients (id, client_instance_id, lead_id, contact_name, email, phone, status, client_since, lifetime_value, retention_risk_score, last_interaction_at) VALUES
('22222222-0001-0000-0000-000000000004',
 '11111111-1111-1111-1111-111111111111',
 '11111111-0001-0000-0000-000000000002',
 'Sarah Williams',
 'sarah.w@email.com',
 '555-1002',
 'active',
 CURRENT_DATE,
 0.00,
 15,
 NOW());

-- Update lead as converted
UPDATE leads SET 
    status = 'converted',
    converted_at = NOW(),
    converted_to_client_id = '22222222-0001-0000-0000-000000000004'
WHERE id = '11111111-0001-0000-0000-000000000002';

-- ============================================================================
-- MESSAGES (Various categories)
-- ============================================================================

-- Prospective inquiry
INSERT INTO messages (id, client_instance_id, lead_id, from_address, channel, subject, body, category, category_confidence, status, received_at, retention_until) VALUES
('33333333-0001-0000-0000-000000000001',
 '11111111-1111-1111-1111-111111111111',
 '11111111-0001-0000-0000-000000000001',
 'john.smith@email.com',
 'email',
 'Tax Preparation Inquiry',
 'Hi, I found your website and I''m looking for someone to help with my taxes this year. I have a W-2 and some investment income. Can you tell me about your services?',
 'prospective',
 0.95,
 'unread',
 NOW() - interval '2 hours',
 CURRENT_DATE + interval '3 years');

-- Client document submission
INSERT INTO messages (id, client_instance_id, client_id, from_address, channel, subject, body, category, category_confidence, status, received_at, attachment_count, retention_until) VALUES
('33333333-0001-0000-0000-000000000002',
 '11111111-1111-1111-1111-111111111111',
 '22222222-0001-0000-0000-000000000001',
 'robert.chen@email.com',
 'email',
 'RE: 2025 Tax Documents',
 'Hi Laura, attached are my W-2 and 1099 forms for this year. Let me know if you need anything else.',
 'client',
 0.98,
 'read',
 NOW() - interval '1 day',
 2,
 CURRENT_DATE + interval '3 years');

-- Office/admin message
INSERT INTO messages (id, client_instance_id, from_address, channel, subject, body, category, category_confidence, status, received_at) VALUES
('33333333-0001-0000-0000-000000000003',
 '11111111-1111-1111-1111-111111111111',
 'supplies@officestore.com',
 'email',
 'Your order has shipped',
 'Your recent order of printer paper has shipped and will arrive Thursday.',
 'office',
 0.92,
 'read',
 NOW() - interval '3 days');

-- Spam
INSERT INTO messages (id, client_instance_id, from_address, channel, subject, body, category, category_confidence, status, received_at) VALUES
('33333333-0001-0000-0000-000000000004',
 '11111111-1111-1111-1111-111111111111',
 'amazing-deal@spam.net',
 'email',
 'URGENT: You''ve won $1,000,000!!!',
 'Click here to claim your prize...',
 'spam',
 0.99,
 'archived',
 NOW() - interval '5 days');

-- ============================================================================
-- TAX RETURNS (Various statuses)
-- ============================================================================

-- Filed return from last year
INSERT INTO tax_returns (id, client_instance_id, client_id, tax_year, return_type, status, filed_at, refund_amount, preparer_id, retention_until) VALUES
('44444444-0001-0000-0000-000000000001',
 '11111111-1111-1111-1111-111111111111',
 '22222222-0001-0000-0000-000000000001',
 2024,
 'individual',
 'filed',
 '2025-03-15',
 1250.00,
 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
 '2032-03-15');

-- Current year - in progress
INSERT INTO tax_returns (id, client_instance_id, client_id, tax_year, return_type, status, organizer_sent_at, documents_received_at, preparer_id) VALUES
('44444444-0001-0000-0000-000000000002',
 '11111111-1111-1111-1111-111111111111',
 '22222222-0001-0000-0000-000000000001',
 2025,
 'individual',
 'docs_received',
 '2026-01-10',
 '2026-01-24',
 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa');

-- Current year - not started
INSERT INTO tax_returns (id, client_instance_id, client_id, tax_year, return_type, status) VALUES
('44444444-0001-0000-0000-000000000003',
 '11111111-1111-1111-1111-111111111111',
 '22222222-0001-0000-0000-000000000002',
 2025,
 'individual',
 'not_started');

-- ============================================================================
-- TAX ORGANIZERS (Various statuses)
-- ============================================================================

-- Completed organizer
INSERT INTO tax_organizers (id, client_instance_id, client_id, tax_return_id, tax_year, status, sent_at, opened_at, completed_at, template_name) VALUES
('55555555-0001-0000-0000-000000000001',
 '11111111-1111-1111-1111-111111111111',
 '22222222-0001-0000-0000-000000000001',
 '44444444-0001-0000-0000-000000000002',
 2025,
 'completed',
 '2026-01-10',
 '2026-01-10',
 '2026-01-12',
 'Individual Tax Organizer 2025');

-- Sent but not opened
INSERT INTO tax_organizers (id, client_instance_id, client_id, tax_return_id, tax_year, status, sent_at, sent_method, reminder_count, next_reminder_at, template_name) VALUES
('55555555-0001-0000-0000-000000000002',
 '11111111-1111-1111-1111-111111111111',
 '22222222-0001-0000-0000-000000000002',
 '44444444-0001-0000-0000-000000000003',
 2025,
 'sent',
 '2026-01-15',
 'email',
 1,
 NOW() + interval '3 days',
 'Individual Tax Organizer 2025');

-- Not yet sent
INSERT INTO tax_organizers (id, client_instance_id, client_id, tax_year, status, template_name) VALUES
('55555555-0001-0000-0000-000000000003',
 '11111111-1111-1111-1111-111111111111',
 '22222222-0001-0000-0000-000000000004',
 2025,
 'not_sent',
 'Individual Tax Organizer 2025');

-- ============================================================================
-- TASKS
-- ============================================================================

-- Follow-up task
INSERT INTO tasks (id, client_instance_id, client_id, assigned_to, created_by, title, description, task_type, status, priority, due_date) VALUES
('66666666-0001-0000-0000-000000000001',
 '11111111-1111-1111-1111-111111111111',
 '22222222-0001-0000-0000-000000000003',
 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
 'Win-back call: David Wilson',
 'Client hasn''t filed in 2 years. Call to re-engage.',
 'followup',
 'pending',
 'high',
 CURRENT_DATE + interval '2 days');

-- Document request
INSERT INTO tasks (id, client_instance_id, client_id, assigned_to, title, task_type, status, priority, due_date) VALUES
('66666666-0001-0000-0000-000000000002',
 '11111111-1111-1111-1111-111111111111',
 '22222222-0001-0000-0000-000000000002',
 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
 'Request missing W-2 from Emily',
 'document_request',
 'pending',
 'medium',
 CURRENT_DATE + interval '5 days');

-- Lead follow-up
INSERT INTO tasks (id, client_instance_id, lead_id, assigned_to, title, task_type, status, priority, due_date) VALUES
('66666666-0001-0000-0000-000000000003',
 '11111111-1111-1111-1111-111111111111',
 '11111111-0001-0000-0000-000000000001',
 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
 'Reply to new lead: John Smith',
 'followup',
 'pending',
 'urgent',
 CURRENT_DATE);

-- ============================================================================
-- ANALYTICS (Sample metrics)
-- ============================================================================

INSERT INTO analytics (client_instance_id, metric_name, metric_type, value_numeric, dimensions, recorded_at) VALUES
('11111111-1111-1111-1111-111111111111', 'leads_created', 'counter', 4, '{"source": "all"}', NOW()),
('11111111-1111-1111-1111-111111111111', 'leads_converted', 'counter', 1, '{"source": "referral"}', NOW()),
('11111111-1111-1111-1111-111111111111', 'conversion_rate', 'gauge', 25.0, '{}', NOW()),
('11111111-1111-1111-1111-111111111111', 'avg_lead_score', 'gauge', 45.0, '{}', NOW()),
('11111111-1111-1111-1111-111111111111', 'active_clients', 'gauge', 4, '{}', NOW()),
('11111111-1111-1111-1111-111111111111', 'at_risk_clients', 'gauge', 1, '{}', NOW()),
('11111111-1111-1111-1111-111111111111', 'organizers_sent', 'counter', 2, '{"year": 2025}', NOW()),
('11111111-1111-1111-1111-111111111111', 'organizers_completed', 'counter', 1, '{"year": 2025}', NOW());

-- ============================================================================
-- AUDIT LOG SAMPLES
-- ============================================================================

INSERT INTO audit_logs (client_instance_id, user_id, user_email, action, resource_type, resource_id, description, ip_address) VALUES
('11111111-1111-1111-1111-111111111111', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'laura@taxprep.example.com', 'login', 'session', NULL, 'User logged in', '192.168.1.1'),
('11111111-1111-1111-1111-111111111111', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'laura@taxprep.example.com', 'view', 'client', '22222222-0001-0000-0000-000000000001', 'Viewed client profile', '192.168.1.1'),
('11111111-1111-1111-1111-111111111111', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'laura@taxprep.example.com', 'create', 'tax_organizer', '55555555-0001-0000-0000-000000000001', 'Created tax organizer', '192.168.1.1');

COMMIT;

-- ============================================================================
-- VERIFY SAMPLE DATA
-- ============================================================================

-- Run these to verify:
-- SELECT COUNT(*) as leads FROM leads;
-- SELECT COUNT(*) as clients FROM clients;
-- SELECT COUNT(*) as messages FROM messages;
-- SELECT COUNT(*) as tax_returns FROM tax_returns;
-- SELECT COUNT(*) as organizers FROM tax_organizers;
-- SELECT * FROM v_organizer_tracking;
-- SELECT * FROM v_client_retention;
