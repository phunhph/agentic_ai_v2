import sqlglot

# Test SQL from the trace log
sql = "SELECT * FROM business_zone.v_hbl_accounts"

try:
    parsed = sqlglot.parse_one(sql, read="postgres")
    print(f"Parsed successfully: {parsed}")
    print(f"Key: {parsed.key}")
    print(f"SQL: {parsed.sql(dialect='postgres')}")
except Exception as e:
    print(f"Parsing failed: {e}")

# Test with different SQL
test_sqls = [
    "SELECT * FROM accounts",
    "SELECT * FROM business_zone.accounts",
    "SELECT * FROM \"business_zone\".\"v_hbl_accounts\"",
]

for test_sql in test_sqls:
    try:
        parsed = sqlglot.parse_one(test_sql, read="postgres")
        print(f"✓ {test_sql} -> {parsed.key}")
    except Exception as e:
        print(f"✗ {test_sql} -> {e}")