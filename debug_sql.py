import psycopg2
from psycopg2.extras import RealDictCursor
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

with conn.cursor(cursor_factory=RealDictCursor) as cur:
    # Check if view exists
    cur.execute("SELECT table_name FROM information_schema.views WHERE table_schema = 'business_zone' AND table_name = 'v_hbl_accounts'")
    result = cur.fetchall()
    print('View exists:', len(result) > 0)

    if len(result) > 0:
        # Try the actual SQL
        try:
            cur.execute('SELECT * FROM business_zone.v_hbl_accounts LIMIT 1')
            row = cur.fetchone()
            print('SQL works:', row is not None)
            print('Columns:', list(row.keys()) if row else 'No data')
        except Exception as e:
            print('SQL error:', e)
    else:
        # Check tables instead
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'business_zone'")
        tables = cur.fetchall()
        print('Available tables in business_zone:', [t['table_name'] for t in tables])

conn.close()