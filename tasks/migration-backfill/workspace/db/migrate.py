"""Apply SQL migrations in order, recording each in schema_migrations."""

import sqlite3
from pathlib import Path

MIGRATIONS = Path(__file__).parent / "migrations"


def applied(conn: sqlite3.Connection) -> set[str]:
    conn.execute("CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY)")
    return {row[0] for row in conn.execute("SELECT version FROM schema_migrations")}


def migrate(conn: sqlite3.Connection, upto: str | None = None) -> list[str]:
    """Apply pending migrations (optionally only those up to and including `upto`)."""
    done = applied(conn)
    ran = []
    for path in sorted(MIGRATIONS.glob("*.sql")):
        version = path.stem
        if version in done:
            continue
        if upto is not None and version > upto:
            break
        conn.executescript(path.read_text())
        conn.execute("INSERT INTO schema_migrations (version) VALUES (?)", (version,))
        conn.commit()
        ran.append(version)
    return ran
