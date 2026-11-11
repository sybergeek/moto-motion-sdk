"""Non-destructive footage preparation for hybrid Moto Motion productions."""

from .assets import (
    CropConfig,
    CropKeyframe,
    FootageAsset,
    FootageManifest,
    VideoAssetManager,
    VideoClip,
    VideoProbe,
)
from .audio import VerifiedFootageAction, emit_verified_footage_sfx

__all__ = [
    "CropConfig",
    "CropKeyframe",
    "FootageAsset",
    "FootageManifest",
    "VerifiedFootageAction",
    "VideoAssetManager",
    "VideoClip",
    "VideoProbe",
    "emit_verified_footage_sfx",
]
