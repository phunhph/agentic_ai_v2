ALTER TABLE business_zone.accounts ADD COLUMN IF NOT EXISTS tenant_id TEXT NOT NULL DEFAULT 'default';
ALTER TABLE business_zone.contacts ADD COLUMN IF NOT EXISTS tenant_id TEXT NOT NULL DEFAULT 'default';
ALTER TABLE audit_zone.agent_logs ADD COLUMN IF NOT EXISTS tenant_id TEXT;
ALTER TABLE audit_zone.checkpoints ADD COLUMN IF NOT EXISTS tenant_id TEXT;

DROP VIEW IF EXISTS business_zone.v_hbl_contacts;
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
