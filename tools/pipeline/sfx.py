"""Sound effects: cue list from the shot list, real files from sfx/ when present, numpy stand-ins otherwise."""
import os, re, subprocess, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(11)

def lowpass(x, n):
    n = max(1, int(n)); return np.convolve(x, np.ones(n) / n, 'same')
def highpass(x, n): return x - lowpass(x, n)
def env(n, attack=0.005, decay=1.0):
    t = np.arange(n) / SR
    a = np.minimum(1, t / max(attack, 1e-4)); return a * np.exp(-t * decay)
def noise(sec): return rng.standard_normal(int(sec * SR)).astype(np.float32)
def tone(f, sec, kind='sine'):
    t = np.arange(int(sec * SR)) / SR
    if kind == 'saw': return (2 * ((t * f) % 1) - 1).astype(np.float32)
    return np.sin(2 * np.pi * f * t).astype(np.float32)
def norm(x, peak=1.0):
    m = np.abs(x).max(); return (x / m * peak).astype(np.float32) if m > 0 else x

# ---------- synthesized stand-ins (replace with real files in sfx/<name>.wav) ----------
def synth(name):
    if name == 'static': x = highpass(lowpass(noise(0.09), 3), 40) * np.linspace(1, 0, int(0.09 * SR)) ** 0.5
    elif name == 'thud': x = tone(55, 0.35) * env(int(0.35 * SR), 0.003, 9)
    elif name == 'deep_hit': x = (tone(70, 0.7) + 0.3 * lowpass(noise(0.7), 40)) * env(int(0.7 * SR), 0.003, 5)
    elif name == 'click': x = highpass(noise(0.008), 4) * env(int(0.008 * SR), 0.0005, 300)
    elif name == 'tick': x = tone(1500, 0.012) * env(int(0.012 * SR), 0.001, 250)
    elif name == 'pop': x = tone(900, 0.05) * env(int(0.05 * SR), 0.001, 70)
    elif name == 'whoosh':
        n = noise(0.35); x = np.zeros_like(n)
        # sweeping lowpass: short windows with increasing cutoff
        seg = len(n) // 12
        for i in range(12):
            x[i * seg:(i + 1) * seg] = lowpass(n[i * seg:(i + 1) * seg], 60 - i * 4)
        x *= np.sin(np.linspace(0, np.pi, len(x))) ** 2
    elif name == 'scratch':
        a = highpass(noise(0.12), 6) * env(int(0.12 * SR), 0.002, 25)
        x = np.concatenate([a, np.zeros(int(0.08 * SR)), a])
    elif name == 'knock':
        one = lowpass(noise(0.07), 30) * env(int(0.07 * SR), 0.001, 60) + 0.6 * tone(150, 0.07) * env(int(0.07 * SR), 0.001, 50)
        gap = np.zeros(int(0.22 * SR)); x = np.concatenate([one, gap, one, gap, one])
    elif name == 'lock': x = np.concatenate([highpass(noise(0.015), 3) * env(int(0.015 * SR), 0.0005, 200), tone(2100, 0.05) * env(int(0.05 * SR), 0.001, 80)])
    elif name == 'doorbell': x = np.concatenate([tone(659, 0.45) * env(int(0.45 * SR), 0.002, 5), tone(523, 0.7) * env(int(0.7 * SR), 0.002, 4)])
    elif name == 'jingle':
        parts = []
        for i in range(6):
            f = rng.uniform(2800, 6000); parts.append(tone(f, 0.05) * env(int(0.05 * SR), 0.001, 60)); parts.append(np.zeros(int(rng.uniform(0.02, 0.06) * SR)))
        x = np.concatenate(parts)
    elif name == 'footstep': x = lowpass(noise(0.07), 40) * env(int(0.07 * SR), 0.002, 50)
    elif name == 'bark':
        def one():
            n = int(0.11 * SR); t = np.arange(n) / SR
            f = 420 - 180 * (t / t[-1])
            ph = 2 * np.pi * np.cumsum(f) / SR
            v = (0.6 * np.sign(np.sin(ph)) + 0.4 * np.sin(2 * ph)) * (1 + 0.5 * lowpass(noise(0.11), 20))
            return lowpass(v, 6) * env(n, 0.004, 22)
        x = np.concatenate([one(), np.zeros(int(0.16 * SR)), one()])
    elif name == 'growl':
        n = int(0.8 * SR); t = np.arange(n) / SR
        x = np.sign(np.sin(2 * np.pi * 42 * t)) * (0.5 + 0.5 * lowpass(noise(0.8), 25)) * np.sin(np.pi * t / t[-1])
        x = lowpass(x, 14)
    elif name == 'paper': x = highpass(lowpass(noise(0.25), 2), 12) * np.sin(np.linspace(0, np.pi, int(0.25 * SR))) ** 1.5 * 0.5
    elif name == 'breath': x = lowpass(highpass(noise(0.6), 30), 8) * np.sin(np.linspace(0, np.pi, int(0.6 * SR))) ** 2
    elif name == 'ring':
        n = int(0.9 * SR); t = np.arange(n) / SR
        x = tone(1200, 0.9) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 20 * t))) * env(n, 0.002, 2)
    else: x = np.zeros(int(0.05 * SR), dtype=np.float32)
    return norm(x.astype(np.float32))

def load(name):
    for ext in ('wav', 'mp3', 'ogg', 'm4a'):
        p = f'sfx/{name}.{ext}'
        if os.path.exists(p):
            raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
            x = np.frombuffer(raw, dtype=np.float32)
            if len(x): return norm(x), True
    return synth(name), False

# ---------- cue list from shots ----------
GAIN = {'static': 0.16, 'thud': 0.5, 'deep_hit': 0.6, 'click': 0.12, 'tick': 0.2, 'pop': 0.25, 'whoosh': 0.22, 'scratch': 0.2,
        'knock': 0.45, 'lock': 0.3, 'doorbell': 0.35, 'jingle': 0.22, 'footstep': 0.25, 'bark': 0.4, 'growl': 0.3, 'paper': 0.2, 'breath': 0.18, 'ring': 0.3}

def cues_for(shots, cards, glitch_frames, fps, card_len=2.5):
    cues = []  # (time, name)
    for sf in glitch_frames: cues.append((sf / fps, 'static'))
    for (st, n, txt, red) in cards:
        cues.append((st, 'thud'))
        if txt:
            for i in range(len(txt)): cues.append((st + 0.5 + i * 0.04, 'click'))
    for s in shots:
        t0, sc, p = s['start'], s['scene'], s['params']
        low = s['text'].lower()
        dur = s['end'] - s['start']
        if sc in ('dog_four', 'dog_bed', 'circle_dog') or ('dog' in sc and p.get('check')):
            cues.append((t0 + 0.2, 'bark'))
        elif sc in ('dog_two', 'stand_mirror', 'dog_flat') or p.get('dog') or p.get('dog_two') or p.get('dog_behind') or p.get('dog_watch'):
            if s['i'] % 2 == 0: cues.append((t0 + 0.3, 'growl'))
        if p.get('enter') or sc in ('walk_out',) or p.get('dog_watch'): cues.append((t0 + 0.05, 'whoosh'))
        if p.get('xmark'): cues.append((t0 + 0.5, 'scratch'))
        if p.get('label') or sc == 'bubble': cues.append((t0 + 0.4, 'pop'))
        if sc == 'door':
            if p.get('handle_move'): cues.append((t0 + 0.3, 'knock'))
            if p.get('lock'): cues.append((t0 + 0.6, 'lock'))
            if p.get('reach'): cues.append((t0 + 0.8, 'lock'))
        if sc == 'doorbell' and p.get('ring'): cues.append((t0 + 0.2, 'doorbell'))
        if sc == 'phone' or sc == 'person_phone': cues.append((t0 + 0.1, 'click'))
        if sc == 'keys' or p.get('pose') == 'keys': cues.append((t0 + 0.2, 'jingle'))
        if sc == 'walk_out':
            for i in range(5): cues.append((t0 + 0.2 + i * 0.4, 'footstep'))
        if sc == 'seven':
            for i in range(7): cues.append((t0 + 0.1 + i * 0.05, 'tick'))
        if sc == 'casefile': cues.append((t0 + 0.05, 'paper'))
        if sc == 'bigword': cues.append((t0, 'deep_hit'))
        if sc == 'wall_ear' or 'breath' in low: cues.append((t0 + 0.4, 'breath'))
        if sc == 'eye' and p.get('red'): cues.append((t0 + 0.3, 'tick'))
    cues.sort()
    return cues

def build_track(total_sec, cues, out_path='sfx.wav'):
    n = int(total_sec * SR); out = np.zeros(n, dtype=np.float32)
    bank, real = {}, {}
    for (t, name) in cues:
        if name not in bank: bank[name], real[name] = load(name)
        sig = bank[name] * GAIN.get(name, 0.25)
        i = int(t * SR); j = min(n, i + len(sig))
        if i < n: out[i:j] += sig[:j - i]
    out = np.clip(out, -1, 1)
    w = wave.open(out_path, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out * 32767).astype(np.int16).tobytes()); w.close()
    return {k: ('file' if v else 'synthesized') for k, v in real.items()}, len(cues)
