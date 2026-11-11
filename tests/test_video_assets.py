from pathlib import Path

import pytest

from moto_motion.audio import SFXScheduler
from moto_motion.video import (
    CropConfig,
    CropKeyframe,
    FootageAsset,
    VerifiedFootageAction,
    VideoAssetManager,
    VideoClip,
    VideoProbe,
    emit_verified_footage_sfx,
)


def probe(width: int = 1920, height: int = 1080) -> VideoProbe:
    return VideoProbe("assets/footage/source.mp4", width, height, 8.0, 59.94, "h264", "yuv420p", True, "aac", "landscape", 100)


def asset() -> FootageAsset:
    return FootageAsset("test", "assets/footage/source.mp4", probe())


def test_center_crop_is_largest_916_region():
    manager = VideoAssetManager()
    assert manager.crop_rect(probe()) == (607, 1080, 656, 0)


def test_manual_and_keyframed_crops_are_clamped_and_interpolated():
    manager = VideoAssetManager()
    assert manager.crop_rect(probe(), CropConfig("manual", x=10_000, y=-3)) == (607, 1080, 1313, 0)
    crop = CropConfig("keyframed", keyframes=(CropKeyframe(0, 10, 0), CropKeyframe(2, 110, 0)))
    assert manager.crop_rect(probe(), crop, at=1) == (607, 1080, 60, 0)


def test_subject_following_requires_reviewed_keyframes():
    with pytest.raises(ValueError, match="keyframes"):
        VideoAssetManager().crop_rect(probe(), CropConfig("subject_follow"))


def test_crop_filter_is_portrait_and_respects_slow_motion():
    clip = VideoClip(asset(), 0, 2, speed=0.5)
    text = VideoAssetManager().crop_filter(clip)
    assert "crop=607:1080:656:0" in text
    assert "scale=1080:1920" in text
    assert "setpts=PTS/0.500000" in text


def test_only_documented_video_extensions_are_supported(tmp_path: Path):
    invalid = tmp_path / "not-video.wav"
    invalid.write_bytes(b"x")
    with pytest.raises(ValueError, match="unsupported"):
        VideoAssetManager().probe(invalid)


def test_verified_footage_event_uses_existing_sfx_scheduler():
    cue = emit_verified_footage_sfx(
        SFXScheduler(), VerifiedFootageAction("flyby", at=1.2, confidence="high", closest_approach_time=1.4)
    )
    assert cue is not None
    assert cue.event == "vehicle.flyby"
    assert cue.closest_approach_time == 1.4
