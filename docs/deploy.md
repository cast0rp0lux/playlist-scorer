# Cloud Deploy

Playlist Scorer can run as a Telegram webhook service. In this mode your computer does not need to stay on.

## Environment Variables

Set these in the hosting provider:

- `TELEGRAM_BOT_TOKEN`: token from `@BotFather`.
- `TELEGRAM_WEBHOOK_SECRET`: random secret used to verify Telegram webhook calls.
- `PUBLIC_BASE_URL`: public HTTPS URL of the deployed service, for example `https://playlist-scorer.onrender.com`.

On startup, the API registers:

```text
PUBLIC_BASE_URL/telegram/webhook
```

as the Telegram webhook.

## Render Blueprint

The repository includes `render.yaml`. Create a Render Blueprint from the GitHub repo and set:

- `TELEGRAM_BOT_TOKEN`
- `PUBLIC_BASE_URL`

Render can generate `TELEGRAM_WEBHOOK_SECRET` from the blueprint.

## Health Checks

- `GET /health`
- `GET /version`

## Telegram Flow

Telegram sends messages to `POST /telegram/webhook`. The app validates the optional secret header, analyzes the pasted playlist, and sends the audit card back to the same chat.
