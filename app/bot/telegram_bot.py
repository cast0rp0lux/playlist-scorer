from __future__ import annotations

import json
import os

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
except ImportError as exc:  # pragma: no cover - exercised only without optional deps
    raise RuntimeError("Install Telegram dependencies with: python -m pip install -e '.[telegram]'") from exc

from app.core.engine import analyze_playlist
from app.core.ingestion.parser import parse_input
from app.core.output.card import render_curatorial_card
from app.core.version import VERSION_INFO


HELP_TEXT = """Playlist Scorer

Paste tracks as:
Artist - Title
Artist - Title

Commands:
/score - score the following pasted list
/analyze - same as /score
/json - return technical JSON
/debug - return JSON with debug fields
/version - engine version
"""


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT)


async def version_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(json.dumps(VERSION_INFO.to_dict(), indent=2))


async def score_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("Paste a playlist after the command or send it as a normal message.")
        return
    await send_analysis(update, text, as_json=False)


async def json_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("Paste a playlist after /json.")
        return
    await send_analysis(update, text, as_json=True)


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_analysis(update, update.message.text, as_json=False)


async def send_analysis(update: Update, text: str, as_json: bool) -> None:
    request = parse_input(text, playlist_name="Telegram Playlist", pipeline="scene")
    result = analyze_playlist(request)
    if as_json:
        body = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
    else:
        body = render_curatorial_card(result)
    for chunk_start in range(0, len(body), 3900):
        await update.message.reply_text(body[chunk_start : chunk_start + 3900])


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN before starting the bot.")
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("version", version_command))
    application.add_handler(CommandHandler("score", score_command))
    application.add_handler(CommandHandler("analyze", score_command))
    application.add_handler(CommandHandler("json", json_command))
    application.add_handler(CommandHandler("debug", json_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    application.run_polling()


if __name__ == "__main__":
    main()
