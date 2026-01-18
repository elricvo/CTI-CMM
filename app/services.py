import json
from datetime import date
from typing import Any, Dict, List, Optional


def _serialize_audit(payload: Optional[Dict[str, Any]]) -> Optional[str]:
    if payload is None:
        return None
    return json.dumps(payload, ensure_ascii=True, sort_keys=True)


def _audit_log(
    conn,
    entity_type: str,
    entity_id: int,
    action: str,
    old_data: Optional[Dict[str, Any]],
    new_data: Optional[Dict[str, Any]],
) -> None:
    conn.execute(
        """
        INSERT INTO audit_log (entity_type, entity_id, action, old_data, new_data)
        VALUES (?, ?, ?, ?, ?);
        """,
        (
            entity_type,
            entity_id,
            action,
            _serialize_audit(old_data),
            _serialize_audit(new_data),
        ),
    )


def _fetch_practice_score(conn, assessment_id: int, practice_id: int) -> Optional[Dict[str, Any]]:
    row = conn.execute(
        """
        SELECT
            id,
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
        FROM practice_score
        WHERE assessment_id = ? AND practice_id = ?;
        """,
        (assessment_id, practice_id),
    ).fetchone()
    return dict(row) if row else None


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
    assessment_id = int(cursor.lastrowid)
    _audit_log(
        conn,
        "assessment",
        assessment_id,
        "create",
        None,
        {
            "id": assessment_id,
            "name": name,
            "assessment_date": assessment_date,
            "notes": notes,
        },
    )
    conn.commit()
    return assessment_id


def assessment_exists(conn, assessment_id: int) -> bool:
    row = conn.execute(
        "SELECT 1 FROM assessment WHERE id = ?;", (assessment_id,)
    ).fetchone()
    return row is not None


def upsert_practice_score(conn, payload: Dict[str, Any]) -> int:
    old_row = _fetch_practice_score(
        conn, payload["assessment_id"], payload["practice_id"]
    )
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
    new_row = _fetch_practice_score(
        conn, payload["assessment_id"], payload["practice_id"]
    )
    if new_row:
        action = "create" if old_row is None else "update"
        _audit_log(conn, "practice_score", new_row["id"], action, old_row, new_row)
    conn.commit()
    return int(cursor.lastrowid or (new_row["id"] if new_row else 0))


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
    asset_id = int(cursor.lastrowid)
    _audit_log(
        conn,
        "asset",
        asset_id,
        "create",
        None,
        {
            "id": asset_id,
            "name": name,
            "asset_type": asset_type,
            "criticality": criticality,
            "tags": tags,
        },
    )
    conn.commit()
    return asset_id


def link_asset_practice(conn, asset_id: int, practice_id: int) -> bool:
    cursor = conn.execute(
        """
        INSERT OR IGNORE INTO asset_practice (asset_id, practice_id)
        VALUES (?, ?);
        """,
        (asset_id, practice_id),
    )
    if cursor.rowcount > 0:
        _audit_log(
            conn,
            "asset_practice",
            int(cursor.lastrowid),
            "create",
            None,
            {"asset_id": asset_id, "practice_id": practice_id},
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


def get_assessment_trends(conn) -> List[Dict[str, Any]]:
    total_row = conn.execute("SELECT COUNT(*) AS count FROM practice;").fetchone()
    total_practices = int(total_row["count"] or 0)

    rows = conn.execute(
        """
        SELECT
            a.id AS assessment_id,
            a.name AS assessment_name,
            a.assessment_date AS assessment_date,
            COUNT(ps.score) AS scored_practices,
            AVG(ps.score) AS average_score
        FROM assessment a
        LEFT JOIN practice_score ps ON ps.assessment_id = a.id
        GROUP BY a.id
        ORDER BY a.assessment_date ASC, a.id ASC;
        """
    ).fetchall()

    results = []
    for row in rows:
        scored = row["scored_practices"] or 0
        completion = round((scored / total_practices) * 100, 2) if total_practices else 0.0
        results.append(
            {
                "assessment_id": row["assessment_id"],
                "assessment_name": row["assessment_name"],
                "assessment_date": row["assessment_date"],
                "average_score": row["average_score"],
                "scored_practices": scored,
                "total_practices": total_practices,
                "completion_pct": completion,
            }
        )

    return results


def get_evolution(conn, days: int = 30) -> List[Dict[str, Any]]:
    window = f"-{days} days"
    rows = conn.execute(
        """
        SELECT
            date(created_at) AS day,
            entity_type,
            COUNT(*) AS count
        FROM audit_log
        WHERE date(created_at) >= date('now', ?)
        GROUP BY day, entity_type
        ORDER BY day DESC;
        """,
        (window,),
    ).fetchall()

    mapping = {
        "assessment": "assessments",
        "asset": "assets",
        "practice_score": "scores",
        "asset_practice": "links",
    }
    buckets: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        day = row["day"]
        entry = buckets.get(day)
        if entry is None:
            entry = {
                "date": day,
                "total": 0,
                "assessments": 0,
                "assets": 0,
                "scores": 0,
                "links": 0,
                "other": 0,
            }
            buckets[day] = entry
        entry["total"] += row["count"]
        key = mapping.get(row["entity_type"], "other")
        entry[key] += row["count"]

    return [buckets[day] for day in sorted(buckets.keys(), reverse=True)]
