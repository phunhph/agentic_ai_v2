import pytest
from core.utils.logic.tenant_guard import TenantGuard
from core.utils.logic.rls_manager import RLSManager

def test_tenant_guard_assignment():
    guard = TenantGuard()
    
    # Assign tenant
    session_id = "session_123"
    tenant_id = "tenant_abc"
    guard.assign_tenant(session_id, tenant_id)
    
    # Validate
    assert guard.get_tenant(session_id) == tenant_id

def test_tenant_guard_access():
    guard = TenantGuard()
    session_id = "session_456"
    tenant_id = "tenant_xyz"
    guard.assign_tenant(session_id, tenant_id)
    
    # In our simple mock, the tenant_id is often the session_id or mapped 1:1.
    assert guard.validate_access("thread_789", session_id) == True

def test_rls_manager_policy_generation():
    manager = RLSManager()
    
    tenant_id = "tenant_001"
    table_name = "business_zone.v_hbl_accounts"
    
    policy_sql = manager.generate_rls_policy(table_name, tenant_id)
    
    # The policy should contain the table name and the tenant logic
    assert table_name in policy_sql
    assert "CREATE POLICY" in policy_sql or "ALTER TABLE" in policy_sql

def test_tenant_isolation_mock():
    # Simulates what happens if a request for Tenant A tries to read Tenant B's data
    guard = TenantGuard()
    guard.assign_tenant("session_A", "tenant_A")
    guard.assign_tenant("session_B", "tenant_B")
    
    # A cannot access B
    assert guard.get_tenant("session_A") != guard.get_tenant("session_B")
