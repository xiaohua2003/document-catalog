"""SQLite database operations for the document catalog.
Handles document storage and search using transactions,
with relative paths as document identifiers.
"""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from .schema import create_schema
from .tokenize import frequencies, normalize_query
from .errors import StorageError


class Catalog:
    def __init__(self, database: str | Path):
        self.database = Path(database).expanduser()

    @contextmanager
    def connect(self):
        try:
            conn = sqlite3.connect(self.database)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
        except sqlite3.Error as exc:
            raise StorageError(f"cannot open catalog: {exc}") from exc
        try:
            yield conn
        finally:
            conn.close()

    def initialize(self):
        self.database.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            create_schema(conn)

    def contains(self, path: str) -> bool:
        with self.connect() as conn:
            row = conn.execute("SELECT 1 FROM documents WHERE path = ?", (path,)).fetchone()
            return row is not None

    def add_if_missing(self, document) -> bool:
        """Insert a new document and its search terms if document not exist.
        If a document with the same path already exists, leave its
        stored content and search terms unchanged.
        """
        with self.connect() as conn:
            try:
                with conn:
                    cur = conn.execute(
                        "INSERT OR IGNORE INTO documents(path,title,body,sha256,byte_size) "
                        "VALUES (?,?,?,?,?)",
                        (document.key, document.title, document.body,
                         document.sha256, document.byte_size),
                    )
                    if cur.rowcount == 0:
                        return False
                    doc_id = cur.lastrowid
                    counts = frequencies(document.body)
                    conn.executemany(
                        "INSERT INTO terms(document_id, term, frequency) VALUES (?,?,?)",
                        [(doc_id, term, count) for term, count in counts.items()],
                    )
                    return True
            except sqlite3.Error as exc:
                raise StorageError(f"cannot insert {document.key}: {exc}") from exc

    def list_documents(self) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT path, title, byte_size, sha256, indexed_at "
                "FROM documents ORDER BY path"
            ).fetchall()
            return [dict(row) for row in rows]

    def get_document(self, key: str) -> dict | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT path,title,body,sha256,byte_size,indexed_at "
                "FROM documents WHERE path=?", (key,)
            ).fetchone()
            return dict(row) if row else None

    def search(self, query: str, limit: int = 10) -> list[dict]:
        terms = normalize_query(query)
        if not terms or limit <= 0:
            return []
        placeholders = ",".join("?" for _ in terms)
        sql = (
            "SELECT d.path, d.title, SUM(t.frequency) AS score "
            "FROM terms t JOIN documents d ON d.id=t.document_id "
            f"WHERE t.term IN ({placeholders}) "
            "GROUP BY d.id ORDER BY score DESC, d.path ASC LIMIT ?"
        )
        with self.connect() as conn:
            return [dict(row) for row in conn.execute(sql, (*terms, limit))]

    def count(self):
        with self.connect() as conn:
            return conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
