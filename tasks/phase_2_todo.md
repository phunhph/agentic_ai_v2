# Phase 2 To-Do: Database Migration & Schema Optimization

## 🚀 Priority: Agentic Data Seeding
- [x] Design `agentic_ai` table structure
- [x] Create seeding script `data/migration/seed_data.py`
- [x] Run `python data/migration/seed_data.py` (1000+ random rows)
- [x] Verify data randomness and structure

## Database Schema
- [x] Create systemuser table
- [x] Create hbl_account table
- [x] Create hbl_contact table
- [x] Create hbl_opportunities table
- [x] Create hbl_contract table

## Choice Metadata
- [x] Import toàn bộ 19+ choice groups (sys_choice_options)
- [x] Validate duplicate choice_code
- [x] Create indexes cho lookup performance

## AI-Friendly Views
- [x] Create v_hbl_account
- [x] Create v_hbl_contact
- [x] Create v_hbl_opportunities
- [x] Create v_hbl_contract

## Metadata Layer
- [x] Create sys_relation_metadata
- [x] Import relations từ db.json
- [x] Validate lookup graph

## AI Infrastructure
- [x] Install pgvector (Fallback to TEXT if missing)
- [x] Create embedding tables (knowledge_zone.query_patterns)
- [x] Create vector indexes (HNSW)
- [x] Test semantic search pipeline
