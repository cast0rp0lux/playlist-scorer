from __future__ import annotations

from collections import defaultdict

from app.core.models import AuditResult, Classification, TrackAudit


def render_curatorial_card(result: AuditResult) -> str:
    playlist = result.playlist
    grouped = _group_tracks(result.tracks)
    lines = [
        "PLAYLIST SCORER AUDIT",
        "",
        f"Pipeline: {playlist.pipeline.value}",
        f"Playlist name: {playlist.name}",
        f"Target genre / scene: {playlist.target_genre or 'unspecified'} / {playlist.target_scene or 'unspecified'}",
        f"Target era: {playlist.target_era or 'unspecified'}",
        f"Number of tracks: {len(result.tracks)}",
        "",
        "TRACK AUDIT",
    ]
    for track in result.tracks:
        lines.append(_render_track_line(track))
    lines.extend(["", "CLASSIFICATION SUMMARY"])
    for classification in Classification:
        items = grouped.get(classification, [])
        names = ", ".join(f"{track.artist} - {track.title}" for track in items) or "none"
        lines.append(f"{classification.value}: {names}")
    lines.extend(
        [
            "",
            "METRICS",
            f"Scene density: {result.metrics.scene_density:.2f}",
            f"Scene gravity loss: {result.metrics.scene_gravity_loss:.2f}",
            f"Scene cohesion: {result.metrics.scene_cohesion:.2f}",
            f"Decade purity: {result.metrics.decade_purity:.2f}",
            f"Country cohesion: {result.metrics.country_cohesion:.2f}",
            f"Diversity: {result.metrics.diversity:.2f}",
            f"Rarity: {result.metrics.rarity:.2f}",
            f"Discovery score: {result.metrics.discovery_score:.2f}",
            f"Contamination risk: {result.metrics.contamination_risk:.2f}",
            "",
            "COMPARATIVE CONTEXT",
            _comparative_context(result),
            "",
            "VERDICT",
            result.verdict,
            f"Final score: {result.metrics.final_score:.2f}",
        ]
    )
    if result.warnings:
        lines.extend(["", "WARNINGS", *result.warnings])
    lines.append("END")
    return "\n".join(lines)


def _render_track_line(track: TrackAudit) -> str:
    year = track.year if track.year is not None else "unknown year"
    country = track.country or "unknown country"
    notes = f" Notes: {' '.join(track.notes)}" if track.notes else ""
    flags = f" Flags: {', '.join(track.flags)}" if track.flags else ""
    return (
        f"- {track.id}: {track.artist} - {track.title} "
        f"({year}, {country}) -> {track.classification.value}; role: {track.role}.{notes}{flags}"
    )


def _group_tracks(tracks: list[TrackAudit]) -> dict[Classification, list[TrackAudit]]:
    grouped: dict[Classification, list[TrackAudit]] = defaultdict(list)
    for track in tracks:
        grouped[track.classification].append(track)
    return grouped


def _comparative_context(result: AuditResult) -> str:
    if result.metrics.contamination_risk >= 35:
        return "This behaves more like a mixed or contaminated selection than a strict scene document."
    if result.metrics.scene_cohesion >= 75 and result.metrics.decade_purity >= 70:
        return "This behaves like a coherent scene audit with a defensible historical frame."
    return "This sits between scene document and exploratory mix; edge tracks need human review."
