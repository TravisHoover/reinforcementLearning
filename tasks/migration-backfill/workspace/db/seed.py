"""Build an in-memory copy of the staging database: migrations 0001-0002 plus data."""

import sqlite3

from db.migrate import migrate

ACCOUNTS = [
    (1, "ops@example.com", "2024-02-01", None),
    (2, "billing@example.com", "2024-05-17", "2025-11-30"),
    (3, "support@example.com", "2025-01-09", None),
]


def staging_snapshot() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    migrate(conn, upto="0002_add_deleted_at")
    conn.executemany(
        "INSERT INTO accounts (id, email, created_at, deleted_at) VALUES (?, ?, ?, ?)", ACCOUNTS
    )
    conn.commit()
    return conn


def empty_database() -> sqlite3.Connection:
    return sqlite3.connect(":memory:")
