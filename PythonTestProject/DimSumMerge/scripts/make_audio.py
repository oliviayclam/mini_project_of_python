#!/usr/bin/env python3
"""Generate short royalty-free loop + SFX wavs (no third-party samples)."""
import math
import os
import struct
import wave

ROOT = os.path.join(os.path.dirname(__file__), "..", "public", "audio")
RATE = 22050


def write_wav(path, samples):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", int(max(-32767, min(32767, s)))) for s in samples))


def env(i, n, a=80, r=400):
    return min(1.0, i / a) * min(1.0, (n - i) / r)


def melody(path, freqs_beats, bpm, kind="sine", amp=0.18):
    beat = 60.0 / bpm
    samples = []
    for freq, beats in freqs_beats:
        n = int(RATE * beat * beats)
        for i in range(n):
            t = i / RATE
            e = env(i, n)
            if freq <= 0:
                s = 0.0
            elif kind == "tri":
                s = e * amp * (2 * abs(2 * ((freq * t) % 1) - 1) - 1)
            elif kind == "sq":
                s = e * amp * 0.55 * (1 if math.sin(2 * math.pi * freq * t) > 0 else -1)
            else:
                s = e * amp * math.sin(2 * math.pi * freq * t)
                s += e * amp * 0.25 * math.sin(4 * math.pi * freq * t)
            samples.append(s * 32767)
    write_wav(path, samples)


def blip(path, freq, ms, kind="sine"):
    n = int(RATE * ms / 1000)
    samples = []
    for i in range(n):
        t = i / RATE
        e = env(i, n, 40, 200)
        if kind == "noise":
            s = e * 0.2 * math.sin(t * 8000 + i * 12.9898)
        else:
            s = e * 0.28 * math.sin(2 * math.pi * freq * t)
        samples.append(s * 32767)
    write_wav(path, samples)


# pentatonic-ish cute loops
C, D, E, G, A, B = 261.63, 293.66, 329.63, 392.00, 440.00, 493.88
F = 349.23

melody(
    os.path.join(ROOT, "bgm-seating.wav"),
    [(E, 0.5), (G, 0.5), (A, 0.5), (G, 0.5), (E, 0.5), (D, 0.5), (C, 1), (0, 0.5),
     (G, 0.5), (A, 0.5), (B, 0.5), (A, 0.5), (G, 1), (E, 1)],
    bpm=88,
    kind="sine",
)
melody(
    os.path.join(ROOT, "bgm-table.wav"),
    [(C, 0.5), (E, 0.5), (G, 0.5), (E, 0.5), (A, 0.5), (G, 0.5), (E, 0.5), (C, 0.5),
     (D, 0.5), (G, 0.5), (A, 0.5), (G, 0.5), (E, 1), (C, 1)],
    bpm=76,
    kind="sine",
    amp=0.14,
)
melody(
    os.path.join(ROOT, "bgm-waitress.wav"),
    [(G, 0.25), (A, 0.25), (B, 0.5), (A, 0.25), (G, 0.25), (E, 0.5),
     (D, 0.25), (E, 0.25), (G, 0.5), (A, 1)],
    bpm=110,
    kind="tri",
)
melody(
    os.path.join(ROOT, "bgm-cart.wav"),
    [(C * 2, 0.25), (E * 2, 0.25), (G * 2, 0.25), (E * 2, 0.25),
     (D * 2, 0.25), (G, 0.25), (A, 0.5), (G, 0.5)],
    bpm=128,
    kind="sq",
    amp=0.12,
)
melody(
    os.path.join(ROOT, "bgm-calltea.wav"),
    [(A, 0.75), (E, 0.75), (G, 0.5), (D, 1), (E, 1)],
    bpm=70,
    kind="sine",
    amp=0.16,
)
melody(
    os.path.join(ROOT, "bgm-milktea.wav"),
    [(G, 0.5), (B, 0.5), (A, 0.5), (G, 0.5), (E, 0.5), (G, 0.5), (D, 1)],
    bpm=100,
    kind="tri",
)
melody(
    os.path.join(ROOT, "bgm-pineapple.wav"),
    [(C, 0.25), (E, 0.25), (G, 0.25), (C * 2, 0.5), (A, 0.25), (G, 0.5), (E, 0.5), (C, 0.5)],
    bpm=118,
    kind="sq",
    amp=0.11,
)

blip(os.path.join(ROOT, "sfx-merge.wav"), 520, 180)
blip(os.path.join(ROOT, "sfx-pop.wav"), 740, 90)
blip(os.path.join(ROOT, "sfx-bell.wav"), 880, 260)
blip(os.path.join(ROOT, "sfx-clink.wav"), 1200, 140)
melody(
    os.path.join(ROOT, "sfx-win.wav"),
    [(C * 2, 0.2), (E * 2, 0.2), (G * 2, 0.4)],
    bpm=140,
    kind="sine",
    amp=0.22,
)
melody(
    os.path.join(ROOT, "sfx-lose.wav"),
    [(G, 0.3), (E, 0.3), (C, 0.5)],
    bpm=90,
    kind="tri",
    amp=0.18,
)

print("wrote", ROOT)
