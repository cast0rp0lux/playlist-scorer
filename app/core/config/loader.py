from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


CONFIG_DIR = Path(__file__).resolve().parents[2] / "data" / "rules"


@lru_cache(maxsize=1)
def load_pipeline_weights() -> dict[str, dict[str, float]]:
    return _read_json(CONFIG_DIR / "pipeline_weights.json")


@lru_cache(maxsize=1)
def load_thresholds() -> dict[str, Any]:
    return _read_json(CONFIG_DIR / "thresholds.json")


@lru_cache(maxsize=1)
def load_normalization_config() -> dict[str, Any]:
    return _read_json(CONFIG_DIR / "normalization.json")


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)
