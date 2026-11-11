"""FFmpeg-backed, non-destructive helpers for real-footage productions.

The manager deliberately operates on references to originals.  A source is never
modified; each export is a new, named derivative with enough metadata to repeat
the operation.  Coordinates for overlays are expressed in the *delivered*
portrait frame, which avoids drift after a crop or resize.
"""

from __future__ import annotations

import json
import math
import subprocess
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path
from typing import Literal

SUPPORTED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".webm"}


@dataclass(frozen=True)
class VideoProbe:
    path: str
    width: int
    height: int
    duration_seconds: float
    frame_rate: float
    codec: str
    pixel_format: str | None
    has_audio: bool
    audio_codec: str | None
    orientation: str
    file_size_bytes: int


@dataclass(frozen=True)
class FootageAsset:
    """A preserved original and its verified technical metadata."""

    asset_id: str
    original: str
    probe: VideoProbe
    source_url: str | None = None
    creator: str | None = None
    license_name: str | None = None
    license_url: str | None = None
    downloaded_on: str | None = None
    restrictions: tuple[str, ...] = ()
    attribution: str | None = None
    match_status: Literal["verified", "ambiguous", "unmatched"] = "unmatched"


@dataclass(frozen=True)
class CropKeyframe:
    """Top-left crop offset in original-pixel space at a clip-relative time."""

    time_seconds: float
    x: int
    y: int


@dataclass(frozen=True)
class CropConfig:
    """Portrait crop policy.

    ``manual`` uses ``x``/``y`` in original pixels.  ``keyframed`` linearly
    interpolates between two or more original-pixel positions.  Subject tracking
    is intentionally explicit: V1 has no tracker, so callers must supply
    keyframes after review rather than silently trusting unreliable detection.
    """

    mode: Literal["center", "manual", "keyframed", "subject_follow"] = "center"
    x: int | None = None
    y: int | None = None
    keyframes: tuple[CropKeyframe, ...] = ()
    tracking_status: Literal["not_requested", "manual_required", "unavailable"] = "not_requested"


DEFAULT_CROP = CropConfig()


@dataclass(frozen=True)
class VideoClip:
    source: FootageAsset
    start_seconds: float
    end_seconds: float
    crop: CropConfig = CropConfig()
    speed: float = 1.0
    mute_source_audio: bool = True
    output_fps: float = 30.0
    label: str | None = None

    @property
    def duration_seconds(self) -> float:
        return self.end_seconds - self.start_seconds


@dataclass
class FootageManifest:
    """Portable asset provenance; no absolute source paths are written."""

    assets: list[FootageAsset] = field(default_factory=list)
    derived_clips: list[dict[str, object]] = field(default_factory=list)

    def add(self, asset: FootageAsset) -> FootageAsset:
        if any(item.asset_id == asset.asset_id for item in self.assets):
            raise ValueError(f"duplicate footage asset id: {asset.asset_id}")
        self.assets.append(asset)
        return asset

    def write(self, path: str | Path, *, root: str | Path) -> Path:
        root_path = Path(root).resolve()

        def portable(value: str) -> str:
            candidate = Path(value)
            if candidate.is_absolute():
                return str(candidate.resolve().relative_to(root_path))
            return value

        def asset_dict(asset: FootageAsset) -> dict[str, object]:
            data = asdict(asset)
            data["original"] = portable(asset.original)
            data["probe"]["path"] = portable(asset.probe.path)
            return data

        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema": "moto-motion.footage-manifest.v1",
            "generated_at": datetime.now(UTC).isoformat(),
            "assets": [asset_dict(item) for item in self.assets],
            "derived_clips": self.derived_clips,
        }
        destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return destination


class VideoAssetManager:
    """Prepare, reframe and composite footage through a single FFmpeg encode."""

    SUPPORTED_EXTENSIONS = SUPPORTED_VIDEO_EXTENSIONS

    def __init__(self, *, ffmpeg: str = "ffmpeg", ffprobe: str = "ffprobe"):
        self.ffmpeg = ffmpeg
        self.ffprobe = ffprobe

    def _run(self, command: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(command, check=True, text=True, capture_output=True)

    def probe(self, path: str | Path) -> VideoProbe:
        source = Path(path)
        if not source.is_file():
            raise FileNotFoundError(source)
        if source.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"unsupported footage extension: {source.suffix}")
        raw = self._run([
            self.ffprobe, "-v", "error", "-show_entries",
            "format=duration,size:stream=index,codec_type,codec_name,width,height,avg_frame_rate,pix_fmt:stream_tags=rotate",
            "-of", "json", str(source),
        ])
        data = json.loads(raw.stdout)
        streams = data.get("streams", [])
        video = next((stream for stream in streams if stream.get("codec_type") == "video"), None)
        if video is None:
            raise ValueError(f"not a video stream: {source}")
        audio = next((stream for stream in streams if stream.get("codec_type") == "audio"), None)
        numerator, denominator = (video.get("avg_frame_rate") or "0/1").split("/", 1)
        frame_rate = float(numerator) / max(1.0, float(denominator))
        rotation = int((video.get("tags") or {}).get("rotate", 0)) % 360
        width, height = int(video["width"]), int(video["height"])
        if rotation in {90, 270}:
            width, height = height, width
        orientation = "portrait" if height > width else "landscape" if width > height else "square"
        return VideoProbe(
            path=str(source.resolve()), width=width, height=height,
            duration_seconds=float(data["format"]["duration"]), frame_rate=frame_rate,
            codec=str(video["codec_name"]), pixel_format=video.get("pix_fmt"),
            has_audio=audio is not None, audio_codec=audio.get("codec_name") if audio else None,
            orientation=orientation, file_size_bytes=int(data["format"].get("size", source.stat().st_size)),
        )

    def register(self, asset_id: str, source: str | Path, **metadata: object) -> FootageAsset:
        return FootageAsset(asset_id=asset_id, original=str(Path(source).resolve()), probe=self.probe(source), **metadata)

    @staticmethod
    def portrait_dimensions(probe: VideoProbe) -> tuple[int, int]:
        """Largest 9:16 crop in original dimensions, retaining native resolution."""
        if probe.width / probe.height >= 9 / 16:
            return int(probe.height * 9 / 16), probe.height
        return probe.width, int(probe.width * 16 / 9)

    def crop_rect(self, probe: VideoProbe, crop: CropConfig = DEFAULT_CROP, *, at: float = 0.0) -> tuple[int, int, int, int]:
        width, height = self.portrait_dimensions(probe)
        maximum_x, maximum_y = max(0, probe.width - width), max(0, probe.height - height)
        if crop.mode == "subject_follow":
            raise ValueError("subject-following is not automatic in V1; supply reviewed keyframes instead")
        if crop.mode == "center":
            x, y = maximum_x // 2, maximum_y // 2
        elif crop.mode == "manual":
            if crop.x is None or crop.y is None:
                raise ValueError("manual crops require x and y original-pixel coordinates")
            x, y = crop.x, crop.y
        elif crop.mode == "keyframed":
            frames = sorted(crop.keyframes, key=lambda item: item.time_seconds)
            if len(frames) < 2:
                raise ValueError("keyframed crops require at least two crop keyframes")
            before, after = frames[0], frames[-1]
            for left, right in pairwise(frames):
                if left.time_seconds <= at <= right.time_seconds:
                    before, after = left, right
                    break
            amount = 0.0 if after.time_seconds == before.time_seconds else (at - before.time_seconds) / (after.time_seconds - before.time_seconds)
            amount = min(1.0, max(0.0, amount))
            x, y = round(before.x + (after.x - before.x) * amount), round(before.y + (after.y - before.y) * amount)
        else:  # pragma: no cover - Literal protects this, retained for callers deserializing JSON
            raise ValueError(f"unknown crop mode: {crop.mode}")
        return width, height, min(max(0, int(x)), maximum_x), min(max(0, int(y)), maximum_y)

    def crop_filter(self, clip: VideoClip, *, output_width: int = 1080, output_height: int = 1920) -> str:
        probe, crop = clip.source.probe, clip.crop
        crop_width, crop_height, x, y = self.crop_rect(probe, crop)
        if crop.mode != "keyframed":
            location = f"{x}:{y}"
        else:
            frames = sorted(crop.keyframes, key=lambda item: item.time_seconds)
            # FFmpeg evaluates crop x/y per-frame. Build a continuous piecewise
            # linear expression in clip-relative time; callers have already
            # reviewed each keyframe in source-pixel space.
            expressions: list[str] = []
            for left, right in pairwise(frames):
                span = max(0.001, right.time_seconds - left.time_seconds)
                fx = f"{left.x}+({right.x}-{left.x})*(t-{left.time_seconds:.6f})/{span:.6f}"
                fy = f"{left.y}+({right.y}-{left.y})*(t-{left.time_seconds:.6f})/{span:.6f}"
                expressions.append((fx, fy))
            x_expr, y_expr = expressions[-1]
            for index in range(len(expressions) - 2, -1, -1):
                at = frames[index + 1].time_seconds
                px, py = expressions[index]
                x_expr, y_expr = f"if(lt(t\\,{at:.6f})\\,{px}\\,{x_expr})", f"if(lt(t\\,{at:.6f})\\,{py}\\,{y_expr})"
            location = f"'{x_expr}':'{y_expr}'"
        filters = [f"crop={crop_width}:{crop_height}:{location}", f"scale={output_width}:{output_height}:flags=lanczos"]
        if clip.speed != 1.0:
            if clip.speed <= 0:
                raise ValueError("clip speed must be positive")
            filters.append(f"setpts=PTS/{clip.speed:.6f}")
        filters.append(f"fps={clip.output_fps:g}")
        return ",".join(filters)

    def render(self, clip: VideoClip, output: str | Path, *, output_width: int = 1080, output_height: int = 1920, crf: int = 18) -> Path:
        if clip.start_seconds < 0 or clip.end_seconds <= clip.start_seconds or clip.end_seconds > clip.source.probe.duration_seconds + 0.05:
            raise ValueError("clip timestamps lie outside the source footage")
        destination = Path(output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        command = [self.ffmpeg, "-hide_banner", "-y", "-ss", f"{clip.start_seconds:.6f}", "-i", clip.source.original, "-t", f"{clip.duration_seconds:.6f}", "-vf", self.crop_filter(clip, output_width=output_width, output_height=output_height), "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
        if clip.mute_source_audio:
            command.append("-an")
        else:
            command += ["-c:a", "aac", "-ar", "48000", "-b:a", "192k"]
        command.append(str(destination))
        self._run(command)
        return destination

    def freeze_frame(self, asset: FootageAsset, *, at: float, output: str | Path, duration_seconds: float = 1.0, crop: CropConfig = DEFAULT_CROP, output_width: int = 1080, output_height: int = 1920) -> Path:
        if duration_seconds <= 0:
            raise ValueError("freeze duration must be positive")
        probe_clip = VideoClip(asset, at, min(at + 0.001, asset.probe.duration_seconds), crop=crop)
        destination = Path(output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        self._run([self.ffmpeg, "-hide_banner", "-y", "-ss", f"{at:.6f}", "-i", asset.original, "-frames:v", "1", "-vf", self.crop_filter(probe_clip, output_width=output_width, output_height=output_height), str(destination.with_suffix(".png"))])
        png = destination.with_suffix(".png")
        self._run([self.ffmpeg, "-hide_banner", "-y", "-loop", "1", "-i", str(png), "-t", f"{duration_seconds:.6f}", "-r", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an", str(destination)])
        return destination

    def crop_preview(self, asset: FootageAsset, *, at: float, output: str | Path, crop: CropConfig = DEFAULT_CROP, width: int = 270, height: int = 480) -> Path:
        """Export a real portrait composition for editorial review, not a proxy crop."""
        preview = VideoClip(asset, at, min(at + 0.04, asset.probe.duration_seconds), crop=crop)
        destination = Path(output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        self._run([self.ffmpeg, "-hide_banner", "-y", "-ss", f"{at:.6f}", "-i", asset.original, "-frames:v", "1", "-vf", self.crop_filter(preview, output_width=width, output_height=height), str(destination)])
        return destination

    def overlay(self, video: str | Path, overlay: str | Path, output: str | Path, *, x: int = 0, y: int = 0, start_seconds: float = 0.0, end_seconds: float | None = None, keep_audio: bool = False) -> Path:
        """Composite a Manim/SVG-derived alpha video or PNG in delivered coordinates."""
        destination = Path(output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        enable = f":enable='between(t\\,{start_seconds:.3f}\\,{end_seconds:.3f})'" if end_seconds is not None else ""
        command = [self.ffmpeg, "-hide_banner", "-y", "-i", str(video), "-i", str(overlay), "-filter_complex", f"[0:v][1:v]overlay={x}:{y}{enable}[v]", "-map", "[v]"]
        command += ["-map", "0:a?", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p"] if keep_audio else ["-an", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p"]
        command.append(str(destination))
        self._run(command)
        return destination

    def source_to_portrait(self, asset: FootageAsset, x: float, y: float, *, crop: CropConfig = DEFAULT_CROP, at: float = 0.0, output_width: int = 1080, output_height: int = 1920) -> tuple[float, float]:
        """Transform an original-frame annotation coordinate into portrait pixels."""
        width, height, crop_x, crop_y = self.crop_rect(asset.probe, crop, at=at)
        return (x - crop_x) * output_width / width, (y - crop_y) * output_height / height

    def contact_sheet(self, asset: FootageAsset, output: str | Path, *, interval_seconds: float = 0.5, tile_width: int = 320, columns: int = 4) -> Path:
        if interval_seconds <= 0:
            raise ValueError("contact-sheet interval must be positive")
        destination = Path(output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        # macOS FFmpeg builds often omit drawtext.  Compose labels in Pillow so
        # contact sheets remain portable and each sampled moment remains auditable.
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError as error:  # pragma: no cover - Manim installs Pillow
            raise RuntimeError("contact sheets require Pillow (installed with Manim)") from error
        with tempfile.TemporaryDirectory(prefix="moto-motion-contact-sheet-") as temp:
            pattern = Path(temp) / "frame-%04d.png"
            filters = f"fps=1/{interval_seconds:.6f},scale={tile_width}:-2"
            self._run([self.ffmpeg, "-hide_banner", "-y", "-i", asset.original, "-vf", filters, str(pattern)])
            frames = sorted(Path(temp).glob("frame-*.png"))
            if not frames:
                raise RuntimeError(f"no sampled frames produced for {asset.original}")
            first = Image.open(frames[0]).convert("RGB")
            tile_height = first.height
            label_height, padding = 32, 8
            rows = math.ceil(len(frames) / columns)
            canvas = Image.new("RGB", (columns * (tile_width + padding) + padding, rows * (tile_height + label_height + padding) + padding), "#0B1118")
            font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
            font = ImageFont.truetype(font_path, 19) if Path(font_path).is_file() else ImageFont.load_default()
            draw = ImageDraw.Draw(canvas)
            for index, frame_path in enumerate(frames):
                frame = Image.open(frame_path).convert("RGB")
                column, row = index % columns, index // columns
                x, y = padding + column * (tile_width + padding), padding + row * (tile_height + label_height + padding)
                canvas.paste(frame, (x, y))
                draw.rectangle((x, y, x + 116, y + 29), fill="#000000")
                draw.text((x + 7, y + 4), f"{index * interval_seconds:05.2f}s", fill="white", font=font)
            canvas.save(destination)
        return destination
