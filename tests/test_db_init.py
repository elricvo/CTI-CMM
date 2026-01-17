import sqlite3
import tempfile
import unittest
from pathlib import Path

from app import db


class TestDbInit(unittest.TestCase):
    def test_init_creates_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "app.db"
            db.init_db(db_path)

            self.assertTrue(db_path.exists())

            conn = sqlite3.connect(db_path)
            try:
                tables = {
                    row[0]
                    for row in conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table';"
                    )
                }
            finally:
                conn.close()

            self.assertIn("schema_version", tables)
            self.assertIn("domain", tables)
