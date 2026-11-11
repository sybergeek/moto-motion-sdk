# Moto Motion SFX system

The opt-in SFX system lives in `moto_motion.audio`. Existing projects remain silent unless they create an `SFXScheduler` and export a mix.

## Workflow

1. Put source recordings outside `assets/sfx/processed`; sources remain immutable.
2. Add source metadata and neutral event candidates to `scripts/build_sfx_library.py`.
3. Run `python scripts/build_sfx_library.py` to produce 48 kHz, faded, conservatively normalized clips plus source/processing manifests.
4. Load `assets/sfx/manifests/registry.json` with `SFXRegistry`.
5. Use `SFXScheduler(mode="hybrid")` with `.emit()` for semantic events and `.play()` for explicit overrides.
6. Use `SFXMixer` with narration and scheduled cues; it keeps narration first and applies final loudness normalization.

## Modes

- `off`: no cues.
- `auto`: semantic event mapping only.
- `manual`: `.play()` calls only.
- `hybrid`: explicit and automatic events; recommended for new projects.

Vehicle IDs are deliberately `motorsport.generic.*` unless provenance establishes a specific series. The supplied source recordings are documented under the Pixabay Content License and are not to be redistributed through a public repository without confirming the current license terms.

## Audition and demo

Run `python scripts/build_sfx_audition.py` for `media/sfx_audition/index.html`, and `bash scripts/render_sfx_demo.sh` to create paired SFX-on/off demo videos plus `media/sfx_demo/timeline.json`.

## Narration-first mixing

`AudioMixConfig` defaults to narration priority, SFX ducking, and phrase-gap scheduling. Its project-safe defaults are stored in `assets/sfx/manifests/default_audio_config.json`:

- UI accents target a 6 dB reduction during detected speech.
- Transitions target 9 dB, impacts 10 dB, and generic vehicle effects 15 dB.
- A +12 dB SFX-bus makeup gain compensates for the source library's conservative -20 LUFS normalization; ducking is applied relative to that audible bus level.
- Essential vehicle events retain their visual timeline time; flexible accents may move by at most 150 ms into a meaningful speech gap; decorative events can be suppressed in dense speech.
- FFmpeg side-chain compression applies smooth 40 ms attack and 250 ms release. Its sidechain control is advanced by 50 ms, allowing the gain envelope to begin before narration without moving the audible essential effect away from its visual event.

Use real word alignment when supplied in `alignment.word_timestamps`. A manifest marked provisional, or one without word timestamps, falls back to deterministic RMS speech detection with hysteresis and a 350 ms minimum phrase gap. Provisional scene boundaries are never used as speech timing.

```python
from moto_motion.audio import AudioMixConfig, SFXMixer, SpeechDetector

speech = SpeechDetector().detect("media/audio/my_reel/narration.wav", manifest="examples/my_reel.narration.json")
SFXMixer(registry, config=AudioMixConfig()).mix(
    "media/audio/my_reel/narration.wav", cues, "media/audio/my_reel/final.wav",
    speech_regions=speech, stems_dir="media/audio/my_reel/stems",
    report_path="media/audio/my_reel/mix-report.json",
)
```

`bash scripts/render_sfx_narration_demo.sh` creates matched baseline and narration-aware videos, isolated narration/SFX/music stems, and per-cue reports under `media/sfx_narration_demo/`. Existing reels do not opt in automatically.
