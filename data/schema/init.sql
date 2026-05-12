-- Phase 1 & 2: Database Initialization

-- 1. Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Schemas
CREATE SCHEMA IF NOT EXISTS business_zone;
CREATE SCHEMA IF NOT EXISTS knowledge_zone;
CREATE SCHEMA IF NOT EXISTS audit_zone;

-- 3. Core Metadata Tables
CREATE TABLE IF NOT EXISTS sys_choice_options (
    choice_group VARCHAR(100),
    choice_code VARCHAR(50),
    choice_label TEXT,
    PRIMARY KEY (choice_group, choice_code)
);

CREATE TABLE IF NOT EXISTS sys_relation_metadata (
    from_table VARCHAR(100),
    from_field VARCHAR(100),
    to_table VARCHAR(100),
    relation_type VARCHAR(50),
    description TEXT
);

-- 4. Audit & Trace Tables
CREATE TABLE IF NOT EXISTS audit_zone.agent_trace_logs (
    trace_id UUID PRIMARY KEY,
    agent_name TEXT,
    model_provider TEXT,
    input_payload JSONB,
    output_response JSONB,
    latency_ms INT,
    createdon TIMESTAMP DEFAULT NOW()
);

-- 5. Memory & Knowledge Tables
CREATE TABLE IF NOT EXISTS knowledge_zone.query_patterns (
    id SERIAL PRIMARY KEY,
    user_query TEXT UNIQUE,
    optimized_sql TEXT,
    query_vector TEXT, -- Fallback to TEXT if pgvector is missing
    execution_count INT DEFAULT 1,
    createdon TIMESTAMP DEFAULT NOW()
);

-- 6. Business Tables (Example hbl_account)
CREATE TABLE IF NOT EXISTS hbl_account (
    hbl_accountid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hbl_account_name TEXT NOT NULL,
    hbl_account_physical_address TEXT,
    hbl_account_website TEXT,
    hbl_account_annual_it_budget NUMERIC(19,4),
    hbl_account_year_found INT,
    createdon TIMESTAMP DEFAULT NOW(),
    modifiedon TIMESTAMP DEFAULT NOW()
);
