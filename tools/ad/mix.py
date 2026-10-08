"""Original soundtrack for the SCAYL ad: generated music + SFX + narration, with voice ducking.

    python tools/ad/mix.py <events.json> <video_seconds> <out.wav> [voice_dir]
Music and effects are synthesized here (no third-party audio, no rights issues).
"""
import json
import sys
import wave
from pathlib import Path

import numpy as np

SR = 44100
VOICE = Path(sys.argv[4]) if len(sys.argv) > 4 else Path(__file__).parent / "build" / "voice"
events = json.loads(Path(sys.argv[1]).read_text())
video_dur = float(sys.argv[2])
out = Path(sys.argv[3])
offset = video_dur - next(e["t"] for e in events if e["kind"] == "end")  # align log clock to video clock
N = int((video_dur + 0.5) * SR)
rng = np.random.default_rng(7)


def t_axis(sec):
    return np.arange(int(sec * SR)) / SR


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x):  # small signals only (SFX); music uses FFT filter below
        acc = (1 - a) * v + a * acc; y[i] = acc
    return y


def fft_lowpass(x, cutoff):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))


def midi(n):
    return 440 * 2 ** ((n - 69) / 12)


# ---------- music: calm, confident "newsroom tech" bed, 96 BPM ----------
bpm = 96; beat = 60 / bpm; bar = 4 * beat
chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
music = np.zeros(N)
L = N / SR
nbars = int(L / bar) + 1
for b in range(nbars):
    start = int(b * bar * SR); n = int(bar * SR)
    if start >= N: break
    seg = t_axis(bar)
    ch = chords[b % 4]
    env = np.minimum(1, seg / 0.4) * np.minimum(1, (bar - seg) / 0.5)
    pad = sum(np.sin(2 * np.pi * midi(k) * seg) + 0.5 * np.sin(2 * np.pi * midi(k) * 1.003 * seg + 1) +
              0.25 * np.sin(2 * np.pi * midi(k + 12) * seg) for k in ch) / 9
    bass = 0.55 * np.sin(2 * np.pi * midi(ch[0] - 12) * seg) * np.exp(-seg * 0.6)
    chunk = (pad * env * 0.55 + bass * env)
    # arpeggio plucks (8ths) from bar 2 on
    if b >= 2:
        notes = ch + [ch[0] + 12]
        for i in range(8):
            ts = i * beat / 2; k = notes[i % 4] + 12
            s0 = int(ts * SR); tt = t_axis(min(0.6, bar - ts))
            pl = (np.sin(2 * np.pi * midi(k) * tt) + 0.3 * np.sin(4 * np.pi * midi(k) * tt)) * np.exp(-tt * 7) * 0.22
            chunk[s0:s0 + len(pl)] += pl[: n - s0]
    # soft kick + shaker from bar 4 on
    if b >= 4:
        for i in range(4):
            s0 = int(i * beat * SR); tt = t_axis(0.25)
            kick = np.sin(2 * np.pi * (45 + 70 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 14) * 0.5
            chunk[s0:s0 + len(kick)] += kick[: n - s0]
            s1 = int((i + 0.5) * beat * SR); sh = rng.standard_normal(int(0.05 * SR)) * np.exp(-t_axis(0.05) * 70) * 0.06
            chunk[s1:s1 + len(sh)] += sh[: n - s1]
    music[start:start + n] += chunk[: N - start]
music = fft_lowpass(music, 5200)
# fade in/out
fi = int(1.5 * SR); fo = int(3.0 * SR)
music[:fi] *= np.linspace(0, 1, fi); music[-fo:] *= np.linspace(1, 0, fo)

# ---------- narration ----------
voice = np.zeros(N)
for e in events:
    if e["kind"] != "voice": continue
    with wave.open(str(VOICE / f"{e['key']}.wav")) as w:
        sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float64) / 32768
    x = np.interp(np.arange(int(len(x) * SR / sr)) * sr / SR, np.arange(len(x)), x)
    s0 = int((e["t"] + offset) * SR)
    voice[s0:s0 + len(x)] += x[: N - s0]

# ---------- SFX ----------
sfx = np.zeros(N)
def place(sig, t):
    s0 = int((t + offset) * SR)
    if 0 <= s0 < N: sfx[s0:s0 + len(sig)] += sig[: N - s0]

tw = t_axis(0.7)
whoosh = lowpass(rng.standard_normal(len(tw)), 2500) * np.sin(np.pi * tw / 0.7) ** 2 * 1.4
tp = t_axis(0.09)
pop = np.sin(2 * np.pi * (900 + 500 * tp / 0.09) * tp) * np.exp(-tp * 45) * 0.22
tc = t_axis(0.03)
click = rng.standard_normal(len(tc)) * np.exp(-tc * 220) * 0.28
for e in events:
    {"whoosh": lambda t: place(whoosh, t - 0.25), "pop": lambda t: place(pop, t),
     "click": lambda t: place(click, t)}.get(e["kind"], lambda t: None)(e["t"])

# ---------- ducking + mix ----------
envv = np.convolve(np.abs(voice), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
duck = 1 - 0.68 * np.clip(envv / (envv.max() * 0.15 + 1e-9), 0, 1)
duck = np.convolve(duck, np.ones(int(0.12 * SR)) / int(0.12 * SR), mode="same")
mix_mono_music = music / (np.abs(music).max() + 1e-9) * 0.30 * duck
v = voice / (np.abs(voice).max() + 1e-9) * 0.92
left = mix_mono_music * 0.96 + v + sfx * 0.9
right = mix_mono_music * 1.0 + v + sfx * 0.9
# gentle stereo width on music
right = right + 0.06 * np.roll(mix_mono_music, int(0.012 * SR))
stereo = np.stack([left, right], 1)
stereo = np.tanh(stereo * 1.1) / np.tanh(1.1)  # soft limiter
stereo *= 0.95 / np.abs(stereo).max()
with wave.open(str(out), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((stereo * 32767).astype("<i2").tobytes())
print("offset", round(offset, 3), "seconds", round(N / SR, 2))
