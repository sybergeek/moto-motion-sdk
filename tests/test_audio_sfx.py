from pathlib import Path

from moto_motion.audio.builtin import write_builtin_library
from moto_motion.audio.events import SFXScheduler, SoundMode
from moto_motion.audio.ingest import IngestConfig, SFXIngestor
from moto_motion.audio.mix import SFXMixer
from moto_motion.audio.narration import SpeechRegion, speech_gaps
from moto_motion.audio.events import SFXCue, SFXPriority


def test_builtin_library_is_deterministic_and_48khz(tmp_path: Path):
    first = write_builtin_library(tmp_path)
    second = write_builtin_library(tmp_path)
    assert len(first) == len(second) == 15
    assert all(asset["sample_rate"] == 48000 for asset in first)
    assert all((tmp_path / asset["file"]).is_file() for asset in first)


def test_event_scheduler_honours_mode_cooldown_and_tick_bound():
    scheduler = SFXScheduler(SoundMode.HYBRID, cooldown_seconds=0.2)
    assert scheduler.emit("text.pop", at=1.0)
    assert scheduler.emit("text.pop", at=1.1) is None
    assert len(scheduler.counter(start=2, duration=1, ticks=100)) == 9
    assert SFXScheduler(SoundMode.OFF).emit("text.pop", at=0) is None


def test_ingest_defaults_are_conservative():
    config = IngestConfig()
    assert config.sample_rate == 48000
    assert config.silence_db == -40.0
    assert config.context_seconds > 0


def test_supported_source_formats_are_explicit():
    assert SFXIngestor.SUPPORTED_EXTENSIONS == {".wav", ".mp3", ".flac", ".ogg", ".m4a"}


def test_speech_gaps_ignore_word_scale_pauses():
    gaps = speech_gaps([SpeechRegion(0.0, 0.2, "test"), SpeechRegion(0.3, 0.5, "test"), SpeechRegion(1.0, 1.2, "test")], 2.0, minimum_seconds=0.35)
    assert gaps == [(0.5, 1.0), (1.2, 2.0)]


def test_planner_shifts_only_flexible_cues_and_keeps_essential_sync():
    class Registry:
        def get(self, _sfx_id):
            return {"duration_seconds": 0.1, "category": "motorsport.generic"}

    mixer = SFXMixer(Registry())
    regions = [SpeechRegion(0.4, 1.0, "test")]
    flexible = SFXCue("cue", at=0.95, priority=SFXPriority.FLEXIBLE)
    essential = SFXCue("cue", at=0.95, priority=SFXPriority.ESSENTIAL)
    planned = mixer.plan([flexible, essential], regions, narration_duration=1.5)
    assert planned[0].scheduled_at == 1.0
    assert planned[0].status == "shifted"
    assert planned[1].scheduled_at == 0.95
    assert planned[1].duck_target_db == -15.0
