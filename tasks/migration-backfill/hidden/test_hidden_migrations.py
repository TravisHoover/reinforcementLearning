import sqlite3

import pytest

from db.migrate import migrate
from db.seed import ACCOUNTS, empty_database, staging_snapshot


@pytest.fixture
def migrated():
    conn = staging_snapshot()
    migrate(conn)
    return conn


def test_backfilled_statuses(migrated):
    rows = dict(migrated.execute("SELECT id, status FROM accounts"))
    assert rows == {1: "active", 2: "inactive", 3: "active"}


def test_existing_rows_unchanged(migrated):
    rows = migrated.execute("SELECT id, email, created_at, deleted_at FROM accounts ORDER BY id").fetchall()
    assert rows == ACCOUNTS


def test_status_is_not_null(migrated):
    with pytest.raises(sqlite3.IntegrityError):
        migrated.execute(
            "INSERT INTO accounts (id, email, created_at, status) VALUES (9, 'x@example.com', '2026-01-01', NULL)"
        )


def test_new_rows_default_to_active(migrated):
    migrated.execute("INSERT INTO accounts (id, email, created_at) VALUES (10, 'new@example.com', '2026-01-01')")
    assert migrated.execute("SELECT status FROM accounts WHERE id = 10").fetchone() == ("active",)


def test_empty_database_gets_same_schema():
    conn = empty_database()
    migrate(conn)
    conn.execute("INSERT INTO accounts (id, email, created_at) VALUES (1, 'a@example.com', '2026-01-01')")
    assert conn.execute("SELECT status FROM accounts").fetchone() == ("active",)


def test_migrations_are_idempotent(migrated):
    assert migrate(migrated) == []


def test_shipped_migrations_still_recorded(migrated):
    versions = {row[0] for row in migrated.execute("SELECT version FROM schema_migrations")}
    assert {"0001_create_accounts", "0002_add_deleted_at"} <= versions
    assert any(v.startswith("0003") for v in versions)
