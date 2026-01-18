from datetime import date
from typing import Any, Dict, List, Optional


def get_domains(conn, assessment_id: Optional[int] = None) -> List[Dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT
            d.id AS domain_id,
            d.code AS domain_code,
            d.name AS domain_name,
            d.description AS domain_description,
            o.id AS objective_id,
            o.code AS objective_code,
            o.name AS objective_name,
            o.description AS objective_description,
            p.id AS practice_id,
            p.code AS practice_code,
            p.name AS practice_name,
            p.description AS practice_description,
            ps.score AS score,
            ps.evidence AS evidence,
            ps.poc AS poc,
            ps.target_score AS target_score,
            ps.impact AS impact,
            ps.effort AS effort,
            ps.priority AS priority,
            ps.target_date AS target_date,
            ps.notes AS notes
        FROM domain d
        LEFT JOIN objective o ON o.domain_id = d.id
        LEFT JOIN practice p ON p.objective_id = o.id
        LEFT JOIN practice_score ps
            ON ps.practice_id = p.id
           AND ps.assessment_id = ?
        ORDER BY d.id, o.id, p.id;
        """,
        (assessment_id,),
    ).fetchall()

    domains: List[Dict[str, Any]] = []
    domain_map: Dict[int, Dict[str, Any]] = {}
    objective_map: Dict[int, Dict[str, Any]] = {}

    for row in rows:
        domain_id = row["domain_id"]
        domain = domain_map.get(domain_id)
        if domain is None:
            domain = {
                "id": domain_id,
                "code": row["domain_code"],
                "name": row["domain_name"],
                "description": row["domain_description"],
                "objectives": [],
            }
            domain_map[domain_id] = domain
            domains.append(domain)

        objective_id = row["objective_id"]
        if objective_id is None:
            continue

        objective = objective_map.get(objective_id)
        if objective is None:
            objective = {
                "id": objective_id,
                "code": row["objective_code"],
                "name": row["objective_name"],
                "description": row["objective_description"],
                "practices": [],
            }
            objective_map[objective_id] = objective
            domain["objectives"].append(objective)

        practice_id = row["practice_id"]
        if practice_id is None:
            continue

        objective["practices"].append(
            {
                "id": practice_id,
                "code": row["practice_code"],
                "name": row["practice_name"],
                "description": row["practice_description"],
                "score": row["score"],
                "evidence": row["evidence"],
                "poc": row["poc"],
                "target_score": row["target_score"],
                "impact": row["impact"],
                "effort": row["effort"],
                "priority": row["priority"],
                "target_date": row["target_date"],
                "notes": row["notes"],
            }
        )

    return domains


def list_assessments(conn) -> List[Dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT id, name, assessment_date, notes
        FROM assessment
        ORDER BY assessment_date DESC, id DESC;
        """
    ).fetchall()
    return [dict(row) for row in rows]


def create_assessment(
    conn, name: str, assessment_date: Optional[str], notes: Optional[str]
) -> int:
    if not assessment_date:
        assessment_date = date.today().isoformat()
    cursor = conn.execute(
        "INSERT INTO assessment (name, assessment_date, notes) VALUES (?, ?, ?);",
        (name, assessment_date, notes),
    )
    conn.commit()
    return int(cursor.lastrowid)


def assessment_exists(conn, assessment_id: int) -> bool:
    row = conn.execute(
        "SELECT 1 FROM assessment WHERE id = ?;", (assessment_id,)
    ).fetchone()
    return row is not None


def upsert_practice_score(conn, payload: Dict[str, Any]) -> int:
    cursor = conn.execute(
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
            payload["assessment_id"],
            payload["practice_id"],
            payload.get("score"),
            payload.get("evidence"),
            payload.get("poc"),
            payload.get("target_score"),
            payload.get("impact"),
            payload.get("effort"),
            payload.get("priority"),
            payload.get("target_date"),
            payload.get("notes"),
        ),
    )
    conn.commit()
    return int(cursor.lastrowid)


def list_assets(conn) -> List[Dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT id, name, asset_type, criticality, tags
        FROM asset
        ORDER BY name ASC, id ASC;
        """
    ).fetchall()
    return [dict(row) for row in rows]


def create_asset(
    conn, name: str, asset_type: Optional[str], criticality: Optional[int], tags: Optional[str]
) -> int:
    cursor = conn.execute(
        "INSERT INTO asset (name, asset_type, criticality, tags) VALUES (?, ?, ?, ?);",
        (name, asset_type, criticality, tags),
    )
    conn.commit()
    return int(cursor.lastrowid)


def link_asset_practice(conn, asset_id: int, practice_id: int) -> bool:
    cursor = conn.execute(
        """
        INSERT OR IGNORE INTO asset_practice (asset_id, practice_id)
        VALUES (?, ?);
        """,
        (asset_id, practice_id),
    )
    conn.commit()
    return cursor.rowcount > 0


def get_dashboard(conn, assessment_id: int) -> List[Dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT
            d.id AS domain_id,
            d.code AS domain_code,
            d.name AS domain_name,
            COUNT(p.id) AS total_practices,
            COUNT(ps.score) AS scored_practices,
            AVG(ps.score) AS average_score
        FROM domain d
        LEFT JOIN objective o ON o.domain_id = d.id
        LEFT JOIN practice p ON p.objective_id = o.id
        LEFT JOIN practice_score ps
            ON ps.practice_id = p.id
           AND ps.assessment_id = ?
        GROUP BY d.id
        ORDER BY d.id;
        """,
        (assessment_id,),
    ).fetchall()

    results = []
    for row in rows:
        total = row["total_practices"] or 0
        scored = row["scored_practices"] or 0
        completion = round((scored / total) * 100, 2) if total else 0.0
        results.append(
            {
                "domain_id": row["domain_id"],
                "domain_code": row["domain_code"],
                "domain_name": row["domain_name"],
                "total_practices": total,
                "scored_practices": scored,
                "average_score": row["average_score"],
                "completion_pct": completion,
            }
        )

    return results


def get_backlog(conn, assessment_id: int) -> List[Dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT
            d.code AS domain_code,
            d.name AS domain_name,
            o.code AS objective_code,
            o.name AS objective_name,
            p.id AS practice_id,
            p.code AS practice_code,
            p.name AS practice_name,
            ps.score AS score,
            ps.target_score AS target_score,
            ps.impact AS impact,
            ps.effort AS effort,
            ps.priority AS priority,
            ps.target_date AS target_date,
            ps.notes AS notes,
            COALESCE(ps.priority, (COALESCE(ps.impact, 0) * 2) - COALESCE(ps.effort, 0))
                AS computed_priority
        FROM practice_score ps
        JOIN practice p ON p.id = ps.practice_id
        JOIN objective o ON o.id = p.objective_id
        JOIN domain d ON d.id = o.domain_id
        WHERE ps.assessment_id = ?
          AND ps.target_score IS NOT NULL
          AND (ps.score IS NULL OR ps.target_score > ps.score)
        ORDER BY computed_priority DESC, COALESCE(ps.impact, 0) DESC, COALESCE(ps.effort, 0) ASC;
        """,
        (assessment_id,),
    ).fetchall()

    return [dict(row) for row in rows]
