"""SQLite schema definitions and initialization.
Supports schema versioning, foreign keys, and safe repeated initialization.
"""
SCHEMA_VERSION = 1

CREATE_SQL = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    byte_size INTEGER NOT NULL CHECK (byte_size >= 0),
    indexed_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
CREATE TABLE IF NOT EXISTS terms (
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    term TEXT NOT NULL,
    frequency INTEGER NOT NULL CHECK (frequency > 0),
    PRIMARY KEY (document_id, term)
);
CREATE INDEX IF NOT EXISTS terms_by_term ON terms(term);
"""


def create_schema(conn):
    """Initialize the schema on a connection with autocommit enabled."""
    conn.executescript(CREATE_SQL)
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version == 0:
        conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    elif version != SCHEMA_VERSION:
        raise RuntimeError(f"unsupported catalog schema version: {version}")
