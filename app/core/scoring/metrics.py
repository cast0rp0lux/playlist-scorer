from __future__ import annotations

from collections import Counter

from app.core.config.loader import load_pipeline_weights
from app.core.models import Classification, MetricSet, Pipeline, PlaylistRequest, TrackAudit


POSITIVE_CLASSES = {
    Classification.CORE,
    Classification.PERIPHERAL,
    Classification.ANCESTOR,
    Classification.DESCENDANT,
}


def calculate_metrics(playlist: PlaylistRequest, tracks: list[TrackAudit]) -> MetricSet:
    if not tracks:
        raise ValueError("Cannot score an empty playlist.")
    scene_cohesion = _average(track.score_components["scene_fit"] for track in tracks)
    decade_purity = _average(track.score_components["decade_fit"] for track in tracks)
    country_cohesion = _average(track.score_components["country_fit"] for track in tracks)
    diversity = _artist_diversity(tracks)
    rarity = _average(track.score_components["rarity"] for track in tracks)
    contamination_risk = _contamination_risk(tracks)
    scene_density = _scene_density(tracks)
    discovery_score = _discovery_score(rarity, diversity, contamination_risk)
    scene_gravity_loss = _scene_gravity_loss(tracks)
    final_score = _weighted_score(
        playlist.pipeline,
        {
            "scene_cohesion": scene_cohesion,
            "decade_purity": decade_purity,
            "country_cohesion": country_cohesion,
            "diversity": diversity,
            "rarity": rarity,
            "discovery_score": discovery_score,
            "contamination_risk": contamination_risk,
            "scene_density": scene_density,
            "scene_gravity_loss": scene_gravity_loss,
        },
    )
    return MetricSet(
        scene_cohesion=round(scene_cohesion * 100, 2),
        decade_purity=round(decade_purity * 100, 2),
        country_cohesion=round(country_cohesion * 100, 2),
        diversity=round(diversity * 100, 2),
        rarity=round(rarity * 100, 2),
        discovery_score=round(discovery_score * 100, 2),
        contamination_risk=round(contamination_risk * 100, 2),
        scene_density=round(scene_density * 100, 2),
        scene_gravity_loss=round(scene_gravity_loss * 100, 2),
        final_score=round(final_score * 100, 2),
    )


def _weighted_score(pipeline: Pipeline, values: dict[str, float]) -> float:
    weights = load_pipeline_weights()[pipeline.value]
    score = 0.0
    for metric, weight in weights.items():
        value = values[metric]
        if metric in {"contamination_risk", "scene_gravity_loss"}:
            value = 1 - value
        score += value * weight
    return max(0.0, min(1.0, score / sum(weights.values())))


def _artist_diversity(tracks: list[TrackAudit]) -> float:
    unique_artists = len({track.artist.casefold() for track in tracks})
    return unique_artists / len(tracks)


def _contamination_risk(tracks: list[TrackAudit]) -> float:
    bad = sum(1 for track in tracks if track.classification in {Classification.OUTLIER, Classification.METADATA_ERROR})
    soft_flags = sum(1 for track in tracks if any(flag.endswith("unknown") or flag == "scene_ambiguous" for flag in track.flags))
    return min(1.0, (bad / len(tracks)) + (soft_flags / len(tracks) * 0.15))


def _scene_density(tracks: list[TrackAudit]) -> float:
    positive = sum(1 for track in tracks if track.classification in POSITIVE_CLASSES)
    core = sum(1 for track in tracks if track.classification == Classification.CORE)
    return min(1.0, (positive / len(tracks) * 0.65) + (core / len(tracks) * 0.35))


def _discovery_score(rarity: float, diversity: float, contamination_risk: float) -> float:
    return max(0.0, min(1.0, rarity * 0.45 + diversity * 0.4 + (1 - contamination_risk) * 0.15))


def _scene_gravity_loss(tracks: list[TrackAudit]) -> float:
    full = _average(track.score_components["scene_fit"] for track in tracks)
    checkpoints = [10, 20, len(tracks)]
    prefix_scores = []
    for checkpoint in checkpoints:
        if len(tracks) >= checkpoint:
            prefix_scores.append(_average(track.score_components["scene_fit"] for track in tracks[:checkpoint]))
    if not prefix_scores:
        return 0.0
    strongest_prefix = max(prefix_scores)
    return max(0.0, strongest_prefix - full)


def _average(values) -> float:
    values = list(values)
    return sum(values) / len(values)


def classification_counts(tracks: list[TrackAudit]) -> dict[str, int]:
    counts = Counter(track.classification.value for track in tracks)
    return dict(sorted(counts.items()))
