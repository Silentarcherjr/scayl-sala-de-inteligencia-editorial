"""Render the SCAYL ad end to end: record the site -> mix the soundtrack -> MP4 (H.264 + AAC, 1080p).

    python tools/ad/make_ad.py                       # uses tools/ad/build/voice (run voice.py first)
    python tools/ad/make_ad.py --silent              # no audio (subtitles only)
    AD_BASE_URL=https://scayl-editorial.vercel.app python tools/ad/make_ad.py

Output: tools/ad/build/SCAYL_anuncio.mp4 (tools/ad/build/ is ignored by git).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
BUILD = HERE / "build"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--silent", action="store_true")
    ap.add_argument("--out", type=Path, default=BUILD / "SCAYL_anuncio.mp4")
    args = ap.parse_args()
    raw = BUILD / "raw"
    shutil.rmtree(raw, ignore_errors=True); raw.mkdir(parents=True)
    voice = Path(os.environ.get("AD_VOICE_DIR", BUILD / "voice"))
    if not (voice / "durations.json").exists():
        sys.exit("Falta la narración: ejecuta primero tools/ad/voice.py (o crea durations.json con 0 para --silent).")
    subprocess.run([sys.executable, str(HERE / "record.py"), str(raw)], check=True)
    video = next(raw.glob("*.webm"))
    dur = float(json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json",
                                           str(video)], capture_output=True, text=True, check=True).stdout)["format"]["duration"])
    vf = f"fade=t=in:st=0:d=0.6,fade=t=out:st={dur - 1.2:.2f}:d=1.2,format=yuv420p"
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(video)]
    if not args.silent:
        wav = BUILD / "soundtrack.wav"
        subprocess.run([sys.executable, str(HERE / "mix.py"), str(raw / "events.json"), str(dur), str(wav), str(voice)],
                       check=True)
        cmd += ["-i", str(wav), "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-vf", vf, "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-r", "30", "-movflags", "+faststart",
            str(args.out)]
    subprocess.run(cmd, check=True)
    print(f"Listo: {args.out} ({dur:.1f} s). Revísalo con: python tools/ad/inspect_video.py {args.out}")


if __name__ == "__main__":
    main()
