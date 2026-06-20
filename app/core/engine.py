from __future__ import annotations

from app.core.classification.rules import classify_track
from app.core.enrichment.local_knowledge import enrich_track
from app.core.models import AuditResult, PlaylistRequest, TrackAudit
from app.core.scoring.metrics import calculate_metrics, classification_counts
from app.core.version import VERSION_INFO


def analyze_playlist(playlist: PlaylistRequest) -> AuditResult:
    audits: list[TrackAudit] = []
    warnings: list[str] = []
    for track in playlist.tracks:
        enriched = enrich_track(track, playlist.target_scene)
        classification, role, notes, components = classify_track(enriched, playlist)
        if classification.value in {"outlier", "metadata_error"}:
            warnings.append(f"{track.artist} - {track.title}: {classification.value}")
        audits.append(
            TrackAudit(
                id=track.id,
                artist=enriched.artist_record.canonical_name if enriched.artist_record else track.artist,
                title=track.title,
                year=enriched.year,
                country=enriched.country,
                scene=enriched.scene_record.name if enriched.scene_record else None,
                styles=enriched.styles,
                confidence=enriched.confidence,
                classification=classification,
                role=role,
                notes=notes,
                flags=enriched.flags,
                score_components=components,
            )
        )
    metrics = calculate_metrics(playlist, audits)
    return AuditResult(
        playlist=playlist,
        tracks=audits,
        metrics=metrics,
        verdict=_verdict(metrics.final_score, metrics.contamination_risk),
        warnings=warnings,
        debug_info={
            "classification_counts": classification_counts(audits),
            "input_size": len(playlist.tracks),
            "enrichment_hits": sum(1 for audit in audits if "artist_ambiguous" not in audit.flags),
            "enrichment_misses": sum(1 for audit in audits if "artist_ambiguous" in audit.flags),
        },
        version=VERSION_INFO.to_dict(),
    )


def _verdict(final_score: float, contamination_risk: float) -> str:
    if final_score >= 85 and contamination_risk < 15:
        return "Excellent curatorial object: coherent, traceable, and low-contamination."
    if final_score >= 70:
        return "Strong playlist with a defensible frame and some reviewable edges."
    if final_score >= 50:
        return "Mixed curatorial result: useful, but the scene argument needs tightening."
    return "Weak scene document: too many unresolved, external, or anachronistic tracks."
