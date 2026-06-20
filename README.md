# Playlist Scorer

Playlist Scorer is a deterministic curatorial audit engine for playlists. It parses pasted track lists or JSON, normalizes tracks, enriches them from a local knowledge base, classifies each track, scores the playlist with pipeline-aware weights, and renders stable text or JSON output.

The first target surface is a Telegram bot, but the core is presentation-agnostic so it can also power an API or future web dashboard.

## What Works Now

- Pasted text input in `Artist - Title` format
- JSON input for playlist integrations
- Local curated knowledge base for artists and scenes
- Track classifications: `core`, `peripheral`, `ancestor`, `descendant`, `outlier`, `metadata_error`
- Metrics: scene cohesion, decade purity, country cohesion, diversity, rarity, discovery score, contamination risk, scene density, scene gravity loss
- Pipeline-specific scoring weights in config
- Stable curatorial card ending with `END`
- API and Telegram adapters kept outside the core engine
- Unit and integration tests

## Quick Start

```powershell
python -m app.cli --name "Minimal Wave Test" --pipeline scene --scene "minimal wave" --era 1980s --file .\examples\minimal_wave.txt
python -m unittest
```

## Optional API

Install the API extra, then run:

```powershell
python -m pip install -e ".[api]"
uvicorn app.api.main:app --reload
```

Endpoint:

```text
POST /analyze-playlist
```

## Optional Telegram Bot

No-dependency runner:

```powershell
$env:TELEGRAM_BOT_TOKEN="..."
python -m app.bot.simple_telegram_bot
```

Optional `python-telegram-bot` adapter:

```powershell
python -m pip install -e ".[telegram]"
$env:TELEGRAM_BOT_TOKEN="..."
python -m app.bot.telegram_bot
```

See [docs/telegram.md](docs/telegram.md) for the BotFather setup flow.

Supported commands:

- `/score`
- `/analyze`
- `/json`
- `/debug`
- `/help`
- `/version`

## Project Layout

```text
app/
  api/                 Future HTTP surface
  bot/                 Telegram adapter
  core/                Curatorial engine
    classification/
    config/
    enrichment/
    ingestion/
    models/
    output/
    scoring/
    utils/
  data/                Versioned local knowledge
docs/                  Product and engine notes
tests/                 Unit and integration tests
```
