"""Portable SFX registry loader and validator."""

from __future__ import annotations

import json
from pathlib import Path


class SFXRegistry:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.root = self.path.parents[3] if self.path.parts[-3:] == ("sfx", "manifests", self.path.name) else self.path.parent
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.assets: dict[str, dict] = {entry["id"]: entry for entry in data["assets"]}

    def get(self, sfx_id: str) -> dict:
        return self.assets[sfx_id]

    def select(self, *, category: str | None = None, tags: set[str] | None = None) -> list[dict]:
        tags = tags or set()
        return [
            entry for entry in self.assets.values()
            if (category is None or entry["category"].startswith(category)) and tags.issubset(set(entry.get("tags", [])))
        ]

    def file_path(self, sfx_id: str) -> Path:
        return self.root / self.get(sfx_id)["file"]

    def validate(self) -> list[str]:
        return [sfx_id for sfx_id in self.assets if not self.file_path(sfx_id).is_file()]
