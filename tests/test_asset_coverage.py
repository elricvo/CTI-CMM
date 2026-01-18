"""
Author: eric vanoverbeke
Date: 2026-01-18
"""

import sqlite3
import unittest

from app.db import apply_migrations
from app import services


class TestAssetCoverage(unittest.TestCase):
    def test_asset_coverage_counts_links(self) -> None:
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            apply_migrations(conn)
            domain_id = conn.execute(
                "INSERT INTO domain (code, name) VALUES ('D1', 'Domain');"
            ).lastrowid
            objective_id = conn.execute(
                "INSERT INTO objective (domain_id, code, name) VALUES (?, 'O1', 'Objective');",
                (domain_id,),
            ).lastrowid
            practice_id = conn.execute(
                "INSERT INTO practice (objective_id, code, name) VALUES (?, 'P1', 'Practice');",
                (objective_id,),
            ).lastrowid
            asset_id = conn.execute(
                "INSERT INTO asset (name) VALUES ('Asset A');"
            ).lastrowid
            conn.execute(
                "INSERT INTO asset_practice (asset_id, practice_id) VALUES (?, ?);",
                (asset_id, practice_id),
            )
            conn.commit()

            coverage = services.get_asset_coverage(conn)
            self.assertEqual(len(coverage), 1)
            self.assertEqual(coverage[0]["linked_practices"], 1)
        finally:
            conn.close()
