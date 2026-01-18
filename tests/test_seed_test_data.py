"""
Author: eric vanoverbeke
Date: 2026-01-18
"""

import sqlite3
import unittest

from app.db import apply_migrations
from app.seed import TEST_SEED_PATH, load_seed_data, seed_reference_data, seed_test_records


class TestSeedTestData(unittest.TestCase):
    def test_seed_test_data_populates_tables(self) -> None:
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            apply_migrations(conn)
            payload = load_seed_data(TEST_SEED_PATH)

            self.assertTrue(seed_reference_data(conn, payload))
            self.assertTrue(seed_test_records(conn, payload))

            domain_count = conn.execute("SELECT COUNT(*) FROM domain;").fetchone()[0]
            practice_count = conn.execute("SELECT COUNT(*) FROM practice;").fetchone()[0]
            assessment_count = conn.execute("SELECT COUNT(*) FROM assessment;").fetchone()[0]
            asset_count = conn.execute("SELECT COUNT(*) FROM asset;").fetchone()[0]
            score_count = conn.execute("SELECT COUNT(*) FROM practice_score;").fetchone()[0]

            self.assertGreaterEqual(domain_count, 3)
            self.assertGreaterEqual(practice_count, 12)
            self.assertGreaterEqual(assessment_count, 2)
            self.assertGreaterEqual(asset_count, 3)
            self.assertGreaterEqual(score_count, 10)
        finally:
            conn.close()
