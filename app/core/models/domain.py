from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class Pipeline(StrEnum):
    GENRE = "genre"
    RARE = "rare"
    DISCOVERY = "discovery"
    SCENE = "scene"
    SIMILAR = "similar"
    MIX = "mix"


class Classification(StrEnum):
    CORE = "core"
    PERIPHERAL = "peripheral"
    ANCESTOR = "ancestor"
    DESCENDANT = "descendant"
    OUTLIER = "outlier"
    METADATA_ERROR = "metadata_error"


@dataclass(frozen=True)
class TrackInput:
    id: str
    artist: str
    title: str
    album: str | None = None
    year: int | None = None
    country: str | None = None
    genre_tags: list[str] = field(default_factory=list)
    source: str = "text"
    confidence: float = 0.5


@dataclass(frozen=True)
class PlaylistRequest:
    id: str
    name: str
    pipeline: Pipeline
    tracks: list[TrackInput]
    target_genre: str | None = None
    target_scene: str | None = None
    target_era: str | None = None


@dataclass(frozen=True)
class ArtistRecord:
    id: str
    canonical_name: str
    aliases: list[str]
    countries: list[str]
    scenes: list[str]
    active_years: tuple[int, int] | None = None
    tags: list[str] = field(default_factory=list)
    rarity: float = 0.5


@dataclass(frozen=True)
class SceneRecord:
    id: str
    name: str
    countries: list[str]
    eras: list[str]
    core_artists: list[str]
    parent_scenes: list[str] = field(default_factory=list)
    child_scenes: list[str] = field(default_factory=list)
    related_scenes: list[str] = field(default_factory=list)
    styles: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class TrackAudit:
    id: str
    artist: str
    title: str
    year: int | None
    country: str | None
    scene: str | None
    styles: list[str]
    confidence: float
    classification: Classification
    role: str
    notes: list[str]
    flags: list[str]
    score_components: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["classification"] = self.classification.value
        return data


@dataclass(frozen=True)
class MetricSet:
    scene_cohesion: float
    decade_purity: float
    country_cohesion: float
    diversity: float
    rarity: float
    discovery_score: float
    contamination_risk: float
    scene_density: float
    scene_gravity_loss: float
    final_score: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True)
class AuditResult:
    playlist: PlaylistRequest
    tracks: list[TrackAudit]
    metrics: MetricSet
    verdict: str
    warnings: list[str]
    debug_info: dict[str, Any]
    version: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "playlist": {
                "id": self.playlist.id,
                "name": self.playlist.name,
                "pipeline": self.playlist.pipeline.value,
                "target_genre": self.playlist.target_genre,
                "target_scene": self.playlist.target_scene,
                "target_era": self.playlist.target_era,
                "track_count": len(self.playlist.tracks),
            },
            "tracks": [track.to_dict() for track in self.tracks],
            "metrics": self.metrics.to_dict(),
            "verdict": self.verdict,
            "warnings": self.warnings,
            "debug_info": self.debug_info,
            "version": self.version,
        }
