# Architecture

Playlist Scorer is split into a deterministic core and thin delivery adapters.

## Layers

1. Ingestion: parses pasted text and JSON into `PlaylistRequest`.
2. Normalization: canonicalizes names and titles for matching.
3. Enrichment: uses versioned local data before any future external source.
4. Classification: applies hard and soft rules to each track.
5. Aggregation: computes metrics and pipeline-weighted final scores.
6. Explanation: renders stable text and JSON.
7. Output adapters: Telegram and HTTP API.

## Determinism

The core does not call an LLM. Future LLM use should live behind an adapter and only handle ambiguity resolution or explanatory prose. Any model-assisted decision should be marked in debug metadata.

## Versioned Inputs

Every result includes:

- `engine_version`
- `data_version`
- `schema_version`
- `rules_version`
- `weights_version`
- `llm_adapter_version`
