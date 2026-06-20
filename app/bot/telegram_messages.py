from __future__ import annotations

import json

from app.core.engine import analyze_playlist
from app.core.ingestion.parser import parse_input
from app.core.output.card import render_curatorial_card
from app.core.version import VERSION_INFO


HELP_TEXT = """Playlist Scorer

Paste tracks as:
Artist - Title
Artist - Title

Commands:
/score - score pasted tracks
/analyze - same as /score
/json - return technical JSON
/debug - return technical JSON
/help - show this help
/version - engine version
"""


def build_reply(text: str) -> str:
    text = text.strip()
    if not text:
        return HELP_TEXT

    command, body = split_command(text)
    try:
        if command in {"/start", "/help"}:
            return HELP_TEXT
        if command == "/version":
            return json.dumps(VERSION_INFO.to_dict(), indent=2)
        if command in {"/json", "/debug"}:
            return analyze_text(body, as_json=True)
        if command in {"/score", "/analyze"}:
            return analyze_text(body, as_json=False)
        return analyze_text(text, as_json=False)
    except ValueError as exc:
        return f"Could not analyze that playlist: {exc}"


def split_command(text: str) -> tuple[str | None, str]:
    if not text.startswith("/"):
        return None, text
    head, _, tail = text.partition(" ")
    return head.split("@", 1)[0].casefold(), tail.strip()


def analyze_text(text: str, *, as_json: bool) -> str:
    if not text:
        return "Paste tracks after the command or send a plain text playlist."
    request = parse_input(text, playlist_name="Telegram Playlist", pipeline="scene")
    result = analyze_playlist(request)
    if as_json:
        return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
    return render_curatorial_card(result)
