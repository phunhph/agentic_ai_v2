import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
import os
from core.utils.infra.db import db_manager
from psycopg2.extras import execute_values

TYPE_MAP = {
    "uuid": "UUID",
    "text": "TEXT",
    "datetime": "TIMESTAMP",
    "decimal": "NUMERIC(19,4)",
    "int": "INT",
    "richtext": "TEXT"
}

def migrate_metadata():
    try:
        with open("plans/db.json", "r", encoding="utf-8") as f:
            db_data = json.load(f)

        with db_manager.get_connection() as conn:
            cur = conn.cursor()
            
            # 0. Kich hoat UUID extension
            cur.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")

            # 1. Tao cac bang tu "tables"
            print("--- Dang tao cac bang nghiep vu tu db.json ---")
            for table in db_data["tables"]:
                table_name = table["name"]
                fields = []
                for field in table["fields"]:
                    f_name = field["name"]
                    f_type = TYPE_MAP.get(field["type"], "TEXT")
                    f_null = "" if field.get("nullable", True) else "NOT NULL"
                    f_pk = "PRIMARY KEY" if f_name == table["primary_key"] else ""
                    fields.append(f"{f_name} {f_type} {f_null} {f_pk}")
                
                # Drop existing table to ensure schema sync (Phase 13 fix)
                cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
                create_sql = f"CREATE TABLE {table_name} ({', '.join(fields)});"
                cur.execute(create_sql)
                print(f"OK: Da tao/dong bo bang: {table_name}")

            # 2. Import Choice Options vao sys_choice_options
            print("--- Dang import Choice Options ---")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sys_choice_options (
                    choice_group TEXT,
                    choice_code TEXT,
                    choice_label TEXT,
                    PRIMARY KEY (choice_group, choice_code)
                );
            """)
            cur.execute("TRUNCATE TABLE sys_choice_options;")
            choice_data = []
            for group, options in db_data["choice_options"].items():
                for opt in options:
                    choice_data.append((group, opt["code"], opt["label"]))
            
            execute_values(cur, """
                INSERT INTO sys_choice_options (choice_group, choice_code, choice_label)
                VALUES %s
            """, choice_data)

            # 3. Import Relations vao sys_relation_metadata
            print("--- Dang import Relation Metadata ---")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sys_relation_metadata (
                    from_table TEXT,
                    from_field TEXT,
                    to_table TEXT,
                    relation_type TEXT,
                    description TEXT
                );
            """)
            cur.execute("TRUNCATE TABLE sys_relation_metadata;")
            relation_data = []
            for rel in db_data["relations"]["lookup"]:
                relation_data.append((
                    rel["from_table"], rel["from_field"], 
                    rel["to_table"], "lookup", 
                    f"Lookup from {rel['from_table']} to {rel['to_table']}"
                ))
            
            execute_values(cur, """
                INSERT INTO sys_relation_metadata (from_table, from_field, to_table, relation_type, description)
                VALUES %s
            """, relation_data)

            # 4. Tao cac Mapping Table cho Choice
            print("--- Dang tao cac bang Mapping cho Choice ---")
            for rel in db_data["relations"]["choice"]:
                map_table = rel["join_table"]
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {map_table} (
                        {rel['left_fk']} UUID,
                        {rel['right_fk']} UUID,
                        PRIMARY KEY ({rel['left_fk']}, {rel['right_fk']})
                    );
                """)

            # 5. Tao AI-Friendly Views
            print("--- Dang tao cac AI-Friendly Views ---")
            views = {
                "v_hbl_account": "SELECT h.*, u1.fullname as am_name, u2.fullname as bd_name FROM hbl_account h LEFT JOIN systemuser u1 ON h.cr987_account_am_salesid = u1.systemuserid LEFT JOIN systemuser u2 ON h.cr987_account_bdid = u2.systemuserid",
                "v_hbl_contact": "SELECT c.*, a.hbl_account_name FROM hbl_contact c LEFT JOIN hbl_account a ON c.hbl_contact_accountid = a.hbl_accountid",
                "v_hbl_opportunities": "SELECT o.*, a.hbl_account_name, u.fullname as owner_name FROM hbl_opportunities o LEFT JOIN hbl_account a ON o.hbl_opportunities_accountid = a.hbl_accountid LEFT JOIN systemuser u ON o.mc_opportunities_ownerid = u.systemuserid",
                "v_hbl_contract": "SELECT c.*, o.hbl_opportunities_name FROM hbl_contract c LEFT JOIN hbl_opportunities o ON c.hbl_contract_opportunityid = o.hbl_opportunitiesid"
            }
            for view_name, view_sql in views.items():
                cur.execute(f"DROP VIEW IF EXISTS {view_name} CASCADE;")
                cur.execute(f"CREATE OR REPLACE VIEW {view_name} AS {view_sql};")
                print(f"OK: Da tao View: {view_name}")

            print("\n*** QUA TRINH DI CHUYEN METADATA HOAN TAT! ***")

    except Exception as e:
        print(f"ERROR: Loi: {e}")

if __name__ == "__main__":
    migrate_metadata()
