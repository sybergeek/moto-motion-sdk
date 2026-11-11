"""Build narrated baseline and narration-aware SFX comparison audio."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from moto_motion.audio.events import SFXScheduler
from moto_motion.audio.mix import AudioMixConfig, SFXMixer
from moto_motion.audio.narration import SpeechDetector
from moto_motion.audio.registry import SFXRegistry


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "media/sfx_narration_demo"
NARRATION_SOURCE = ROOT / "media/audio/reel_003_kimi_champion/narration.wav"


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    narration = OUTPUT / "narration_excerpt.wav"
    subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", str(NARRATION_SOURCE), "-t", "6.2", "-ar", "48000", "-ac", "2", str(narration)], check=True)
    silence = OUTPUT / "sfx_silence.wav"
    subprocess.run(["ffmpeg", "-hide_banner", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", "6.2", str(silence)], check=True)
    scheduler = SFXScheduler()
    scheduler.emit("text.pop", at=.35, intensity=.45)
    scheduler.counter(start=.65, duration=1.2, ticks=5)
    scheduler.emit("character.enter", at=2.1, intensity=.5)
    scheduler.emit("vehicle.accelerate", at=2.55, intensity=.8, pan=-.4)
    scheduler.emit("vehicle.flyby", at=3.15, intensity=.85, pan=.7, closest_approach_time=3.45)
    scheduler.emit("trophy.reveal", at=3.8, intensity=.7)
    registry = SFXRegistry(ROOT / "assets/sfx/manifests/registry.json")
    missing = registry.validate()
    if missing:
        raise RuntimeError(f"registry entries missing files: {missing}")
    detector = SpeechDetector()
    regions = detector.detect(narration)
    # Build the no-duck control as a standalone SFX bus, then combine it with
    # the same narration. This keeps the comparison honest and avoids making
    # the no-duck path depend on a narration sidechain graph.
    sfx_only = OUTPUT / "sfx_only.wav"
    SFXMixer(registry).mix(silence, scheduler.cues, sfx_only)
    baseline = OUTPUT / "baseline.wav"
    subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", str(narration), "-i", str(sfx_only), "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[mix]", "-map", "[mix]", "-ar", "48000", "-ac", "2", str(baseline)], check=True)
    (OUTPUT / "baseline/stems").mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", str(narration), "-ar", "48000", "-ac", "2", str(OUTPUT / "baseline/stems/narration.wav")], check=True)
    subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", str(sfx_only), "-ar", "48000", "-ac", "2", str(OUTPUT / "baseline/stems/sfx.wav")], check=True)
    subprocess.run(["ffmpeg", "-hide_banner", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", "6.2", str(OUTPUT / "baseline/stems/music.wav")], check=True)
    (OUTPUT / "baseline/report.json").write_text(json.dumps({"mode": "baseline", "narration_priority": False, "auto_ducking": False, "speech_gap_scheduling": False, "planned_cues": [cue.__dict__ for cue in scheduler.cues], "stems": {"narration": "media/sfx_narration_demo/baseline/stems/narration.wav", "sfx": "media/sfx_narration_demo/baseline/stems/sfx.wav", "music": "media/sfx_narration_demo/baseline/stems/music.wav"}}, indent=2, default=str) + "\n")
    aware = SFXMixer(registry)
    aware.mix(narration, scheduler.cues, OUTPUT / "narration_aware.wav", speech_regions=regions, stems_dir=OUTPUT / "narration_aware/stems", report_path=OUTPUT / "narration_aware/report.json")
    (OUTPUT / "timeline.json").write_text(json.dumps({"mode": "hybrid", "narration": str(narration.relative_to(ROOT)), "speech_detection": "RMS fallback; narration manifest has no word-level alignment", "speech_regions": [region.__dict__ for region in regions], "cues": [cue.__dict__ for cue in scheduler.cues], "missing_assets": missing}, indent=2, default=str) + "\n")


if __name__ == "__main__":
    main()
