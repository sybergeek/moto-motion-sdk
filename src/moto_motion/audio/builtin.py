"""Small original procedural UI SFX; no third-party asset redistribution."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import soundfile as sf


SAMPLE_RATE = 48000


def _envelope(length: int, attack: float = 0.008, release: float = 0.08) -> np.ndarray:
    envelope = np.ones(length, dtype=np.float32)
    attack_samples = min(length, max(1, int(attack * SAMPLE_RATE)))
    release_samples = min(length, max(1, int(release * SAMPLE_RATE)))
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples, dtype=np.float32)
    envelope[-release_samples:] *= np.linspace(1, 0, release_samples, dtype=np.float32)
    return envelope


def _tone(seconds: float, start_hz: float, end_hz: float, *, amplitude: float = 0.25, noise: float = 0.0) -> np.ndarray:
    length = int(seconds * SAMPLE_RATE)
    frequency = np.linspace(start_hz, end_hz, length, dtype=np.float32)
    phase = 2 * np.pi * np.cumsum(frequency) / SAMPLE_RATE
    signal = amplitude * np.sin(phase) + noise * np.random.default_rng(7).normal(0, 1, length).astype(np.float32)
    return signal * _envelope(length)


def write_builtin_library(root: str | Path) -> list[dict]:
    root = Path(root)
    folder = root / "assets/sfx/processed/ui"
    folder.mkdir(parents=True, exist_ok=True)
    definitions = {
        "pop.soft": (0.12, 480, 780, 0.16, 0.0),
        "click.mechanical": (0.09, 1500, 900, 0.18, 0.04),
        "whoosh.short": (0.28, 220, 900, 0.10, 0.07),
        "whoosh.long": (0.72, 120, 1100, 0.09, 0.06),
        "impact.soft": (0.24, 145, 70, 0.28, 0.02),
        "impact.cinematic": (0.52, 95, 42, 0.36, 0.035),
        "counter.tick": (0.055, 1120, 990, 0.13, 0.0),
        "counter.complete": (0.19, 560, 980, 0.20, 0.0),
        "reveal.positive": (0.38, 480, 1320, 0.15, 0.01),
        "reveal.negative": (0.33, 600, 180, 0.13, 0.01),
        "character.entrance": (0.32, 280, 760, 0.11, 0.04),
        "celebration.accent": (0.44, 600, 1440, 0.16, 0.02),
        "slide.transition": (0.46, 160, 760, 0.10, 0.07),
        "trophy.reveal": (0.62, 520, 1480, 0.17, 0.015),
        "notification.short": (0.16, 740, 980, 0.15, 0.0),
    }
    assets = []
    for suffix, (seconds, start_hz, end_hz, amplitude, noise) in definitions.items():
        audio = _tone(seconds, start_hz, end_hz, amplitude=amplitude, noise=noise)
        stereo = np.column_stack((audio, audio))
        path = folder / f"{suffix.replace('.', '_')}.wav"
        sf.write(path, stereo, SAMPLE_RATE, subtype="PCM_16")
        assets.append({
            "id": f"ui.{suffix}", "name": suffix.replace(".", " ").title(), "category": f"ui.{suffix.rsplit('.', 1)[0]}",
            "file": path.relative_to(root).as_posix(), "duration_seconds": round(len(audio) / SAMPLE_RATE, 3), "sample_rate": SAMPLE_RATE,
            "channels": 2, "default_gain_db": -18, "tags": ["ui", *suffix.split(".")],
            "source": {"kind": "moto_motion_original_procedural", "license": "Project-owned", "attribution": None},
            "processing": {"generator": "moto_motion.audio.builtin", "seed": 7}, "recommended_events": [],
        })
    return assets
