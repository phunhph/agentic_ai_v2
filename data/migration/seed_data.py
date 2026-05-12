import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import random
import uuid
import string
from datetime import datetime, timedelta
import json
from core.utils.db import db_manager
from psycopg2.extras import execute_values

INDUSTRIES = ["Finance", "Technology", "Healthcare", "Education", "Retail", "Manufacturing", "Energy"]
COUNTRIES = ["Vietnam", "USA", "Singapore", "Japan", "Germany", "UK", "France"]
STATUSES = ["Active", "Lead", "Customer", "Churned", "Partner"]

def get_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

def seed_agentic_ai_table(num_rows=1000):
    try:
        with db_manager.get_connection() as conn:
            cur = conn.cursor()

            # 1. Khoi tao Extension va tao bang agentic_ai
            print("--- Dang cau hinh Database va tao bang agentic_ai ---")
            cur.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS agentic_ai (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    customer_name TEXT NOT NULL,
                    industry TEXT,
                    annual_revenue NUMERIC(19,4),
                    employee_count INT,
                    country TEXT,
                    contact_email TEXT,
                    status TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    last_interaction TIMESTAMP,
                    created_at TIMESTAMP DEFAULT NOW(),
                    meta_data JSONB
                );
            """)

            # 2. Sinh du lieu ngau nhien
            print(f"--- Dang sinh {num_rows} dong du lieu ngau nhien ---")
            
            data = []
            for _ in range(num_rows):
                name = f"{get_random_string(5).capitalize()} {random.choice(['Group', 'Corp', 'Solutions', 'Global', 'Inc'])}"
                industry = random.choice(INDUSTRIES)
                revenue = round(random.uniform(10000, 10000000), 2)
                employees = random.randint(10, 5000)
                country = random.choice(COUNTRIES)
                email = f"contact@{name.lower().replace(' ', '')}.com"
                status = random.choice(STATUSES)
                active = random.random() > 0.1
                interaction = datetime.now() - timedelta(days=random.randint(0, 365))
                
                meta = {
                    "source": random.choice(["LinkedIn", "Referral", "Website", "Event"]),
                    "priority": random.choice(["High", "Medium", "Low"]),
                    "notes": get_random_string(20)
                }

                data.append((
                    str(uuid.uuid4()), name, industry, revenue, employees, 
                    country, email, status, active, interaction, 
                    json.dumps(meta)
                ))

            # 3. Chen du lieu
            print("--- Dang chen du lieu vao Database ---")
            insert_query = """
                INSERT INTO agentic_ai 
                (id, customer_name, industry, annual_revenue, employee_count, country, contact_email, status, is_active, last_interaction, meta_data)
                VALUES %s
            """
            execute_values(cur, insert_query, data)
            
            print(f"OK: Hoan thanh! Da tao bang va chen {num_rows} dong du lieu thanh cong.")

    except Exception as e:
        print(f"ERROR: Loi: {e}")

if __name__ == "__main__":
    seed_agentic_ai_table(1000)
