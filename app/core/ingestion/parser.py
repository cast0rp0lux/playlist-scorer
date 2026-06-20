from __future__ import annotations

import hashlib
import json
from typing import Any

from app.core.models import Pipeline, PlaylistRequest, TrackInput
from app.core.utils.normalization import SEPARATORS


def parse_input(
    raw: str | dict[str, Any],
    *,
    playlist_name: str,
    pipeline: str,
    target_scene: str | None = None,
    target_genre: str | None = None,
    target_era: str | None = None,
) -> PlaylistRequest:
    if isinstance(raw, dict):
        return _parse_json_payload(raw, playlist_name, pipeline, target_scene, target_genre, target_era)
    text = raw.strip()
    if not text:
        raise ValueError("Playlist input is empty.")
    if text.startswith("{") or text.startswith("["):
        return _parse_json_payload(json.loads(text), playlist_name, pipeline, target_scene, target_genre, target_era)
    tracks = _parse_text_lines(text)
    return PlaylistRequest(
        id=_playlist_id(playlist_name, tracks),
        name=playlist_name,
        pipeline=Pipeline(pipeline.casefold()),
        tracks=tracks,
        target_genre=target_genre,
        target_scene=target_scene,
        target_era=target_era,
    )


def _parse_json_payload(
    payload: dict[str, Any] | list[Any],
    playlist_name: str,
    pipeline: str,
    target_scene: str | None,
    target_genre: str | None,
    target_era: str | None,
) -> PlaylistRequest:
    if isinstance(payload, list):
        tracks_payload = payload
        name = playlist_name
    else:
        tracks_payload = payload.get("tracks") or payload.get("items") or []
        name = payload.get("name", playlist_name)
        pipeline = payload.get("pipeline", pipeline)
        target_scene = payload.get("target_scene", target_scene)
        target_genre = payload.get("target_genre", target_genre)
        target_era = payload.get("target_era", target_era)
    tracks = [_track_from_mapping(item, index) for index, item in enumerate(tracks_payload, start=1)]
    if not tracks:
        raise ValueError("JSON playlist has no tracks.")
    return PlaylistRequest(
        id=_playlist_id(name, tracks),
        name=name,
        pipeline=Pipeline(pipeline.casefold()),
        tracks=tracks,
        target_genre=target_genre,
        target_scene=target_scene,
        target_era=target_era,
    )


def _parse_text_lines(text: str) -> list[TrackInput]:
    tracks: list[TrackInput] = []
    for line in text.splitlines():
        cleaned = line.strip()
        if not cleaned or cleaned.startswith("#"):
            continue
        artist, title = _split_track_line(cleaned)
        tracks.append(TrackInput(id=f"t{len(tracks) + 1:03d}", artist=artist, title=title, source="text"))
    if not tracks:
        raise ValueError("No valid tracks found. Use lines like: Artist - Title.")
    return tracks


def _split_track_line(line: str) -> tuple[str, str]:
    for separator in SEPARATORS:
        if separator in line:
            artist, title = line.split(separator, 1)
            return artist.strip(), title.strip()
    raise ValueError(f"Cannot parse track line: {line}")


def _track_from_mapping(item: Any, index: int) -> TrackInput:
    if not isinstance(item, dict):
        raise ValueError("JSON tracks must be objects.")
    artist = item.get("artist") or item.get("artist_name")
    title = item.get("title") or item.get("track_title") or item.get("name")
    if not artist or not title:
        raise ValueError("Each track needs artist and title.")
    return TrackInput(
        id=str(item.get("id") or f"t{index:03d}"),
        artist=str(artist),
        title=str(title),
        album=item.get("album"),
        year=_safe_int(item.get("year")),
        country=item.get("country"),
        genre_tags=list(item.get("genre_tags") or item.get("styles") or []),
        source=str(item.get("source") or "json"),
        confidence=float(item.get("confidence", 0.65)),
    )


def _safe_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return int(value)


def _playlist_id(name: str, tracks: list[TrackInput]) -> str:
    digest = hashlib.sha1((name + "|" + "|".join(f"{t.artist}-{t.title}" for t in tracks)).encode("utf-8")).hexdigest()
    return digest[:12]
