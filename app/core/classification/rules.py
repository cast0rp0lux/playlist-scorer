from __future__ import annotations

from app.core.config.loader import load_thresholds
from app.core.enrichment.local_knowledge import EnrichedTrack
from app.core.models import Classification, Pipeline, PlaylistRequest
from app.core.utils.normalization import normalize_name, parse_era


PURE_PIPELINES = {Pipeline.GENRE, Pipeline.SCENE}


def classify_track(enriched: EnrichedTrack, playlist: PlaylistRequest) -> tuple[Classification, str, list[str], dict[str, float]]:
    thresholds = load_thresholds()
    notes = list(enriched.notes)
    flags = list(enriched.flags)
    components = score_track_components(enriched, playlist)

    if "artist_ambiguous" in flags and enriched.confidence < thresholds["metadata_error_confidence"]:
        notes.append("Low-confidence artist match.")
        return Classification.METADATA_ERROR, "needs metadata review", notes, components

    if playlist.pipeline in PURE_PIPELINES and any(flag in flags for flag in thresholds["pure_pipeline_veto_flags"]):
        notes.append("Format flag conflicts with a purity-oriented pipeline.")
        return Classification.OUTLIER, "format contamination", notes, components

    if components["decade_fit"] == 0 and playlist.target_era:
        notes.append("Track falls outside the declared era.")
        return Classification.OUTLIER, "temporal break", notes, components

    if components["scene_fit"] >= 0.9 and components["country_fit"] >= 0.8 and components["decade_fit"] >= 0.8:
        return Classification.CORE, "scene nucleus", notes, components

    if components["scene_fit"] >= 0.65 and components["decade_fit"] >= 0.5:
        notes.append("Compatible with the target, but not central on every axis.")
        return Classification.PERIPHERAL, "compatible edge", notes, components

    relation = scene_relation(enriched, playlist)
    if relation == "ancestor":
        notes.append("Earlier related scene acts as a historical source.")
        return Classification.ANCESTOR, "historical source", notes, components
    if relation == "descendant":
        notes.append("Later related scene inherits the language without strict membership.")
        return Classification.DESCENDANT, "later inheritance", notes, components

    notes.append("Cannot justify the track inside the declared curatorial frame.")
    return Classification.OUTLIER, "curatorial break", notes, components


def score_track_components(enriched: EnrichedTrack, playlist: PlaylistRequest) -> dict[str, float]:
    return {
        "scene_fit": _scene_fit(enriched, playlist),
        "country_fit": _country_fit(enriched, playlist),
        "decade_fit": _decade_fit(enriched, playlist),
        "style_fit": _style_fit(enriched, playlist),
        "confidence": enriched.confidence,
        "rarity": enriched.artist_record.rarity if enriched.artist_record else 0.2,
    }


def scene_relation(enriched: EnrichedTrack, playlist: PlaylistRequest) -> str | None:
    if not enriched.scene_record or not playlist.target_scene:
        return None
    target = _target_scene_id(playlist.target_scene)
    if target in enriched.scene_record.child_scenes:
        return "ancestor"
    if target in enriched.scene_record.parent_scenes:
        return "descendant"
    return None


def _scene_fit(enriched: EnrichedTrack, playlist: PlaylistRequest) -> float:
    if not playlist.target_scene:
        return 0.75 if enriched.scene_record else 0.35
    if not enriched.scene_record:
        return 0.1
    target = _target_scene_id(playlist.target_scene)
    if enriched.scene_record.id == target or normalize_name(enriched.scene_record.name) == normalize_name(playlist.target_scene):
        return 1.0
    if target in enriched.scene_record.related_scenes:
        return 0.7
    if target in enriched.scene_record.parent_scenes or target in enriched.scene_record.child_scenes:
        return 0.55
    return 0.15


def _country_fit(enriched: EnrichedTrack, playlist: PlaylistRequest) -> float:
    if not playlist.target_scene or not enriched.scene_record:
        return 0.7 if enriched.country else 0.35
    if enriched.country and enriched.country in enriched.scene_record.countries:
        return 1.0
    return 0.55 if enriched.country else 0.25


def _decade_fit(enriched: EnrichedTrack, playlist: PlaylistRequest) -> float:
    era = parse_era(playlist.target_era)
    if not era:
        return 0.7
    if enriched.year is None:
        if enriched.artist_record and enriched.artist_record.active_years:
            active_start, active_end = enriched.artist_record.active_years
            era_start, era_end = era
            if active_start <= era_end and active_end >= era_start:
                return 0.85
        return 0.45
    start, end = era
    if start <= enriched.year <= end:
        return 1.0
    distance = min(abs(enriched.year - start), abs(enriched.year - end))
    if distance <= 3:
        return 0.65
    if distance <= 10:
        return 0.35
    return 0.0


def _style_fit(enriched: EnrichedTrack, playlist: PlaylistRequest) -> float:
    if not playlist.target_genre:
        return 0.7 if enriched.styles else 0.35
    target = normalize_name(playlist.target_genre)
    return 1.0 if any(normalize_name(style) == target for style in enriched.styles) else 0.45


def _target_scene_id(target_scene: str) -> str:
    return normalize_name(target_scene).replace(" ", "_")
