#!/usr/bin/env python3
"""Synthesizes the Chiptune Keys sound pack (build/chiptune-keys.clinkpack).

Four interchangeable 8-bit takes in the official .clinkpack shape
({pack:{...}, samples:[base64 wav,...]}), reverse-engineered from
anti-ltd/clink-sounds' arcade pack: 44.1kHz mono 16-bit WAV,
square wave with an exponential decay envelope.
"""
import base64, io, json, math, pathlib, struct, wave

SR = 44100
ROOT = pathlib.Path(__file__).resolve().parents[1]

def tone(freq, ms, vol=0.7, decay=6.0):
    n = int(SR * ms / 1000)
    out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-decay * i / n)
        # slight attack ramp to soften the click
        atk = min(1.0, i / 66.0)
        s = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        out.append(int(32767 * vol * env * atk * s))
    return out

def sweep(f0, f1, ms, steps=8, vol=0.7, decay=4.0):
    # quantized pitch steps, chiptune style
    out = []
    per = ms / steps
    for s in range(steps):
        f = f0 * (f1 / f0) ** (s / (steps - 1))
        out += tone(f, per, vol=vol, decay=decay)
    return out

def wav_bytes(samples):
    buf = io.BytesIO()
    w = wave.open(buf, "wb")
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(b"".join(struct.pack("<h", max(-32767, min(32767, s))) for s in samples))
    w.close()
    return buf.getvalue()

TAKES = {
    "chiptune-1": tone(988, 55) + tone(1319, 95),          # coin: B5 -> E6
    "chiptune-2": tone(659, 40) + tone(784, 40) + tone(988, 65),  # mini arpeggio
    "chiptune-3": sweep(300, 900, 115),                    # jump
    "chiptune-4": tone(1319, 38) + tone(988, 38) + tone(1568, 60, decay=7.0),  # sparkle
}

def main():
    names = list(TAKES.keys())
    pack = {
        "pack": {
            "id": "chiptune-keys",
            "name": "Chiptune Keys",
            "blurb": "8-bit game blips under your fingers: coins, jumps and sparkles.",
            "sampleNames": names,
            "fileExtension": "wav",
            "gain": 0.9,
            "source": "bundled",
        },
        "samples": [base64.b64encode(wav_bytes(TAKES[n])).decode() for n in names],
    }
    out = ROOT / "build" / "chiptune-keys.clinkpack"
    out.write_text(json.dumps(pack), encoding="utf-8")
    print(out, out.stat().st_size, "bytes")

if __name__ == "__main__":
    main()
