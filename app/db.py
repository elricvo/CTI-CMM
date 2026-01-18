"""
Author: eric vanoverbeke
Date: 2026-01-18
"""

import sqlite3
from pathlib import Path
from typing import Iterable, Tuple, Union

from app.config import ensure_data_dir, get_db_path


MIGRATIONS: Iterable[Tuple[int, str]] = (
    (
        1,
        """
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER NOT NULL UNIQUE,
            applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS domain (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS objective (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (domain_id) REFERENCES domain(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS practice (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            objective_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (objective_id) REFERENCES objective(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS assessment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            assessment_date TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS practice_score (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER NOT NULL,
            practice_id INTEGER NOT NULL,
            score INTEGER,
            evidence TEXT,
            poc TEXT,
            target_score INTEGER,
            impact INTEGER,
            effort INTEGER,
            priority INTEGER,
            target_date TEXT,
            notes TEXT,
            UNIQUE (assessment_id, practice_id),
            FOREIGN KEY (assessment_id) REFERENCES assessment(id) ON DELETE CASCADE,
            FOREIGN KEY (practice_id) REFERENCES practice(id) ON DELETE CASCADE,
            CHECK (score IN (0, 1, 2, 3) OR score IS NULL),
            CHECK (target_score IN (0, 1, 2, 3) OR target_score IS NULL)
        );

        CREATE TABLE IF NOT EXISTS asset (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            asset_type TEXT,
            criticality INTEGER,
            tags TEXT
        );

        CREATE TABLE IF NOT EXISTS asset_practice (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id INTEGER NOT NULL,
            practice_id INTEGER NOT NULL,
            UNIQUE (asset_id, practice_id),
            FOREIGN KEY (asset_id) REFERENCES asset(id) ON DELETE CASCADE,
            FOREIGN KEY (practice_id) REFERENCES practice(id) ON DELETE CASCADE
        );
        """,
    ),
    (
        2,
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            entity_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            old_data TEXT,
            new_data TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """,
    ),
    (
        3,
        """
        ALTER TABLE practice_score
        ADD COLUMN updated_at TEXT NOT NULL DEFAULT (datetime('now'));

        UPDATE practice_score
        SET updated_at = datetime('now')
        WHERE updated_at IS NULL;
        """,
    ),
)


def _normalize_db_path(db_path: Union[Path, str, None]) -> Path:
    if db_path is None:
        ensure_data_dir()
        return get_db_path()
    path = Path(db_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def connect(db_path: Union[Path, str, None] = None) -> sqlite3.Connection:
    path = _normalize_db_path(db_path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def _current_schema_version(conn: sqlite3.Connection) -> int:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER NOT NULL UNIQUE,
            applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """
    )
    row = conn.execute("SELECT MAX(version) AS version FROM schema_version;").fetchone()
    return int(row["version"] or 0)


def apply_migrations(conn: sqlite3.Connection) -> None:
    current_version = _current_schema_version(conn)
    for version, sql in MIGRATIONS:
        if version > current_version:
            conn.executescript(sql)
            conn.execute("INSERT INTO schema_version (version) VALUES (?);", (version,))
            conn.commit()


def init_db(db_path: Union[Path, str, None] = None) -> Path:
    conn = connect(db_path)
    try:
        apply_migrations(conn)
    finally:
        conn.close()
    return _normalize_db_path(db_path)
