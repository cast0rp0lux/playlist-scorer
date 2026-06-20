from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VersionInfo:
    engine_version: str = "0.1.0"
    data_version: str = "2026.06.20"
    schema_version: str = "0.1"
    rules_version: str = "0.1"
    weights_version: str = "0.1"
    llm_adapter_version: str = "none"

    def to_dict(self) -> dict[str, str]:
        return {
            "engine_version": self.engine_version,
            "data_version": self.data_version,
            "schema_version": self.schema_version,
            "rules_version": self.rules_version,
            "weights_version": self.weights_version,
            "llm_adapter_version": self.llm_adapter_version,
        }


VERSION_INFO = VersionInfo()
