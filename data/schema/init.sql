-- Schema initialization for Agentic AI Phase 1
-- This file creates semantic schema zones, extensions, core tables, and AI-friendly views.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

CREATE SCHEMA IF NOT EXISTS business_zone;
CREATE SCHEMA IF NOT EXISTS knowledge_zone;
CREATE SCHEMA IF NOT EXISTS audit_zone;

CREATE TABLE IF NOT EXISTS business_zone.accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id TEXT NOT NULL DEFAULT 'default',
    account_name TEXT NOT NULL,
    industry TEXT,
    annual_revenue NUMERIC,
    region TEXT,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS business_zone.contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id TEXT NOT NULL DEFAULT 'default',
    account_id UUID REFERENCES business_zone.accounts(id),
    full_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    title TEXT,
    region TEXT,
    last_activity TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS knowledge_zone.agent_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_schema TEXT NOT NULL,
    source_table TEXT NOT NULL,
    source_id UUID NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_zone.agent_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    thread_id TEXT,
    tenant_id TEXT,
    event_type TEXT NOT NULL,
    payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_zone.checkpoints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    thread_id TEXT NOT NULL,
    session_id TEXT,
    tenant_id TEXT,
    checkpoint_data JSONB NOT NULL,
    previous_checkpoint_id UUID,
    state_type TEXT NOT NULL DEFAULT 'checkpoint',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_zone.api_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name TEXT NOT NULL,
    metric_value NUMERIC NOT NULL,
    metric_labels JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE business_zone.accounts ADD COLUMN IF NOT EXISTS tenant_id TEXT NOT NULL DEFAULT 'default';
ALTER TABLE business_zone.contacts ADD COLUMN IF NOT EXISTS tenant_id TEXT NOT NULL DEFAULT 'default';
ALTER TABLE audit_zone.agent_logs ADD COLUMN IF NOT EXISTS tenant_id TEXT;
ALTER TABLE audit_zone.checkpoints ADD COLUMN IF NOT EXISTS tenant_id TEXT;

DROP VIEW IF EXISTS business_zone.v_hbl_accounts;
CREATE VIEW business_zone.v_hbl_accounts AS
SELECT
    tenant_id AS tenant_id,
    id AS account_id,
    account_name AS account_name,
    account_name AS name,
    industry AS industry,
    annual_revenue AS revenue,
    region AS region,
    description AS business_description,
    created_at AS created_at
FROM business_zone.accounts;

DROP VIEW IF EXISTS business_zone.v_hbl_contacts;
CREATE VIEW business_zone.v_hbl_contacts AS
SELECT
    c.tenant_id AS tenant_id,
    c.id AS contact_id,
    c.account_id AS account_id,
    c.full_name AS contact_name,
    c.email AS contact_email,
    c.phone AS contact_phone,
    c.title AS contact_title,
    c.region AS contact_region,
    c.last_activity AS contact_last_activity,
    c.notes AS contact_notes,
    a.account_name AS account_name,
    a.industry AS account_industry,
    a.annual_revenue AS account_revenue
FROM business_zone.contacts c
LEFT JOIN business_zone.accounts a ON c.account_id = a.id;

ALTER TABLE business_zone.accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE business_zone.contacts ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS accounts_tenant_isolation ON business_zone.accounts;
CREATE POLICY accounts_tenant_isolation ON business_zone.accounts
    USING (tenant_id = current_setting('app.tenant_id', true) OR current_setting('app.tenant_id', true) IS NULL);

DROP POLICY IF EXISTS contacts_tenant_isolation ON business_zone.contacts;
CREATE POLICY contacts_tenant_isolation ON business_zone.contacts
    USING (tenant_id = current_setting('app.tenant_id', true) OR current_setting('app.tenant_id', true) IS NULL);
