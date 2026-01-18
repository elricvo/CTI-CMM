import sqlite3
import unittest

from app import services
from app.db import apply_migrations


class TestAuditLog(unittest.TestCase):
    def test_create_assessment_logs_audit(self) -> None:
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            apply_migrations(conn)
            assessment_id = services.create_assessment(
                conn, "Audit Test", "2026-01-12", "note"
            )
            row = conn.execute("SELECT * FROM audit_log WHERE entity_type = 'assessment';").fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["entity_id"], assessment_id)
            self.assertEqual(row["action"], "create")
        finally:
            conn.close()
