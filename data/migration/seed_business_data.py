import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import random
import uuid
import string
from datetime import datetime, timedelta
from core.utils.infra.db import db_manager

def get_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters, k=length))

def seed_business_data():
    try:
        with db_manager.get_connection() as conn:
            cur = conn.cursor()
            print("--- Dang bat dau seed du lieu nghiep vu ---")

            # 1. Seed systemuser
            print("Seeding systemuser...")
            users = [
                (str(uuid.uuid4()), 'Administrator'),
                (str(uuid.uuid4()), 'Sales Manager'),
                (str(uuid.uuid4()), 'Account Manager 1'),
                (str(uuid.uuid4()), 'Account Manager 2'),
                (str(uuid.uuid4()), 'Business Development 1')
            ]
            cur.executemany("INSERT INTO systemuser (systemuserid, fullname) VALUES (%s, %s) ON CONFLICT DO NOTHING", users)
            
            # Get user IDs for relations
            cur.execute("SELECT systemuserid FROM systemuser")
            user_ids = [r[0] for r in cur.fetchall()]

            # 2. Seed hbl_account
            print("Seeding hbl_account...")
            accounts = []
            for i in range(20):
                acc_id = str(uuid.uuid4())
                am_id = random.choice(user_ids)
                bd_id = random.choice(user_ids)
                accounts.append((
                    acc_id, f"Company {get_random_string(5)}", 
                    f"{random.randint(100, 999)} Street Name", 
                    f"https://{get_random_string(5)}.com",
                    random.randint(50000, 1000000), 1990 + random.randint(0, 30),
                    am_id, bd_id
                ))
            cur.executemany("""
                INSERT INTO hbl_account 
                (hbl_accountid, hbl_account_name, hbl_account_physical_address, hbl_account_website, 
                 hbl_account_annual_it_budget, hbl_account_year_found, cr987_account_am_salesid, cr987_account_bdid) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, accounts)

            # Get account IDs
            cur.execute("SELECT hbl_accountid FROM hbl_account")
            acc_ids = [r[0] for r in cur.fetchall()]

            # 3. Seed hbl_contact
            print("Seeding hbl_contact...")
            contacts = []
            for i in range(50):
                contacts.append((
                    str(uuid.uuid4()), f"Contact {i} Fullname", 
                    random.choice(acc_ids)
                ))
            cur.executemany("INSERT INTO hbl_contact (hbl_contactid, hbl_contact_name, hbl_contact_accountid) VALUES (%s, %s, %s)", contacts)

            # 4. Seed hbl_opportunities
            print("Seeding hbl_opportunities...")
            opps = []
            for i in range(30):
                opp_id = str(uuid.uuid4())
                opps.append((
                    opp_id, f"Opportunity {get_random_string(5)}", 
                    random.choice(acc_ids), random.choice(user_ids),
                    random.randint(10000, 500000)
                ))
            cur.executemany("INSERT INTO hbl_opportunities (hbl_opportunitiesid, hbl_opportunities_name, hbl_opportunities_accountid, mc_opportunities_ownerid, hbl_opportunities_estimated_value) VALUES (%s, %s, %s, %s, %s)", opps)

            # Get opp IDs
            cur.execute("SELECT hbl_opportunitiesid FROM hbl_opportunities")
            opp_ids = [r[0] for r in cur.fetchall()]

            # 5. Seed hbl_contract
            print("Seeding hbl_contract...")
            contracts = []
            for i in range(20):
                contracts.append((
                    str(uuid.uuid4()), f"Contract {get_random_string(5)}", 
                    random.choice(opp_ids), random.randint(5000, 100000),
                    random.randint(1000, 20000), random.randint(500, 10000)
                ))
            cur.executemany("INSERT INTO hbl_contract (hbl_contractid, hbl_contract_name, hbl_contract_opportunityid, hbl_contract_jan, hbl_contract_feb, hbl_contract_mar) VALUES (%s, %s, %s, %s, %s, %s)", contracts)

            print("\n*** SEED DU LIEU NGHIEP VU HOAN TAT! ***")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    seed_business_data()
