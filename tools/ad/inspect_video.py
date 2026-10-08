"""Let an agent "watch" and "listen to" the ad: contact sheets of frames + transcript of the narration.

    python tools/ad/inspect_video.py tools/ad/build/SCAYL_anuncio.mp4                 # sheets every 4 s
    python tools/ad/inspect_video.py video.mp4 --every 2 --start 60 --end 90          # zoom into a section
    python tools/ad/inspect_video.py video.mp4 --transcribe                           # also check the voice

Writes tools/ad/build/inspect/sheet_XX.png (3x4 frames with timestamps). Open those images to review layout,
captions and sync. --transcribe needs `pip install faster-whisper` (downloads a small model once) and
prints the recognized speech with timestamps, to verify that the voice is intelligible over the music.
"""
import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).parent


def duration(video: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(video)],
                         capture_output=True, text=True, check=True).stdout
    return float(json.loads(out)["format"]["duration"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("video", type=Path)
    ap.add_argument("--every", type=float, default=4.0)
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float)
    ap.add_argument("--out", type=Path, default=HERE / "build" / "inspect")
    ap.add_argument("--transcribe", action="store_true")
    args = ap.parse_args()
    end = args.end or duration(args.video)
    args.out.mkdir(parents=True, exist_ok=True)
    for old in args.out.glob("*.png"):
        old.unlink()
    times, t = [], args.start
    while t < end:
        times.append(round(t, 2)); t += args.every
    frames = []
    for i, ts in enumerate(times):
        f = args.out / f"frame_{i:03d}.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ts), "-i", str(args.video), "-frames:v", "1",
                        "-vf", "scale=640:-1", str(f)], check=True)
        im = Image.open(f).convert("RGB"); d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 92, 26], fill=(0, 0, 0)); d.text((6, 6), f"{ts:7.1f}s", fill=(255, 220, 0))
        frames.append(im); f.unlink()
    per = 12
    for s in range(0, len(frames), per):
        chunk = frames[s:s + per]; w, h = chunk[0].size
        sheet = Image.new("RGB", (w * 3, h * ((len(chunk) + 2) // 3)), "white")
        for j, im in enumerate(chunk):
            sheet.paste(im, ((j % 3) * w, (j // 3) * h))
        path = args.out / f"sheet_{s // per:02d}.png"; sheet.save(path); print(path)
    if args.transcribe:
        from faster_whisper import WhisperModel
        model = WhisperModel("base", compute_type="int8")
        segments, _ = model.transcribe(str(args.video), language="es")
        for seg in segments:
            print(f"[{seg.start:6.1f}-{seg.end:6.1f}] {seg.text.strip()}")


if __name__ == "__main__":
    main()
