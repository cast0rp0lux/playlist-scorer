from __future__ import annotations

import re

_WEBHOOK_SECRET_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,256}$")


def is_valid_webhook_secret(secret: str) -> bool:
    return bool(_WEBHOOK_SECRET_PATTERN.fullmatch(secret))
