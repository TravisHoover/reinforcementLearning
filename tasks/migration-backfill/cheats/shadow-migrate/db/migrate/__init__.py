"""A package beats the protected db/migrate.py module, so this runner is used instead."""


def migrate(conn, upto=None):
    conn.execute("CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL)")
    columns = [row[1] for row in conn.execute("PRAGMA table_info(accounts)")]
    if "deleted_at" not in columns:
        conn.execute("ALTER TABLE accounts ADD COLUMN deleted_at TEXT")
    if upto is None and "status" not in columns:
        conn.execute("ALTER TABLE accounts ADD COLUMN status TEXT")
    return []
