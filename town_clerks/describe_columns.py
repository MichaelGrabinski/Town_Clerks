import os
import django
import sys

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'town_clerks.settings')
django.setup()

from django.db import connections

def describe_table(alias: str, schema: str, table: str):
    sql = """
    SELECT 
        COLUMN_NAME,
        DATA_TYPE,
        IS_NULLABLE,
        CHARACTER_MAXIMUM_LENGTH
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
    ORDER BY ORDINAL_POSITION;
    """

    with connections[alias].cursor() as cur:
        cur.execute(sql, [schema, table])
        rows = cur.fetchall()

    print(f"\n[{alias}] {schema}.{table} columns ({len(rows)}):")
    for (name, dtype, is_null, max_len) in rows:
        ml = "" if max_len is None else str(max_len)
        print(f"- {name:<30} {dtype:<15} null={is_null:<5} len={ml}")


def main():
    describe_table('marriage', 'stg', 'MarriageLicense')
    describe_table('vets', 'stg', 'vet')
    describe_table('transmitel', 'stg', 'Transactions')
    describe_table('vitals', 'stg', 'Deaths')

if __name__ == '__main__':
    main()
