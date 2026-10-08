"""Narration for the SCAYL ad: one WAV per line of narration.json + durations.json (used by record.py).

    python tools/ad/voice.py edge es-PA-RobertoNeural          # Microsoft neural voices (needs internet)
    python tools/ad/voice.py kokoro 29 --model <kokoro-dir>    # local Kokoro via sherpa-onnx (29 = em_alex)
    python tools/ad/voice.py edge es-PA-RobertoNeural --only c3,cierre   # regenerate some lines

edge: `pip install edge-tts`; needs ffmpeg in PATH. Good Spanish voices: es-PA-RobertoNeural,
es-PA-MargaritaNeural (Panamá), es-MX-JorgeNeural, es-MX-DaliaNeural.
kokoro: `pip install sherpa-onnx`; model from
https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-multi-lang-v1_0.tar.bz2
(Spanish speakers: 28 ef_dora, 29 em_alex, 53 em_santa).
"""
import argparse
import asyncio
import json
import subprocess
import tempfile
import wave
from pathlib import Path

HERE = Path(__file__).parent


def write_wav(path: Path, samples, rate: int) -> float:
    import numpy as np
    x = np.asarray(samples, dtype=np.float64)
    x = np.clip(x * 0.95 / (np.abs(x).max() + 1e-9), -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes((x * 32767).astype("<i2").tobytes())
    return round(len(x) / rate, 2)


def wav_seconds(path: Path) -> float:
    with wave.open(str(path)) as w:
        return round(w.getnframes() / w.getframerate(), 2)


async def edge_mp3(text: str, voice: str, rate: str, mp3: Path) -> None:
    import edge_tts
    await edge_tts.Communicate(text, voice, rate=rate).save(str(mp3))


def edge(lines: dict, voice: str, rate: str, out: Path) -> dict:
    durs = {}
    for key, text in lines.items():
        with tempfile.TemporaryDirectory() as tmp:
            mp3 = Path(tmp) / f"{key}.mp3"
            asyncio.run(edge_mp3(text, voice, rate, mp3))
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp3), "-ac", "1", "-ar", "44100",
                            str(out / f"{key}.wav")], check=True)
        durs[key] = wav_seconds(out / f"{key}.wav")
        print(key, durs[key])
    return durs


def kokoro(lines: dict, sid: int, model: Path, speed: float, out: Path) -> dict:
    import sherpa_onnx
    cfg = {"model": str(model / "model.onnx"), "voices": str(model / "voices.bin"), "tokens": str(model / "tokens.txt"),
           "data_dir": str(model / "espeak-ng-data"), "dict_dir": str(model / "dict"),
           "lexicon": f"{model / 'lexicon-us-en.txt'},{model / 'lexicon-zh.txt'}"}
    try:
        k = sherpa_onnx.OfflineTtsKokoroModelConfig(**cfg, lang="es")
    except TypeError:
        k = sherpa_onnx.OfflineTtsKokoroModelConfig(**cfg)
    tts = sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(kokoro=k, num_threads=4), max_num_sentences=4))
    durs = {}
    for key, text in lines.items():
        a = tts.generate(text, sid=sid, speed=speed)
        durs[key] = write_wav(out / f"{key}.wav", a.samples, a.sample_rate)
        print(key, durs[key])
    return durs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("engine", choices=["edge", "kokoro"])
    ap.add_argument("voice", help="edge voice name, or kokoro speaker id")
    ap.add_argument("--rate", default="+0%", help="edge speaking rate, e.g. +5%%")
    ap.add_argument("--speed", type=float, default=1.0, help="kokoro speed")
    ap.add_argument("--model", type=Path, help="kokoro model directory")
    ap.add_argument("--text", type=Path, default=HERE / "narration.json")
    ap.add_argument("--out", type=Path, default=HERE / "build" / "voice")
    ap.add_argument("--only", help="comma-separated keys to regenerate")
    args = ap.parse_args()
    lines = json.loads(args.text.read_text(encoding="utf-8"))
    if args.only:
        lines = {k: lines[k] for k in args.only.split(",")}
    args.out.mkdir(parents=True, exist_ok=True)
    durs = (edge(lines, args.voice, args.rate, args.out) if args.engine == "edge"
            else kokoro(lines, int(args.voice), args.model, args.speed, args.out))
    dpath = args.out / "durations.json"
    all_durs = json.loads(dpath.read_text()) if dpath.exists() else {}
    all_durs.update(durs)
    dpath.write_text(json.dumps(all_durs, indent=1))


if __name__ == "__main__":
    main()
