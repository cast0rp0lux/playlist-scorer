from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

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


class TelegramClient:
    def __init__(self, token: str) -> None:
        self.base_url = f"https://api.telegram.org/bot{token}"

    def call(self, method: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        data = None
        headers = {"Content-Type": "application/json"}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(f"{self.base_url}/{method}", data=data, headers=headers, method="POST")
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))

    def send_message(self, chat_id: int, text: str) -> None:
        for chunk_start in range(0, len(text), 3900):
            self.call("sendMessage", {"chat_id": chat_id, "text": text[chunk_start : chunk_start + 3900]})


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN before starting the bot.")

    client = TelegramClient(token)
    identity = client.call("getMe")
    username = identity.get("result", {}).get("username", "unknown")
    print(f"Playlist Scorer bot is running as @{username}. Press Ctrl+C to stop.")
    poll_updates(client)


def poll_updates(client: TelegramClient) -> None:
    offset = 0
    while True:
        try:
            response = client.call("getUpdates", {"offset": offset, "timeout": 30})
            for update in response.get("result", []):
                offset = max(offset, int(update["update_id"]) + 1)
                handle_update(client, update)
        except (urllib.error.URLError, TimeoutError) as exc:
            print(f"Telegram polling warning: {exc}")
            time.sleep(5)


def handle_update(client: TelegramClient, update: dict[str, Any]) -> None:
    message = update.get("message") or update.get("edited_message")
    if not message or "text" not in message:
        return
    chat_id = int(message["chat"]["id"])
    text = str(message["text"]).strip()
    if not text:
        return

    command, body = split_command(text)
    try:
        if command in {"/start", "/help"}:
            client.send_message(chat_id, HELP_TEXT)
        elif command == "/version":
            client.send_message(chat_id, json.dumps(VERSION_INFO.to_dict(), indent=2))
        elif command in {"/json", "/debug"}:
            client.send_message(chat_id, analyze_text(body, as_json=True))
        elif command in {"/score", "/analyze"}:
            client.send_message(chat_id, analyze_text(body, as_json=False))
        else:
            client.send_message(chat_id, analyze_text(text, as_json=False))
    except ValueError as exc:
        client.send_message(chat_id, f"Could not analyze that playlist: {exc}")


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


if __name__ == "__main__":
    main()
