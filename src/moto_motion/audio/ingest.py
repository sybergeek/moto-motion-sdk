"""Deterministic FFmpeg-based SFX inspection and non-destructive segmentation."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class IngestConfig:
    silence_db: float = -40.0
    minimum_silence_seconds: float = 0.25
    context_seconds: float = 0.06
    min_event_seconds: float = 0.30
    fade_seconds: float = 0.025
    sample_rate: int = 48000
    target_lufs: float = -20.0


class SFXIngestor:
    SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg", ".m4a"}

    def __init__(self, config: IngestConfig = IngestConfig()):
        self.config = config

    @staticmethod
    def _run(*args: str) -> str:
        return subprocess.run(args, check=True, text=True, capture_output=True).stdout

    def inspect(self, source: str | Path) -> dict:
        source = Path(source)
        if source.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported SFX input {source.suffix!r}; expected one of "
                f"{', '.join(sorted(self.SUPPORTED_EXTENSIONS))}."
            )
        raw = self._run("ffprobe", "-v", "error", "-show_entries", "format=duration,bit_rate:stream=codec_name,sample_rate,channels", "-of", "json", str(source))
        report = json.loads(raw)
        report["source"] = str(source)
        return report

    def silence_regions(self, source: str | Path) -> list[tuple[float, float]]:
        source = Path(source)
        process = subprocess.run(
            ["ffmpeg", "-hide_banner", "-i", str(source), "-af", f"silencedetect=noise={self.config.silence_db}dB:d={self.config.minimum_silence_seconds}", "-f", "null", "-"],
            text=True, capture_output=True, check=True,
        )
        starts = [float(value) for value in re.findall(r"silence_start: ([0-9.]+)", process.stderr)]
        ends = [float(value) for value in re.findall(r"silence_end: ([0-9.]+)", process.stderr)]
        return list(zip(starts, ends, strict=False))

    def candidate_events(self, source: str | Path) -> list[tuple[float, float]]:
        info = self.inspect(source)
        duration = float(info["format"]["duration"])
        silences = self.silence_regions(source)
        cursor = 0.0
        events = []
        for start, end in silences:
            if start - cursor >= self.config.min_event_seconds:
                events.append((max(0.0, cursor - self.config.context_seconds), min(duration, start + self.config.context_seconds)))
            cursor = max(cursor, end)
        if duration - cursor >= self.config.min_event_seconds:
            events.append((max(0.0, cursor - self.config.context_seconds), duration))
        return events

    def extract(self, source: str | Path, output: str | Path, start: float, end: float) -> dict:
        source, output = Path(source), Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        duration = max(0.01, end - start)
        fade = min(self.config.fade_seconds, duration / 4)
        filters = f"atrim=start={start:.6f}:end={end:.6f},asetpts=N/SR/TB,aresample={self.config.sample_rate},afade=t=in:st=0:d={fade:.6f},afade=t=out:st={max(0, duration-fade):.6f}:d={fade:.6f},loudnorm=I={self.config.target_lufs}:TP=-3:LRA=11"
        subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", str(source), "-af", filters, "-ar", str(self.config.sample_rate), str(output)], check=True)
        return {"source_file": str(source), "start_seconds": start, "end_seconds": end, "duration_seconds": duration, "fades_seconds": fade, "sample_rate": self.config.sample_rate, "filters": filters, "config": asdict(self.config)}
