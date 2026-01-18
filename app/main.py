from pathlib import Path
import os
import sqlite3
import signal
import threading
import time
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

from app.config import get_default_language, is_quit_allowed
from app.db import connect
from app.seed import seed_db
from app import services

WEB_INDEX_PATH = Path(__file__).resolve().parents[1] / "web" / "index.html"


class AssessmentCreate(BaseModel):
    name: str
    assessment_date: Optional[str] = None
    notes: Optional[str] = None


class AssetCreate(BaseModel):
    name: str
    asset_type: Optional[str] = None
    criticality: Optional[int] = None
    tags: Optional[str] = None


class ScoreUpsert(BaseModel):
    assessment_id: int
    practice_id: int
    score: Optional[int] = None
    evidence: Optional[str] = None
    poc: Optional[str] = None
    target_score: Optional[int] = None
    impact: Optional[int] = None
    effort: Optional[int] = None
    priority: Optional[int] = None
    target_date: Optional[str] = None
    notes: Optional[str] = None


class AssetLink(BaseModel):
    asset_id: int
    practice_id: int


def index():
    if WEB_INDEX_PATH.exists():
        return FileResponse(WEB_INDEX_PATH)
    return HTMLResponse(
        "<h1>CTI-CMM</h1><p>UI not ready yet.</p>", status_code=200
    )


def healthz():
    return {"status": "ok"}


def config_payload():
    return {"default_language": get_default_language()}


def request_shutdown() -> None:
    def _shutdown() -> None:
        time.sleep(0.5)
        os.kill(os.getpid(), signal.SIGINT)

    thread = threading.Thread(target=_shutdown, daemon=True)
    thread.start()


def _validate_score(value: Optional[int], field_name: str) -> None:
    if value is None:
        return
    if value not in (0, 1, 2, 3):
        raise HTTPException(status_code=400, detail=f"{field_name} must be 0-3 or null")


def create_app() -> FastAPI:
    app = FastAPI()

    @app.on_event("startup")
    def _startup() -> None:
        try:
            seed_db()
        except FileNotFoundError:
            pass

    app.get("/")(index)
    app.get("/api/healthz")(healthz)
    app.get("/api/config")(config_payload)

    @app.post("/api/quit")
    def post_quit(request: Request):
        client_host = request.client.host if request.client else None
        if not is_quit_allowed(client_host):
            raise HTTPException(status_code=403, detail="shutdown not allowed")
        request_shutdown()
        return {"status": "shutting_down"}

    @app.get("/api/domains")
    def get_domains(assessment_id: Optional[int] = Query(None, gt=0)):
        conn = connect()
        try:
            return services.get_domains(conn, assessment_id)
        finally:
            conn.close()

    @app.get("/api/assessments")
    def get_assessments():
        conn = connect()
        try:
            return services.list_assessments(conn)
        finally:
            conn.close()

    @app.post("/api/assessments")
    def post_assessment(payload: AssessmentCreate):
        name = payload.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="name is required")
        conn = connect()
        try:
            assessment_id = services.create_assessment(
                conn, name, payload.assessment_date, payload.notes
            )
        finally:
            conn.close()
        return {"id": assessment_id}

    @app.get("/api/dashboard")
    def get_dashboard(assessment_id: int = Query(..., gt=0)):
        conn = connect()
        try:
            if not services.assessment_exists(conn, assessment_id):
                raise HTTPException(status_code=404, detail="assessment not found")
            return services.get_dashboard(conn, assessment_id)
        finally:
            conn.close()

    @app.get("/api/backlog")
    def get_backlog(assessment_id: int = Query(..., gt=0)):
        conn = connect()
        try:
            if not services.assessment_exists(conn, assessment_id):
                raise HTTPException(status_code=404, detail="assessment not found")
            return services.get_backlog(conn, assessment_id)
        finally:
            conn.close()

    @app.get("/api/assets")
    def get_assets():
        conn = connect()
        try:
            return services.list_assets(conn)
        finally:
            conn.close()

    @app.post("/api/assets")
    def post_assets(payload: AssetCreate):
        name = payload.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="name is required")
        conn = connect()
        try:
            asset_id = services.create_asset(
                conn, name, payload.asset_type, payload.criticality, payload.tags
            )
        finally:
            conn.close()
        return {"id": asset_id}

    @app.post("/api/asset-links")
    def post_asset_link(payload: AssetLink):
        if payload.asset_id <= 0 or payload.practice_id <= 0:
            raise HTTPException(status_code=400, detail="invalid ids")
        conn = connect()
        try:
            try:
                created = services.link_asset_practice(
                    conn, payload.asset_id, payload.practice_id
                )
            except sqlite3.IntegrityError:
                raise HTTPException(
                    status_code=400, detail="invalid asset or practice"
                )
        finally:
            conn.close()
        return {"created": created}

    @app.post("/api/scores")
    def post_score(payload: ScoreUpsert):
        if payload.assessment_id <= 0 or payload.practice_id <= 0:
            raise HTTPException(status_code=400, detail="invalid ids")
        _validate_score(payload.score, "score")
        _validate_score(payload.target_score, "target_score")
        conn = connect()
        try:
            if not services.assessment_exists(conn, payload.assessment_id):
                raise HTTPException(status_code=404, detail="assessment not found")
            payload_dict = (
                payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
            )
            try:
                services.upsert_practice_score(conn, payload_dict)
            except sqlite3.IntegrityError:
                raise HTTPException(status_code=400, detail="invalid practice id")
        finally:
            conn.close()
        return {"status": "ok"}

    return app


app = create_app()
