import json
from pathlib import Path
from typing import Any, Dict

from app.db import apply_migrations, connect

SEED_PATH = Path(__file__).resolve().parents[1] / "seed" / "domains.json"


def load_seed_data(path: Path = SEED_PATH) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def seed_if_empty(conn) -> bool:
    row = conn.execute("SELECT COUNT(*) AS count FROM domain;").fetchone()
    if row["count"] > 0:
        return False

    payload = load_seed_data()
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


def seed_db() -> bool:
    conn = connect()
    try:
        apply_migrations(conn)
        return seed_if_empty(conn)
    finally:
        conn.close()
