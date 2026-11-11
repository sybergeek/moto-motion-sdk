"""Opt-in SFX ingestion, scheduling, registry and mixing utilities."""

from .events import SFXCue, SFXPriority, SFXScheduler, SoundMode
from .ingest import IngestConfig, SFXIngestor
from .mix import AudioMixConfig, SFXMixer
from .narration import SpeechDetectionConfig, SpeechDetector, SpeechRegion, speech_gaps
from .registry import SFXRegistry

__all__ = ["AudioMixConfig", "IngestConfig", "SFXCue", "SFXIngestor", "SFXMixer", "SFXPriority", "SFXRegistry", "SFXScheduler", "SoundMode", "SpeechDetectionConfig", "SpeechDetector", "SpeechRegion", "speech_gaps"]
