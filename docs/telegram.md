# Telegram Bot Setup

The Telegram adapter is already implemented in `app/bot/telegram_bot.py`.

## Create The Bot

1. Open Telegram.
2. Start a chat with `@BotFather`.
3. Send `/newbot`.
4. Choose the display name, for example `Playlist Scorer`.
5. Choose a username ending in `bot`, for example `playlist_scorer_bot`.
6. Copy the token that BotFather returns.

## Run In Cloud

Use the webhook API if you do not want the bot running on your computer.

See [deploy.md](deploy.md).

## Run Locally

No-dependency runner:

```powershell
$env:TELEGRAM_BOT_TOKEN="PASTE_TOKEN_HERE"
python -m app.bot.simple_telegram_bot
```

Optional `python-telegram-bot` adapter:

```powershell
python -m pip install -e ".[telegram]"
$env:TELEGRAM_BOT_TOKEN="PASTE_TOKEN_HERE"
python -m app.bot.telegram_bot
```

## Commands

- `/score Artist - Title`
- `/analyze Artist - Title`
- `/json Artist - Title`
- `/debug Artist - Title`
- `/help`
- `/version`

You can also paste a plain text playlist directly:

```text
Linear Movement - The Game
Snowy Red - Euroshima
Molchat Doma - Sudno
```
