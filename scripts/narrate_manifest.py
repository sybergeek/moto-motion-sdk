"""Synthesize a Moto Motion narration manifest with Kokoro TTS.

Usage:
    python scripts/narrate_manifest.py examples/reel.narration.json
    python scripts/narrate_manifest.py examples/reel.narration.json --timing-mode natural
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro import KPipeline


def synthesize(pipeline: KPipeline, text: str, voice: str, speed: float) -> np.ndarray:
    chunks: list[np.ndarray] = []
    for result in pipeline(text, voice=voice, speed=speed, split_pattern=r"\n+"):
        if result.audio is not None:
            chunks.append(result.audio.detach().cpu().numpy())
    if not chunks:
        raise RuntimeError(f"Kokoro returned no audio for: {text[:80]}")
    return np.concatenate(chunks).astype(np.float32)


def duration_seconds(path: Path) -> float:
    with wave.open(str(path), "rb") as handle:
        return handle.getnframes() / handle.getframerate()


def fit_segment(audio: np.ndarray, target_seconds: float, sample_rate: int, temp_dir: Path) -> np.ndarray:
    target_samples = int(round(target_seconds * sample_rate))
    if len(audio) <= target_samples:
        return audio

    raw_path = temp_dir / "raw.wav"
    fitted_path = temp_dir / "fitted.wav"
    sf.write(raw_path, audio, sample_rate, subtype="PCM_16")
    factor = min(2.0, len(audio) / target_samples)
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-y", "-i", str(raw_path), "-filter:a", f"atempo={factor:.6f}", str(fitted_path)],
        check=True,
    )
    fitted, fitted_rate = sf.read(fitted_path, dtype="float32")
    if fitted_rate != sample_rate:
        raise RuntimeError(f"unexpected sample rate from ffmpeg: {fitted_rate}")
    return np.asarray(fitted, dtype=np.float32)


def write_timing_manifest(path: Path | None, base: dict, rendered: list[dict[str, object]], duration: float) -> None:
    """Write scene windows derived from measured narration segment durations."""
    if path is None:
        return
    timing = json.loads(path.read_text()) if path.exists() else {
        "schema": "moto-motion.scene-timing.v1",
        "project": base["project"],
        "scenes": [],
    }
    if not timing.get("scenes"):
        timing["scenes"] = [
            {"id": item["scene_id"], "trigger": next((segment.get("visual_trigger") for segment in base.get("segments", []) if segment.get("id") == item["id"]), None)}
            for item in rendered
        ]
    by_id = {str(item["id"]): item for item in rendered}
    scenes = []
    for scene in timing.get("scenes", []):
        measured = by_id.get(str(scene["id"]))
        scenes.append({**scene, **({"start_seconds": measured["start_seconds"], "end_seconds": measured["end_seconds"]} if measured else {})})
    timing.update({"duration_seconds": round(duration, 3), "timing_status": "audio_derived_from_narration", "scenes": scenes})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(timing, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--voice")
    parser.add_argument("--speed", type=float)
    parser.add_argument("--timing-mode", choices=("natural", "fixed"), default="natural", help="natural derives scene windows from measured audio; fixed preserves manifest windows")
    parser.add_argument("--timing-output", type=Path, help="optional scene-timing JSON to update from measured segment windows")
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text())
    sample_rate = int(manifest.get("synthesis", {}).get("sample_rate", 24000))
    voice_config = manifest.get("voice", {})
    voice = args.voice or voice_config.get("voice_id", "af_heart")
    speed = args.speed or float(voice_config.get("speed", 1.0))
    output_dir = args.output_dir or Path("media/audio") / manifest["project"]
    segment_dir = output_dir / "segments"
    segment_dir.mkdir(parents=True, exist_ok=True)

    pipeline = KPipeline(lang_code=manifest.get("language", "en-US"), device="cpu")
    synthesis_config = manifest.get("synthesis", {})
    if args.timing_mode == "natural":
        leading_pause = float(synthesis_config.get("leading_pause_seconds", 0.15))
        inter_segment_pause = float(synthesis_config.get("inter_segment_pause_seconds", 0.35))
        trailing_pause = float(synthesis_config.get("trailing_pause_seconds", 0.25))
        timeline = np.zeros(0, dtype=np.float32)
        cursor_samples = int(round(leading_pause * sample_rate))
        timeline = np.zeros(cursor_samples, dtype=np.float32)
    else:
        timeline = np.zeros(int(round(manifest["duration_seconds"] * sample_rate)), dtype=np.float32)
        cursor_samples = 0
    rendered: list[dict[str, object]] = []

    for segment in manifest["segments"]:
        segment_id = str(segment["id"])
        target = float(segment["end_seconds"]) - float(segment["start_seconds"])
        audio = synthesize(pipeline, str(segment["text"]), voice, speed)
        if args.timing_mode == "fixed":
            with tempfile.TemporaryDirectory(prefix="moto-motion-tts-") as temp_path:
                audio = fit_segment(audio, target, sample_rate, Path(temp_path))
            start = int(round(float(segment["start_seconds"]) * sample_rate))
            end = min(len(timeline), start + len(audio))
            if end > len(timeline):
                timeline = np.pad(timeline, (0, end - len(timeline)))
            timeline[start:end] += audio[: end - start]
        else:
            start = cursor_samples
            end = start + len(audio)
            timeline = np.pad(timeline, (0, len(audio)))
            timeline[start:end] += audio
            cursor_samples = end + int(round(inter_segment_pause * sample_rate))
            timeline = np.pad(timeline, (0, int(round(inter_segment_pause * sample_rate))))
        segment_path = segment_dir / f"{segment_id}.wav"
        sf.write(segment_path, audio, sample_rate, subtype="PCM_16")
        rendered.append({
            "id": segment_id,
            "scene_id": segment.get("scene_id", segment_id),
            "path": str(segment_path),
            "duration_seconds": len(audio) / sample_rate,
            "start_seconds": round(start / sample_rate, 3),
            "end_seconds": round(end / sample_rate, 3),
        })

    if args.timing_mode == "natural":
        timeline = np.pad(timeline, (0, int(round(trailing_pause * sample_rate))))

    peak = float(np.max(np.abs(timeline)))
    if peak > 0:
        timeline *= 10 ** (-1 / 20) / peak
    narration_path = output_dir / "narration.wav"
    sf.write(narration_path, timeline, sample_rate, subtype="PCM_16")
    actual_duration = len(timeline) / sample_rate
    result = {"manifest": str(args.manifest), "voice": voice, "speed": speed, "sample_rate": sample_rate, "timing_mode": args.timing_mode, "segments": rendered, "duration_seconds": round(actual_duration, 3), "narration": str(narration_path)}
    (output_dir / "rendered.json").write_text(json.dumps(result, indent=2) + "\n")
    write_timing_manifest(args.timing_output, manifest, rendered, actual_duration)
    print(narration_path)


if __name__ == "__main__":
    main()
