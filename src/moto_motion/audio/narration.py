"""Narration speech-region detection for priority-aware audio mixes.

Alignment timestamps are used only when the manifest explicitly supplies real
word timestamps.  Otherwise this module uses a deterministic RMS detector;
provisional scene timing is intentionally never treated as speech timing.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class SpeechRegion:
    start: float
    end: float
    source: str


@dataclass(frozen=True)
class SpeechDetectionConfig:
    sample_rate: int = 16_000
    frame_ms: int = 20
    enter_dbfs: float = -36.0
    exit_dbfs: float = -42.0
    min_speech_seconds: float = 0.18
    min_gap_seconds: float = 0.35
    padding_seconds: float = 0.04


class SpeechDetector:
    def __init__(self, config: SpeechDetectionConfig = SpeechDetectionConfig()):
        self.config = config

    def from_manifest(self, manifest: str | Path) -> list[SpeechRegion]:
        data = json.loads(Path(manifest).read_text(encoding="utf-8"))
        words = data.get("alignment", {}).get("word_timestamps")
        if not isinstance(words, list) or not words:
            return []
        regions = []
        for word in words:
            if not isinstance(word, dict):
                continue
            start = word.get("start_seconds", word.get("start"))
            end = word.get("end_seconds", word.get("end"))
            if isinstance(start, (int, float)) and isinstance(end, (int, float)) and end > start:
                regions.append(SpeechRegion(float(start), float(end), "alignment"))
        return self._merge(regions, source="alignment")

    def detect(self, narration: str | Path, *, manifest: str | Path | None = None) -> list[SpeechRegion]:
        if manifest:
            aligned = self.from_manifest(manifest)
            if aligned:
                return aligned
        return self._detect_rms(Path(narration))

    def _detect_rms(self, narration: Path) -> list[SpeechRegion]:
        decoded = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(narration), "-ac", "1", "-ar", str(self.config.sample_rate), "-f", "f32le", "pipe:1"],
            check=True,
            capture_output=True,
        ).stdout
        samples = np.frombuffer(decoded, dtype=np.float32)
        frame = max(1, round(self.config.sample_rate * self.config.frame_ms / 1000))
        frames = samples[: len(samples) // frame * frame].reshape(-1, frame)
        rms = np.sqrt(np.mean(np.square(frames), axis=1) + 1e-12)
        dbfs = 20 * np.log10(rms + 1e-12)
        active = np.zeros(len(dbfs), dtype=bool)
        on = False
        for index, level in enumerate(dbfs):
            if not on and level >= self.config.enter_dbfs:
                on = True
            elif on and level < self.config.exit_dbfs:
                on = False
            active[index] = on
        regions: list[SpeechRegion] = []
        start: int | None = None
        for index, value in enumerate(active):
            if value and start is None:
                start = index
            elif not value and start is not None:
                if (index - start) * self.config.frame_ms / 1000 >= self.config.min_speech_seconds:
                    regions.append(SpeechRegion(start * self.config.frame_ms / 1000, index * self.config.frame_ms / 1000, "rms"))
                start = None
        if start is not None and (len(active) - start) * self.config.frame_ms / 1000 >= self.config.min_speech_seconds:
            regions.append(SpeechRegion(start * self.config.frame_ms / 1000, len(active) * self.config.frame_ms / 1000, "rms"))
        return self._merge(regions, source="rms")

    def _merge(self, regions: list[SpeechRegion], *, source: str) -> list[SpeechRegion]:
        if not regions:
            return []
        merged: list[SpeechRegion] = []
        for region in sorted(regions, key=lambda item: item.start):
            start = max(0.0, region.start - self.config.padding_seconds)
            end = region.end + self.config.padding_seconds
            if merged and start - merged[-1].end < self.config.min_gap_seconds:
                merged[-1] = SpeechRegion(merged[-1].start, max(merged[-1].end, end), source)
            else:
                merged.append(SpeechRegion(start, end, source))
        return merged


def speech_gaps(regions: list[SpeechRegion], duration: float, *, minimum_seconds: float = 0.35) -> list[tuple[float, float]]:
    """Return meaningful phrase gaps, never word-scale pauses."""
    cursor, gaps = 0.0, []
    for region in regions:
        if region.start - cursor >= minimum_seconds:
            gaps.append((cursor, region.start))
        cursor = max(cursor, region.end)
    if duration - cursor >= minimum_seconds:
        gaps.append((cursor, duration))
    return gaps
