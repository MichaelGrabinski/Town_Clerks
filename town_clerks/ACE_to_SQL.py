import os
import json
import pyodbc
from datetime import datetime
from tkinter import Tk, filedialog
from tqdm import tqdm

# ----------------------------
# CONFIG (SQL only)
# ----------------------------
SQL_SERVER = r"TOEHSQL1"   # e.g. r"TOEHSQL1" or r"TOEHSQL1\SQL2019"
SQL_DATABASE = "DeathVitals"
SQL_SCHEMA = "stg"
BATCH_SIZE = 2000

SQL_CONN_STR = (
    "Driver={ODBC Driver 18 for SQL Server};"
    f"Server={SQL_SERVER};"
    f"Database={SQL_DATABASE};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

# ----------------------------
# UI: pick Access file
# ----------------------------
def pick_access_file() -> str:
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    path = filedialog.askopenfilename(
        title="Select Access database (.accdb or .mdb)",
        filetypes=[("Access Databases", "*.accdb *.mdb"), ("All files", "*.*")]
    )
    root.destroy()

    if not path:
        raise SystemExit("No file selected. Exiting.")
    if not os.path.isfile(path):
        raise SystemExit(f"File not found: {path}")
    return os.path.abspath(path)

def make_access_conn_str(access_path: str) -> str:
    return (
        r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
        f"DBQ={access_path};"
    )

# ----------------------------
# Helpers
# ----------------------------
def qname(schema: str, name: str) -> str:
    return f"[{schema}].[{name.replace(']', ']]')}]"

def colname(name: str) -> str:
    return f"[{name.replace(']', ']]')}]"

def ensure_schema(sql_cur, schema: str):
    safe = schema.replace("]", "]]")
    sql_cur.execute(f"""
    IF SCHEMA_ID(N'{safe}') IS NULL
        EXEC(N'CREATE SCHEMA [{safe}]');
    """)

def ensure_error_table(sql_cur, schema: str):
    safe = schema.replace("]", "]]")
    sql_cur.execute(f"""
    IF OBJECT_ID(N'{safe}.stg_load_errors', 'U') IS NULL
    BEGIN
        CREATE TABLE {qname(schema, "stg_load_errors")} (
            error_id        bigint IDENTITY(1,1) PRIMARY KEY,
            table_name      sysname NULL,
            error_time      datetime2(0) NOT NULL DEFAULT SYSUTCDATETIME(),
            error_message   nvarchar(4000) NULL,
            row_json        nvarchar(max) NULL
        );
    END
    """)

def get_access_tables(acc_cur):
    tables = []
    for row in acc_cur.tables(tableType="TABLE"):
        t = row.table_name
        if t.startswith("MSys"):
            continue
        tables.append(t)
    return tables

def get_access_columns(acc_cur, table: str):
    cols = []
    for row in acc_cur.columns(table=table):
        cols.append(row.column_name)
    return cols

def drop_and_create_staging_table(sql_cur, schema: str, table: str, cols):
    full = qname(schema, table)
    safe_schema = schema.replace("]", "]]")
    safe_table = table.replace("]", "]]")
    sql_cur.execute(f"IF OBJECT_ID(N'{safe_schema}.{safe_table}', 'U') IS NOT NULL DROP TABLE {full};")

    col_defs = ",\n".join([f"{colname(c)} nvarchar(max) NULL" for c in cols])
    sql_cur.execute(f"CREATE TABLE {full} (\n{col_defs}\n);")

def fetch_access_rows(acc_cur, table: str, cols):
    select_cols = ", ".join([f"[{c}]" for c in cols])
    acc_cur.execute(f"SELECT {select_cols} FROM [{table}]")
    while True:
        rows = acc_cur.fetchmany(BATCH_SIZE)
        if not rows:
            break
        yield rows

def to_safe_str(v):
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.isoformat(sep=" ")
    return str(v)

def insert_rows(sql_cur, schema: str, table: str, cols, rows):
    full = qname(schema, table)
    placeholders = ", ".join(["?"] * len(cols))
    col_list = ", ".join([colname(c) for c in cols])
    sql = f"INSERT INTO {full} ({col_list}) VALUES ({placeholders})"

    sql_cur.fast_executemany = True
    params = [tuple(to_safe_str(v) for v in r) for r in rows]
    sql_cur.executemany(sql, params)

def log_bad_batch(sql_cur, schema: str, table: str, err: Exception, rows, cols):
    # Log a sample of the failing batch
    def row_to_dict(r):
        d = {}
        for c, v in zip(cols, r):
            d[c] = to_safe_str(v)
        return d

    msg = str(err)[:4000]
    sample = rows[:20]
    payload = json.dumps([row_to_dict(r) for r in sample], ensure_ascii=False)

    sql_cur.execute(
        f"INSERT INTO {qname(schema,'stg_load_errors')} (table_name, error_message, row_json) VALUES (?,?,?)",
        (table, msg, payload)
    )

# ----------------------------
# MAIN
# ----------------------------
def main():
    access_path = pick_access_file()
    print(f"Using Access DB: {access_path}")

    access_conn_str = make_access_conn_str(access_path)

    # Connect
    acc = pyodbc.connect(access_conn_str, autocommit=True)
    sql = pyodbc.connect(SQL_CONN_STR, autocommit=False)

    acc_cur = acc.cursor()
    sql_cur = sql.cursor()

    ensure_schema(sql_cur, SQL_SCHEMA)
    ensure_error_table(sql_cur, SQL_SCHEMA)
    sql.commit()

    tables = get_access_tables(acc_cur)
    print(f"Found {len(tables)} Access tables.")

    for t in tables:
        cols = get_access_columns(acc_cur, t)
        if not cols:
            print(f"Skipping {t} (no columns).")
            continue

        print(f"\n=== {t} ===")
        drop_and_create_staging_table(sql_cur, SQL_SCHEMA, t, cols)
        sql.commit()

        # Optional rowcount for progress bar
        try:
            acc_cur.execute(f"SELECT COUNT(*) FROM [{t}]")
            total = acc_cur.fetchone()[0]
        except Exception:
            total = None

        pbar = tqdm(total=total, unit="rows", disable=(total is None))
        loaded = 0

        for batch in fetch_access_rows(acc_cur, t, cols):
            try:
                insert_rows(sql_cur, SQL_SCHEMA, t, cols, batch)
                sql.commit()
                loaded += len(batch)
                if total is not None:
                    pbar.update(len(batch))
            except Exception as e:
                sql.rollback()
                log_bad_batch(sql_cur, SQL_SCHEMA, t, e, batch, cols)
                sql.commit()
                # keep going

        if total is not None:
            pbar.close()

        print(f"Loaded {loaded} rows into {SQL_SCHEMA}.{t}")

    sql_cur.close()
    acc_cur.close()
    sql.close()
    acc.close()
    print("\nDone. Check stg.stg_load_errors for any rejected batches.")

if __name__ == "__main__":
    main()
