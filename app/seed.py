import json
from pathlib import Path
from typing import Any, Dict

from app.config import is_test_data_enabled
from app.db import apply_migrations, connect

SEED_PATH = Path(__file__).resolve().parents[1] / "seed" / "domains.json"
TEST_SEED_PATH = Path(__file__).resolve().parents[1] / "seed" / "test_data.json"


def load_seed_data(path: Path = SEED_PATH) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def seed_reference_data(conn, payload: Dict[str, Any]) -> bool:
    row = conn.execute("SELECT COUNT(*) AS count FROM domain;").fetchone()
    if row["count"] > 0:
        return False

    for domain in payload.get("domains", []):
        domain_id = conn.execute(
            "INSERT INTO domain (code, name, description) VALUES (?, ?, ?);",
            (domain.get("code"), domain.get("name"), domain.get("description")),
        ).lastrowid

        for objective in domain.get("objectives", []):
            objective_id = conn.execute(
                "INSERT INTO objective (domain_id, code, name, description) VALUES (?, ?, ?, ?);",
                (
                    domain_id,
                    objective.get("code"),
                    objective.get("name"),
                    objective.get("description"),
                ),
            ).lastrowid

            for practice in objective.get("practices", []):
                conn.execute(
                    "INSERT INTO practice (objective_id, code, name, description) VALUES (?, ?, ?, ?);",
                    (
                        objective_id,
                        practice.get("code"),
                        practice.get("name"),
                        practice.get("description"),
                    ),
                )

    conn.commit()
    return True


def seed_test_records(conn, payload: Dict[str, Any]) -> bool:
    row = conn.execute("SELECT COUNT(*) AS count FROM assessment;").fetchone()
    if row["count"] > 0:
        return False

    practice_rows = conn.execute("SELECT id, code FROM practice;").fetchall()
    practice_map = {row["code"]: row["id"] for row in practice_rows}

    assessment_map = {}
    for assessment in payload.get("assessments", []):
        cursor = conn.execute(
            "INSERT INTO assessment (name, assessment_date, notes) VALUES (?, ?, ?);",
            (
                assessment.get("name"),
                assessment.get("assessment_date"),
                assessment.get("notes"),
            ),
        )
        assessment_map[assessment.get("name")] = cursor.lastrowid

    asset_map = {}
    for asset in payload.get("assets", []):
        cursor = conn.execute(
            "INSERT INTO asset (name, asset_type, criticality, tags) VALUES (?, ?, ?, ?);",
            (
                asset.get("name"),
                asset.get("asset_type"),
                asset.get("criticality"),
                asset.get("tags"),
            ),
        )
        asset_map[asset.get("name")] = cursor.lastrowid

    for link in payload.get("asset_links", []):
        asset_id = asset_map.get(link.get("asset_name"))
        practice_id = practice_map.get(link.get("practice_code"))
        if asset_id and practice_id:
            conn.execute(
                "INSERT OR IGNORE INTO asset_practice (asset_id, practice_id) VALUES (?, ?);",
                (asset_id, practice_id),
            )

    for score in payload.get("scores", []):
        assessment_id = assessment_map.get(score.get("assessment_name"))
        practice_id = practice_map.get(score.get("practice_code"))
        if not assessment_id or not practice_id:
            continue
        conn.execute(
            """
            INSERT INTO practice_score (
                assessment_id,
                practice_id,
                score,
                evidence,
                poc,
                target_score,
                impact,
                effort,
                priority,
                target_date,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (assessment_id, practice_id) DO UPDATE SET
                score = excluded.score,
                evidence = excluded.evidence,
                poc = excluded.poc,
                target_score = excluded.target_score,
                impact = excluded.impact,
                effort = excluded.effort,
                priority = excluded.priority,
                target_date = excluded.target_date,
                notes = excluded.notes;
            """,
            (
                assessment_id,
                practice_id,
                score.get("score"),
                score.get("evidence"),
                score.get("poc"),
                score.get("target_score"),
                score.get("impact"),
                score.get("effort"),
                score.get("priority"),
                score.get("target_date"),
                score.get("notes"),
            ),
        )

    conn.commit()
    return True


def seed_db() -> bool:
    conn = connect()
    try:
        apply_migrations(conn)
        seeded = False
        if is_test_data_enabled():
            payload = load_seed_data(TEST_SEED_PATH)
            seeded |= seed_reference_data(conn, payload)
            seeded |= seed_test_records(conn, payload)
        else:
            payload = load_seed_data(SEED_PATH)
            seeded |= seed_reference_data(conn, payload)
        return seeded
    finally:
        conn.close()
