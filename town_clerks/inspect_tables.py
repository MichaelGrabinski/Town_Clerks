import os
import django
import sys
from django.db import connections, connection

# Setup
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'town_clerks.settings')
django.setup()

dbs = ['marriage', 'vets', 'transmitel', 'vitals']

sql_query = """
SELECT 
    s.name AS SchemaName,
    t.name AS TableName,
    p.rows AS RowCounts
FROM 
    sys.tables t
INNER JOIN 
    sys.schemas s ON t.schema_id = s.schema_id
INNER JOIN      
    sys.indexes i ON t.OBJECT_ID = i.object_id
INNER JOIN 
    sys.partitions p ON i.object_id = p.OBJECT_ID AND i.index_id = p.index_id
WHERE 
    t.is_ms_shipped = 0
GROUP BY 
    s.name, t.Name, p.Rows
ORDER BY 
    p.Rows DESC;
"""

print(f"{'DATABASE':<15} | {'SCHEMA':<10} | {'TABLE NAME':<30} | {'ROW COUNT':<10}")
print("-" * 75)

for alias in dbs:
    try:
        conn = connections[alias]
        with conn.cursor() as cursor:
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            if not rows:
                print(f"{alias:<15} | {'?':<10} | (No tables found or empty)      | 0")
            for row in rows:
                print(f"{alias:<15} | {row[0]:<10} | {row[1]:<30} | {row[2]:<10}")
    except Exception as e:
        print(f"{alias:<15} | ERROR: {e}")
