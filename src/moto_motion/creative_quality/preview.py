"""Low-cost opening previews using existing video or a preview-aware Manim scene."""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from .models import PreviewManifest


@dataclass(frozen=True)
class PreviewRequest:
    reel_id: str
    revision_id: str
    duration_seconds: float = 3.0
    resolution: tuple[int, int] = (1080, 1920)
    frame_rate: int = 30
    output_dir: Path = Path("media/creative_quality")

    def __post_init__(self) -> None:
        if self.duration_seconds <= 0:
            raise ValueError("duration_seconds must be positive")
        if min(self.resolution) <= 0 or self.frame_rate <= 0:
            raise ValueError("resolution and frame_rate must be positive")


def bounded_duration(requested: float, available: float | None = None) -> float:
    if requested <= 0:
        raise ValueError("requested duration must be positive")
    return min(requested, available) if available is not None else requested


def _run(command: Sequence[str], *, env: dict[str, str] | None = None) -> None:
    subprocess.run(list(command), check=True, env=env)


class OpeningPreviewRenderer:
    """Render only an opening artifact; source-video trimming is the safest path."""

    def __init__(self, *, ffmpeg: str = "ffmpeg", ffprobe: str = "ffprobe", manim: str = "manim"):
        self.ffmpeg = ffmpeg
        self.ffprobe = ffprobe
        self.manim = manim

    def trim_video(self, source_video: str | Path, request: PreviewRequest, *, provisional: bool | None = None, timing_status: str = "unknown") -> PreviewManifest:
        source = Path(source_video)
        if not source.exists():
            raise FileNotFoundError(source)
        output_dir = request.output_dir / request.reel_id / request.revision_id
        output_dir.mkdir(parents=True, exist_ok=True)
        video = output_dir / "opening_preview.mp4"
        first_frame = output_dir / "opening_first_frame.png"
        width, height = request.resolution
        _run([self.ffmpeg, "-y", "-i", str(source), "-t", str(request.duration_seconds), "-map", "0:v:0", "-map", "0:a:0?", "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2", "-r", str(request.frame_rate), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart", str(video)])
        self.extract_first_frame(video, first_frame)
        narration_status = "available" if self.has_audio(video) else "missing"
        manifest = PreviewManifest(request.reel_id, request.revision_id, request.duration_seconds, request.resolution, request.frame_rate, str(video), str(first_frame), None, narration_status, timing_status, (narration_status != "available" or timing_status != "audio_derived") if provisional is None else provisional, "trimmed_video", datetime.now(timezone.utc).isoformat())
        self.write_manifest(manifest, output_dir / "preview_manifest.json")
        return manifest

    def render_scene(self, scene_file: str | Path, scene_name: str, request: PreviewRequest, *, narration_available: bool = False, timing_status: str = "provisional") -> PreviewManifest:
        """Invoke a scene with preview env vars; scenes should honor the time limit."""
        output_dir = request.output_dir / request.reel_id / request.revision_id
        manim_dir = output_dir / "manim"
        output_dir.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        env.update({"MOTO_MOTION_PREVIEW": "1", "MOTO_MOTION_PREVIEW_DURATION": str(request.duration_seconds)})
        command = [self.manim, "-ql", "--resolution", f"{request.resolution[0]},{request.resolution[1]}", "--frame_rate", str(request.frame_rate), "--media_dir", str(manim_dir), "--output_file", "opening_scene", str(scene_file), scene_name]
        _run(command, env=env)
        rendered = next(manim_dir.rglob("opening_scene.mp4"), None)
        if rendered is None:
            raise FileNotFoundError("Manim did not produce opening_scene.mp4")
        request = PreviewRequest(request.reel_id, request.revision_id, request.duration_seconds, request.resolution, request.frame_rate, request.output_dir)
        manifest = self.trim_video(rendered, request, provisional=not narration_available, timing_status=timing_status)
        return PreviewManifest(**{**manifest.to_dict(), "source_kind": "manim_scene"})

    def extract_first_frame(self, video: str | Path, output: str | Path) -> Path:
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        _run([self.ffmpeg, "-y", "-i", str(video), "-frames:v", "1", "-update", "1", str(output)])
        return output

    def has_audio(self, video: str | Path) -> bool:
        result = subprocess.run([self.ffprobe, "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=index", "-of", "csv=p=0", str(video)], capture_output=True, text=True, check=True)
        return bool(result.stdout.strip())

    @staticmethod
    def write_manifest(manifest: PreviewManifest, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest.to_dict(), indent=2) + "\n", encoding="utf-8")
        return path

