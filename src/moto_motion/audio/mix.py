"""Narration-first FFmpeg mixing with priority-aware SFX planning."""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

from .events import SFXCue, SFXPriority
from .narration import SpeechRegion, speech_gaps
from .registry import SFXRegistry


@dataclass(frozen=True)
class AudioMixConfig:
    narration_priority: bool = True
    auto_ducking: bool = True
    speech_gap_scheduling: bool = True
    global_sfx_gain_db: float = -3.0
    sfx_bus_gain_db: float = 12.0
    ui_duck_db: float = -6.0
    transition_duck_db: float = -9.0
    vehicle_duck_db: float = -15.0
    impact_duck_db: float = -10.0
    attack_ms: int = 40
    release_ms: int = 250
    lookahead_ms: int = 50
    minimum_speech_gap_seconds: float = 0.35
    dynamic_eq_engines: bool = False


@dataclass(frozen=True)
class PlannedCue:
    cue: SFXCue
    scheduled_at: float
    duck_target_db: float = 0.0
    status: str = "kept"
    reason: str = ""


class SFXMixer:
    """Mix narration, music and SFX while retaining visual-event timing."""

    def __init__(self, registry: SFXRegistry, *, global_gain_db: float = 0.0, config: AudioMixConfig = AudioMixConfig()):
        self.registry = registry
        self.global_gain_db = global_gain_db
        self.config = config
        self.last_report: dict[str, object] = {}

    def _duration(self, sfx_id: str, speed: float) -> float:
        return float(self.registry.get(sfx_id)["duration_seconds"]) / max(0.5, min(2.0, speed))

    def _duck_target(self, cue: SFXCue) -> float:
        event = cue.event or ""
        category = self.registry.get(cue.sfx_id).get("category", "")
        if event.startswith("vehicle.") or category.startswith("motorsport"):
            return self.config.vehicle_duck_db
        if "impact" in event or event in {"trophy.reveal", "comparison.resolve"}:
            return self.config.impact_duck_db
        if "slide" in event or "reveal" in event or "enter" in event:
            return self.config.transition_duck_db
        return self.config.ui_duck_db

    @staticmethod
    def _overlaps(start: float, end: float, regions: list[SpeechRegion]) -> bool:
        return any(start < region.end and end > region.start for region in regions)

    def plan(self, cues: list[SFXCue], speech_regions: list[SpeechRegion], narration_duration: float) -> list[PlannedCue]:
        """Shift only flexible accents into phrase gaps; preserve essential sync."""
        gaps = speech_gaps(speech_regions, narration_duration, minimum_seconds=self.config.minimum_speech_gap_seconds)
        planned: list[PlannedCue] = []
        for cue in sorted(cues, key=lambda item: item.at):
            duration = self._duration(cue.sfx_id, cue.speed)
            overlaps = self._overlaps(cue.at, cue.at + duration, speech_regions)
            nearby = sum(abs(item.scheduled_at - cue.at) < 0.10 for item in planned if item.status != "suppressed")
            if cue.priority == SFXPriority.DECORATIVE and (overlaps or nearby >= 2):
                planned.append(PlannedCue(cue, cue.at, status="suppressed", reason="decorative effect conflicts with narration or a dense SFX moment"))
                continue
            if cue.priority == SFXPriority.FLEXIBLE and overlaps and self.config.speech_gap_scheduling:
                candidates = []
                for gap_start, gap_end in gaps:
                    if gap_end - gap_start < min(duration, 0.15):
                        continue
                    candidate = min(max(cue.at, gap_start), gap_end - min(duration, 0.15))
                    if abs(candidate - cue.at) <= cue.shift_tolerance:
                        candidates.append(candidate)
                if candidates:
                    shifted = min(candidates, key=lambda item: abs(item - cue.at))
                    planned.append(PlannedCue(cue, shifted, status="shifted", reason="moved into a meaningful narration gap"))
                    continue
            duck = self._duck_target(cue) if overlaps and self.config.narration_priority and self.config.auto_ducking else 0.0
            reason = "essential synchronized effect retained" if cue.priority == SFXPriority.ESSENTIAL else "kept at visual event"
            if duck:
                reason += "; narration-aware ducking applied"
            planned.append(PlannedCue(cue, cue.at, duck_target_db=duck, reason=reason))
        return planned

    @staticmethod
    def _audio_duration(path: Path) -> float:
        raw = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)], check=True, text=True, capture_output=True).stdout
        return float(raw.strip())

    @staticmethod
    def _portable_path(path: Path) -> str:
        return os.path.relpath(path.resolve(), Path.cwd())

    def mix(self, narration: str | Path, cues: list[SFXCue], output: str | Path, *, music: str | Path | None = None, speech_regions: list[SpeechRegion] | None = None, config: AudioMixConfig | None = None, stems_dir: str | Path | None = None, report_path: str | Path | None = None) -> Path:
        narration, output = Path(narration), Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        active_config = config or self.config
        if active_config != self.config:
            mixer = SFXMixer(self.registry, global_gain_db=self.global_gain_db, config=active_config)
            result = mixer.mix(narration, cues, output, music=music, speech_regions=speech_regions, stems_dir=stems_dir, report_path=report_path)
            self.last_report = mixer.last_report
            return result
        duration = self._audio_duration(narration)
        regions = speech_regions or []
        planned = self.plan(cues, regions, duration) if active_config.narration_priority else [PlannedCue(cue, cue.at, reason="narration priority disabled") for cue in cues]
        active = [item for item in planned if item.status != "suppressed"]
        inputs = ["ffmpeg", "-hide_banner", "-y", "-i", str(narration)]
        music_index = None
        if music:
            music_index = 1
            inputs += ["-i", str(music)]
        source_index = 1 + int(music is not None)
        for item in active:
            inputs += ["-i", str(self.registry.file_path(item.cue.sfx_id))]

        stem_requested = stems_dir is not None
        duck_count = sum(item.duck_target_db != 0.0 for item in active)
        filter_parts = ["[0:a]aresample=48000,pan=stereo|c0=c0|c1=c1[narration_base]"]
        if duck_count:
            filter_parts.append("[narration_base]asplit=2[narration_program][narration_lookahead_input]")
            lookahead_seconds = active_config.lookahead_ms / 1000
            side_labels = "".join(f"[narration_side_{index}]" for index in range(duck_count))
            filter_parts.append(f"[narration_lookahead_input]atrim=start={lookahead_seconds:.3f},asetpts=PTS-STARTPTS,asplit={duck_count}{side_labels}")
        else:
            filter_parts.append("[narration_base]anull[narration_program]")
        narration_outputs = ["narration_final"]
        if music_index is not None:
            narration_outputs.append("narration_music")
        if stem_requested:
            narration_outputs.append("narration_stem")
        filter_parts.append(f"[narration_program]asplit={len(narration_outputs)}{''.join(f'[{label}]' for label in narration_outputs)}")
        labels = ["[narration_final]"]
        music_stem_label = None
        if music_index is not None:
            filter_parts.append(f"[{music_index}:a]aresample=48000,volume=-18dB[music_raw]")
            filter_parts.append("[music_raw][narration_music]sidechaincompress=threshold=0.015:ratio=8:attack=20:release=250[music_mix]")
            if stem_requested:
                filter_parts.append("[music_mix]asplit=2[music_bus][music_stem]")
                music_stem_label = "[music_stem]"
                labels.append("[music_bus]")
            else:
                labels.append("[music_mix]")

        sfx_labels: list[str] = []
        duck_index = 0
        for offset, item in enumerate(active):
            cue = item.cue
            index = source_index + offset
            delay = max(0, round(item.scheduled_at * 1000))
            pan_left = max(0.0, min(1.0, 0.5 - cue.pan / 2))
            pan_right = max(0.0, min(1.0, 0.5 + cue.pan / 2))
            gain = cue.gain_db + self.global_gain_db + active_config.global_sfx_gain_db + active_config.sfx_bus_gain_db
            cue_duration = self._duration(cue.sfx_id, cue.speed)
            fade_out_start = max(0.0, cue_duration - cue.fade_out)
            base = f"[{index}:a]aresample=48000,atempo={max(0.5, min(2.0, cue.speed)):.3f},volume={gain:.2f}dB,afade=t=in:st=0:d={cue.fade_in:.3f},afade=t=out:st={fade_out_start:.3f}:d={cue.fade_out:.3f},pan=stereo|c0={pan_left:.3f}*c0|c1={pan_right:.3f}*c1,adelay={delay}|{delay},apad=pad_dur={duration:.6f}"
            if item.duck_target_db:
                # The narration sidechain is normalized and sits ~30 dB above the
                # compressor threshold; this mapping yields approximately the
                # configured 6/9/10/15 dB reductions without crushing the SFX bus.
                ratio = 1.0 + abs(item.duck_target_db) / 30.0
                filter_parts.append(f"{base}[duck_source_{offset}]")
                filter_parts.append(f"[duck_source_{offset}][narration_side_{duck_index}]sidechaincompress=threshold=0.015:ratio={ratio:.2f}:attack={active_config.attack_ms}:release={active_config.release_ms}[s{offset}]")
                duck_index += 1
            else:
                filter_parts.append(f"{base}[s{offset}]")
            sfx_labels.append(f"[s{offset}]")

        if sfx_labels:
            filter_parts.append(f"{''.join(sfx_labels)}amix=inputs={len(sfx_labels)}:duration=longest:normalize=0,atrim=duration={duration:.6f},asetpts=N/SR/TB[sfx_raw]")
        else:
            filter_parts.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={duration:.6f}[sfx_raw]")
        if stem_requested:
            filter_parts.append("[sfx_raw]asplit=2[sfx_bus][sfx_stem]")
            labels.append("[sfx_bus]")
        else:
            labels.append("[sfx_raw]")
        filter_parts.append(f"{''.join(labels)}amix=inputs={len(labels)}:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[mix]")

        command = inputs + ["-filter_complex", ";".join(filter_parts), "-map", "[mix]", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", str(output)]
        stems: dict[str, str] = {}
        if stem_requested:
            stem_root = Path(stems_dir)
            stem_root.mkdir(parents=True, exist_ok=True)
            narration_stem, sfx_stem = stem_root / "narration.wav", stem_root / "sfx.wav"
            command += ["-map", "[narration_stem]", "-c:a", "pcm_s16le", str(narration_stem), "-map", "[sfx_stem]", "-c:a", "pcm_s16le", str(sfx_stem)]
            stems = {"narration": self._portable_path(narration_stem), "sfx": self._portable_path(sfx_stem)}
            if music_stem_label:
                music_stem = stem_root / "music.wav"
                command += ["-map", music_stem_label, "-c:a", "pcm_s16le", str(music_stem)]
                stems["music"] = self._portable_path(music_stem)
        subprocess.run(command, check=True)
        if stem_requested and "music" not in stems:
            music_stem = Path(stems_dir) / "music.wav"
            subprocess.run(["ffmpeg", "-hide_banner", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{duration:.6f}", str(music_stem)], check=True)
            stems["music"] = self._portable_path(music_stem)
        self.last_report = {
            "schema": "moto-motion.audio-mix-report.v1", "config": asdict(active_config), "narration_duration_seconds": duration,
            "speech_regions": [item.__dict__ for item in regions],
            "planned_cues": [{"sfx_id": item.cue.sfx_id, "event": item.cue.event, "priority": item.cue.priority.value, "original_at": item.cue.at, "scheduled_at": item.scheduled_at, "duck_target_db": item.duck_target_db, "status": item.status, "reason": item.reason} for item in planned], "stems": stems,
        }
        if report_path:
            report = Path(report_path)
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(json.dumps(self.last_report, indent=2) + "\n", encoding="utf-8")
        return output
