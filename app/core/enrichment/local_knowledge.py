from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from app.core.models import ArtistRecord, SceneRecord, TrackInput
from app.core.utils.normalization import normalize_name, normalize_title


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


@dataclass(frozen=True)
class EnrichedTrack:
    track: TrackInput
    artist_record: ArtistRecord | None
    scene_record: SceneRecord | None
    year: int | None
    country: str | None
    styles: list[str]
    confidence: float
    flags: list[str]
    notes: list[str]


@lru_cache(maxsize=1)
def load_artists() -> dict[str, ArtistRecord]:
    records = _read_json(DATA_DIR / "artists" / "artists.json")
    index: dict[str, ArtistRecord] = {}
    for item in records:
        record = ArtistRecord(
            id=item["id"],
            canonical_name=item["canonical_name"],
            aliases=item.get("aliases", []),
            countries=item.get("countries", []),
            scenes=item.get("scenes", []),
            active_years=tuple(item["active_years"]) if item.get("active_years") else None,
            tags=item.get("tags", []),
            rarity=float(item.get("rarity", 0.5)),
        )
        index[normalize_name(record.canonical_name)] = record
        for alias in record.aliases:
            index[normalize_name(alias)] = record
    return index


@lru_cache(maxsize=1)
def load_scenes() -> dict[str, SceneRecord]:
    records = _read_json(DATA_DIR / "scenes" / "scenes.json")
    return {
        item["id"]: SceneRecord(
            id=item["id"],
            name=item["name"],
            countries=item.get("countries", []),
            eras=item.get("eras", []),
            core_artists=item.get("core_artists", []),
            parent_scenes=item.get("parent_scenes", []),
            child_scenes=item.get("child_scenes", []),
            related_scenes=item.get("related_scenes", []),
            styles=item.get("styles", []),
        )
        for item in records
    }


def enrich_track(track: TrackInput, target_scene: str | None = None) -> EnrichedTrack:
    artist = load_artists().get(normalize_name(track.artist))
    scenes = load_scenes()
    scene = _pick_scene(artist, scenes, target_scene)
    flags = infer_flags(track)
    notes: list[str] = []
    confidence = track.confidence
    if artist:
        confidence = max(confidence, 0.82)
    else:
        flags.append("artist_ambiguous")
        notes.append("Artist not found in local knowledge base.")
        confidence = min(confidence, 0.45)
    if track.year is None:
        flags.append("year_unknown")
    if not (track.country or (artist and artist.countries)):
        flags.append("country_unknown")
    styles = sorted(set(track.genre_tags + (artist.tags if artist else []) + (scene.styles if scene else [])))
    return EnrichedTrack(
        track=track,
        artist_record=artist,
        scene_record=scene,
        year=track.year,
        country=track.country or (artist.countries[0] if artist and artist.countries else None),
        styles=styles,
        confidence=confidence,
        flags=sorted(set(flags)),
        notes=notes,
    )


def infer_flags(track: TrackInput) -> list[str]:
    title = normalize_title(track.title)
    flags: list[str] = []
    checks = {
        "is_live": (" live ", "live"),
        "is_remix": (" remix ", "remix"),
        "is_edit": (" edit ", "radio edit", "single edit"),
        "is_reissue": (" remaster ", "reissue"),
        "is_soundtrack": (" soundtrack ", "ost"),
    }
    padded = f" {title} "
    for flag, patterns in checks.items():
        if any(pattern in padded for pattern in patterns):
            flags.append(flag)
    return flags


def _pick_scene(
    artist: ArtistRecord | None,
    scenes: dict[str, SceneRecord],
    target_scene: str | None,
) -> SceneRecord | None:
    if not artist:
        return None
    if target_scene:
        normalized_target = normalize_name(target_scene)
        for scene_id in artist.scenes:
            scene = scenes.get(scene_id)
            if scene and normalize_name(scene.name) == normalized_target:
                return scene
    return scenes.get(artist.scenes[0]) if artist.scenes else None


def _read_json(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)
