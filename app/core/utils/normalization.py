from __future__ import annotations

import re
import unicodedata

from app.core.config.loader import load_normalization_config


SEPARATORS = (" - ", " – ", " — ", "\t", "|")


def normalize_name(value: str) -> str:
    value = strip_accents(value).casefold()
    value = re.sub(r"\b(the|a|an)\b", " ", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def normalize_title(value: str) -> str:
    value = strip_accents(value).casefold()
    config = load_normalization_config()
    for pattern in config["title_noise_patterns"]:
        value = re.sub(pattern, " ", value, flags=re.IGNORECASE)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def canonical_key(artist: str, title: str, year: int | None = None) -> str:
    parts = [normalize_name(artist), normalize_title(title)]
    if year:
        parts.append(str(year))
    return "::".join(parts)


def parse_era(value: str | None) -> tuple[int, int] | None:
    if not value:
        return None
    match = re.search(r"(\d{4})s?", value)
    if not match:
        return None
    start = int(match.group(1))
    if start % 10 == 0 and value.strip().endswith("s"):
        return start, start + 9
    return start, start


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char))
