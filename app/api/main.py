from __future__ import annotations

from typing import Any

try:
    from fastapi import FastAPI, HTTPException
except ImportError as exc:  # pragma: no cover - exercised only without optional deps
    raise RuntimeError("Install API dependencies with: python -m pip install -e '.[api]'") from exc

from app.core.engine import analyze_playlist
from app.core.ingestion.parser import parse_input
from app.core.version import VERSION_INFO

app = FastAPI(title="Playlist Scorer", version=VERSION_INFO.engine_version)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/version")
def version() -> dict[str, str]:
    return VERSION_INFO.to_dict()


@app.post("/analyze-playlist")
def analyze_playlist_endpoint(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        raw = payload.get("text") or payload.get("playlist") or payload
        request = parse_input(
            raw,
            playlist_name=payload.get("name", "Untitled Playlist"),
            pipeline=payload.get("pipeline", "scene"),
            target_scene=payload.get("target_scene"),
            target_genre=payload.get("target_genre"),
            target_era=payload.get("target_era"),
        )
        return analyze_playlist(request).to_dict()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
