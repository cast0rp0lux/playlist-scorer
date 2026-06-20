from __future__ import annotations

import json
import os
from typing import Any
import urllib.request

try:
    from fastapi import FastAPI, Header, HTTPException
except ImportError as exc:  # pragma: no cover - exercised only without optional deps
    raise RuntimeError("Install API dependencies with: python -m pip install -e '.[api]'") from exc

from app.bot.telegram_messages import build_reply
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


@app.on_event("startup")
def configure_telegram_webhook() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    public_base_url = os.environ.get("PUBLIC_BASE_URL")
    if not token or not public_base_url:
        return
    webhook_secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET")
    payload: dict[str, str] = {"url": f"{public_base_url.rstrip('/')}/telegram/webhook"}
    if webhook_secret:
        payload["secret_token"] = webhook_secret
    _telegram_call(token, "setWebhook", payload)


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


@app.post("/telegram/webhook")
def telegram_webhook(
    update: dict[str, Any],
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict[str, bool]:
    expected_secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET")
    if expected_secret and x_telegram_bot_api_secret_token != expected_secret:
        raise HTTPException(status_code=403, detail="Invalid Telegram webhook secret.")

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise HTTPException(status_code=500, detail="TELEGRAM_BOT_TOKEN is not configured.")

    message = update.get("message") or update.get("edited_message")
    if not message or "text" not in message:
        return {"ok": True}

    chat_id = int(message["chat"]["id"])
    reply = build_reply(str(message["text"]))
    for chunk_start in range(0, len(reply), 3900):
        _telegram_call(token, "sendMessage", {"chat_id": chat_id, "text": reply[chunk_start : chunk_start + 3900]})
    return {"ok": True}


def _telegram_call(token: str, method: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/{method}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))
