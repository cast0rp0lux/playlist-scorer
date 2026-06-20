from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any

from app.bot.telegram_messages import build_reply


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
    client.send_message(chat_id, build_reply(text))


if __name__ == "__main__":
    main()
