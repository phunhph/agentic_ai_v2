import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=int(os.getenv('DB_PORT', '5433')),
    dbname=os.getenv('DB_NAME', 'agentic_ai'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', 'sa')
)

with conn.cursor() as cur:
    # Get view definition
    cur.execute("""
    SELECT view_definition
    FROM information_schema.views
    WHERE table_schema = 'business_zone'
    AND table_name = 'v_hbl_contacts'
    """)
    result = cur.fetchone()
    if result:
        print('Contacts view definition:')
        print(result[0])
    else:
        print('Could not find view definition')

conn.close()