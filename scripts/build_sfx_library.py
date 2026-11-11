"""Build the local, non-destructive SFX library from user-provided recordings."""

from __future__ import annotations

import json
from pathlib import Path

from moto_motion.audio.builtin import write_builtin_library
from moto_motion.audio.ingest import SFXIngestor


ROOT = Path(__file__).resolve().parents[1]
SFX_ROOT = ROOT / "assets/sfx"

SOURCES = [
    {
        "id": "motorsport.generic.vehicle_pass.fast",
        "name": "Fast generic vehicle pass",
        "source": ROOT / "assets/moeeza3-fast-car-passing-sound-395038.mp3",
        "creator": "moeeza3",
        "url": "https://pixabay.com/ja/sound-effects/%E5%B8%82-fast-car-passing-sound-395038/",
        "license": "Pixabay Content License",
        "download_date": "2026-11-07",
        "redistribution": "not established; exclude source and derived audio from public repositories",
        "start": 0.344, "end": 4.047,
        "tags": ["vehicle", "generic", "fast", "pass", "whoosh"],
        "recommended_events": ["vehicle.flyby"],
    },
    {
        "id": "motorsport.generic.vehicle_pass.race",
        "name": "Race-style generic vehicle pass",
        "source": ROOT / "assets/soundreality-f1-151254.mp3",
        "creator": "SoundReality",
        "url": "https://pixabay.com/sound-effects/film-special-effects-f1-151254/",
        "license": "Pixabay Content License",
        "download_date": "2026-11-07",
        "redistribution": "not established; exclude source and derived audio from public repositories",
        "start": 0.0, "end": 3.619,
        "tags": ["vehicle", "generic", "race", "pass", "engine"],
        "recommended_events": ["vehicle.accelerate", "vehicle.flyby"],
    },
]


def main() -> None:
    ingestor = SFXIngestor()
    assets = write_builtin_library(ROOT)
    source_manifest = []
    for source in SOURCES:
        output = SFX_ROOT / "processed/motorsport/generic" / f"{source['id'].split('.')[-1]}.wav"
        processing = ingestor.extract(source["source"], output, source["start"], source["end"])
        processing["source_file"] = source["source"].relative_to(ROOT).as_posix()
        info = ingestor.inspect(output)
        stream = info["streams"][0]
        assets.append({
            "id": source["id"], "name": source["name"], "category": "motorsport.generic.vehicle_pass", "file": output.relative_to(ROOT).as_posix(),
            "duration_seconds": round(source["end"] - source["start"], 3), "sample_rate": int(stream["sample_rate"]), "channels": int(stream["channels"]),
            "default_gain_db": -14, "tags": source["tags"], "source": {"original_file": source["source"].relative_to(ROOT).as_posix(), "start_seconds": source["start"], "end_seconds": source["end"], "creator": source["creator"], "url": source["url"], "license": source["license"], "download_date": source["download_date"], "redistribution": source["redistribution"], "attribution": "Not required by the Pixabay Content License; creator credit retained in manifest."},
            "processing": processing, "recommended_events": source["recommended_events"],
        })
        inspection = ingestor.inspect(source["source"])
        inspection["source"] = source["source"].relative_to(ROOT).as_posix()
        source_manifest.append({
            **{key: value for key, value in source.items() if key != "source"},
            "source": source["source"].relative_to(ROOT).as_posix(),
            "analysis": {"inspection": inspection, "silence_regions": ingestor.silence_regions(source["source"]), "candidate_events": ingestor.candidate_events(source["source"])},
        })
    (SFX_ROOT / "manifests").mkdir(parents=True, exist_ok=True)
    (SFX_ROOT / "manifests/registry.json").write_text(json.dumps({"schema": "moto-motion.sfx-registry.v1", "assets": assets}, indent=2) + "\n")
    (SFX_ROOT / "manifests/sources.json").write_text(json.dumps({"schema": "moto-motion.sfx-sources.v1", "sources": source_manifest}, indent=2) + "\n")


if __name__ == "__main__":
    main()
