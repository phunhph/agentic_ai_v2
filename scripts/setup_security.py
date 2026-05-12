from core.utils.infra.db import db_manager

def setup_database_security():
    """Thiết lập bảo mật Database (Phase 4) sử dụng db_manager"""
    try:
        print("--- Setting up Database Security (Phase 4) ---")
        # Sử dụng db_manager với mặc định (superuser)
        with db_manager.get_connection() as conn:
            conn.autocommit = True
            cur = conn.cursor()

            # 1. Tạo role agent_user nếu chưa tồn tại
            print("1. Creating role agent_user...")
            cur.execute("SELECT 1 FROM pg_roles WHERE rolname='agent_user'")
            if not cur.fetchone():
                cur.execute("CREATE ROLE agent_user WITH LOGIN PASSWORD 'agent_pass_2026';")
                print("   OK: Role agent_user created.")
            else:
                print("   INFO: Role agent_user already exists.")

            # 2. Thiết lập quyền truy cập Schema
            print("2. Setting up Schema permissions...")
            # public schema
            cur.execute("GRANT USAGE ON SCHEMA public TO agent_user;")
            cur.execute("GRANT SELECT ON ALL TABLES IN SCHEMA public TO agent_user;")
            
            # audit_zone schema
            cur.execute("GRANT USAGE ON SCHEMA audit_zone TO agent_user;")
            cur.execute("GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA audit_zone TO agent_user;")
            
            # 3. Explicitly grant SELECT only
            cur.execute("REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM agent_user;")
            cur.execute("GRANT SELECT ON ALL TABLES IN SCHEMA public TO agent_user;")
            
            # 4. Default Privileges
            cur.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO agent_user;")
            cur.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA audit_zone GRANT SELECT, INSERT ON TABLES TO agent_user;")

            print("\nDATABASE SECURITY SETUP COMPLETED!")
            print("   - Restricted user: agent_user")
            print("   - Capabilities: SELECT only in public, SELECT/INSERT in audit_zone")

    except Exception as e:
        print(f"ERROR setting up security: {e}")

if __name__ == "__main__":
    setup_database_security()
