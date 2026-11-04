from db.migrate import migrate
from db.seed import empty_database, staging_snapshot


def columns(conn):
    return [row[1] for row in conn.execute("PRAGMA table_info(accounts)")]


def test_migrates_staging_snapshot():
    conn = staging_snapshot()
    migrate(conn)
    assert "status" in columns(conn)


def test_migrates_empty_database():
    conn = empty_database()
    migrate(conn)
    assert "status" in columns(conn)
