"""Generate portable HTML/audio waveform audition artifacts for the SFX registry."""

from __future__ import annotations

import html
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "assets/sfx/manifests/registry.json"
OUTPUT = ROOT / "media/sfx_audition"


def main() -> None:
    registry = json.loads(REGISTRY.read_text())
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for asset in registry["assets"]:
        sound = ROOT / asset["file"]
        waveform = OUTPUT / f"{asset['id'].replace('.', '_')}.png"
        subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", str(sound), "-filter_complex", "showwavespic=s=900x140:colors=1bc7ba", "-frames:v", "1", str(waveform)], check=True, capture_output=True)
        rel_sound = Path("../../") / asset["file"]
        rows.append(f"<article><h2>{html.escape(asset['name'])}</h2><p><code>{html.escape(asset['id'])}</code> · {asset['duration_seconds']} s · {html.escape(asset['category'])}</p><img src='{waveform.name}' alt='waveform'><audio controls preload='none' src='{rel_sound.as_posix()}'></audio><p>{html.escape(', '.join(asset['tags']))}</p></article>")
    body = "".join(rows)
    (OUTPUT / "index.html").write_text(f"<!doctype html><meta charset='utf-8'><title>Moto Motion SFX audition</title><style>body{{font:16px system-ui;background:#0a1019;color:#f4f7fa;max-width:950px;margin:auto;padding:28px}}article{{background:#142130;margin:16px 0;padding:18px;border-radius:12px}}img{{display:block;width:100%;background:#061018}}audio{{width:100%;margin-top:12px}}code{{color:#1bc7ba}}</style><h1>Moto Motion SFX Audition</h1><p>Processed, registry-backed clips. Originals are preserved separately and are not rehosted here.</p>{body}", encoding="utf-8")


if __name__ == "__main__":
    main()
