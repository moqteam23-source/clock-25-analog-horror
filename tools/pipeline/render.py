"""Compose every frame, encode per shot, join, add audio.
v3: measured card build, caption fade, HUD numbers, measured glitch pattern, push instead of drift, film floor.
See claude/animation-bible.md for every number used here."""
import json, math, os, re, subprocess, sys, random, time
import numpy as np
from PIL import Image, ImageDraw
from multiprocessing import Pool
import engine
from engine import *
import scenes

OUT = 'out'
os.makedirs(OUT, exist_ok=True)
CHANNEL = open('channel.txt').read().strip().splitlines() if os.path.exists('channel.txt') else ['ARCHIVE', 'FILE 001']
HUD_LABEL = f'{CHANNEL[1]}  //  {CHANNEL[0]}'
_m = re.search(r'(\d+)', CHANNEL[1]); NEXT_FILE = f'NEXT FILE: {int(_m.group(1)) + 1:03d}' if _m else 'NEXT FILE'
CARD_LEN = 2.5
CARD_BLACK = 0.4      # measured: 12 black frames (3 with streaks) before the title fades in
CARD_FADE = 0.2       # measured: title fades in over 6 frames, no slide
CARD_TYPE_MS = 25     # measured: 24 to 25 ms per character, no cursor
PRE_FADE = 8 / 30     # measured: the scene fades out over 8 frames before a card
RULE_WORDS = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7}
RULE_TEXT = {1: 'ACT NORMAL', 2: 'DO NOT SAY ITS NAME', 3: 'DO NOT TAKE OUT YOUR PHONE', 4: 'GO TO BED AT YOUR USUAL TIME',
             5: 'DO NOT ANSWER', 6: 'LEAVE THE HOUSE', 7: None}
RULE7_REVEAL = "DO NOT ASK WHO'S A GOOD BOY"
HARD_CUT_EVERY = 6    # measured: 13 to 18 percent of cuts are hard; the rest carry a glitch

caps = json.load(open('captions.json'))
AUDIO_DUR = caps[-1]['end']
TAIL = 1.5
TOTAL_FRAMES = int(round((AUDIO_DUR + TAIL) * FPS))

# ---------- shot list ----------
shots = []
cards = []     # (start_s, num, text, redacted)
seen7 = False
for c in caps:
    m = re.match(r'^rule (\w+)', c['text'].lower())
    card = None
    if m and m.group(1) in RULE_WORDS:
        n = RULE_WORDS[m.group(1)]
        if n == 7 and not seen7:
            card = (c['start'], 7, None, True); seen7 = True
        elif n == 7:
            card = (c['start'], 7, RULE7_REVEAL, False)
        else:
            card = (c['start'], n, RULE_TEXT[n], False)
        cards.append(card)
    scene, params = scenes.assign(c['text'])
    shots.append({'i': c['i'], 'start': c['start'], 'end': c['end'], 'text': c['text'], 'scene': scene, 'params': params, 'card': card})
# last caption = big word card
shots[-1]['scene'] = 'bigword'; shots[-1]['params'] = {'word': shots[-1]['text'].upper()}
# transitions: glitch on most cuts, a hard cut every HARD_CUT_EVERY, black flash only before the big word
for k, s in enumerate(shots):
    s['sf'] = int(round(s['start'] * FPS)); s['ef'] = int(round(s['end'] * FPS))
    s['trans'] = 'glitch'
    if k > 0 and k % HARD_CUT_EVERY == 5 and not s['card'] and not shots[k - 1]['card']: s['trans'] = 'cut'
    if s['card'] or (k > 0 and shots[k - 1]['card']): s['trans'] = 'card'   # handled by the fade recipe
    if k == len(shots) - 1: s['trans'] = 'black'
    s['params']['dur'] = max(0.5, s['end'] - s['start'])
shots[0]['sf'] = 0
shots[-1]['ef'] = TOTAL_FRAMES
# glitch frames: 2 before the cut (heavy), 3 after (heavy, light, light); plus a 3 frame hit mid shot on long holds
GLITCH = {}
for s in shots:
    if s['trans'] == 'glitch':
        for j, heavy in zip(range(-2, 3), (True, True, True, False, False)): GLITCH[s['sf'] + j] = heavy
    if s['end'] - s['start'] > 6.0:
        mid = (s['sf'] + s['ef']) // 2
        for j, heavy in zip(range(0, 3), (True, False, False)): GLITCH[mid + j] = heavy
BLACK_START = shots[-1]['sf'] - 16   # 3 black, 1 picture, 12 black, then the word

def shot_at(f):
    for s in shots:
        if s['sf'] <= f < s['ef']: return s
    return shots[-1]

def card_at(t):
    for (st, n, txt, red) in cards:
        if st <= t < st + CARD_LEN: return (st, n, txt, red)
    return None

def pre_card_fade(t):
    """1.0 normally; falls to 0 over the 8 frames before a card starts."""
    for (st, n, txt, red) in cards:
        if st - PRE_FADE <= t < st: return 1 - (t - (st - PRE_FADE)) / PRE_FADE
    return 1.0

def rule_overlay_at(t):
    for (st, n, txt, red) in cards:
        if st + CARD_LEN <= t < st + CARD_LEN + 2.0: return (st, n, txt, red)
    return None

def current_rule(t):
    n = 0
    for (st, num, txt, red) in cards:
        if t >= st: n = num
    return n

# ---------- drawing pieces ----------
def wrap_caption(d, text, f, maxw):
    words = text.split()
    lines, cur = [], ''
    for w in words:
        trial = (cur + ' ' + w).strip()
        if text_width(d, trial, f, 3) <= maxw: cur = trial
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    if len(lines) == 2:  # balance the break near the middle (measured captions break mid sentence)
        best = None
        for i in range(1, len(words)):
            a, b = ' '.join(words[:i]), ' '.join(words[i:])
            wa, wb = text_width(d, a, f, 3), text_width(d, b, f, 3)
            if wa <= maxw and wb <= maxw:
                sc = abs(wa - wb)
                if best is None or sc < best[0]: best = (sc, [a, b])
        if best: lines = best[1]
    return lines

def draw_caption(img, d, text, alpha=1.0):
    """Measured: 53 px SemiBold caps at 1080p, 3 px tracking, line pitch 60, block centered at y 902, 5 frame fade."""
    text = text.upper()
    f = F_CAP
    lines = wrap_caption(d, text, f, 1500)
    if len(lines) > 2:
        f = font(600, 44); lines = wrap_caption(d, text, f, 1560)
    col = tuple(int(255 * alpha) for _ in range(3))
    y0 = 902 - (len(lines) - 1) * 30
    for i, ln in enumerate(lines):
        draw_spaced(d, (W / 2, y0 + i * 60), ln, f, col, 3)

def draw_hud(d, f, t):
    """Measured: 17 px Medium, color 48, y 82, boxes 32 x 34 at pitch 35, hidden until the first rule card."""
    col = (48, 48, 48)
    draw_spaced(d, (97, 82), HUD_LABEL, F_HUD, col, 3, anchor='left')
    tc = f'{int(t // 3600):02d}:{int(t // 60) % 60:02d}:{int(t) % 60:02d}:{f % FPS:02d}'
    draw_spaced(d, (W - 97, 82), tc, F_HUD, col, 2, anchor='right')
    cur = current_rule(t)
    if cur == 0: return
    x0 = W / 2 - 3 * 35
    for i in range(7):
        bx = x0 + i * 35; n = i + 1
        box = (bx - 16, 65, bx + 16, 99)
        if n == cur:
            d.rounded_rectangle(box, radius=5, fill=(151, 142, 138))
            draw_spaced(d, (bx, 82), str(n), font(700, 15), (0, 0, 0), 0)
        else:
            d.rounded_rectangle(box, radius=5, outline=(41, 41, 41), width=2)
            draw_spaced(d, (bx, 82), str(n), font(700, 15), (70, 70, 70), 0)

def draw_card(img, d, t_in, n, txt, redacted):
    """Measured build: black lead (streaks on frames 2 to 4), title + box fade in together over 6 frames (no slide),
    red line wipes in 3 frames from frame 3 of the fade, subtitle types at 25 ms per character with no cursor,
    seven mini boxes under it, hold."""
    if t_in < CARD_BLACK:
        fr = int(t_in * FPS)
        if 2 <= fr <= 4:
            rng = random.Random(fr)
            for _ in range(40):
                y = rng.randint(0, H - 3); x0 = rng.randint(0, W - 100)
                d.rectangle((x0, y, x0 + rng.randint(10, 90), y + rng.randint(1, 2)), fill=(rng.randint(80, 200),) * 3)
        return
    u = t_in - CARD_BLACK
    a = 0.25 + 0.75 * clamp(u / CARD_FADE, 0, 1)
    col = tuple(int(255 * a) for _ in range(3))
    # title block: "RULE" + box, centered as a block at y 430
    f = F_RULE
    tw = text_width(d, 'RULE', f, 12); box = 195; gap = 36
    total = tw + gap + box
    x0 = W / 2 - total / 2
    draw_spaced(d, (x0, 430), 'RULE', f, col, 12, anchor='left')
    bx = x0 + tw + gap + box / 2
    d.rounded_rectangle((bx - box / 2, 430 - box / 2, bx + box / 2, 430 + box / 2), radius=21, fill=col)
    draw_spaced(d, (bx, 436), str(n), F_RULENUM, (0, 0, 0), 0)
    kl = draw_on(u, 3, CARD_FADE * 0.5)
    if kl > 0: d.line((W / 2 - 330, 572, W / 2 - 330 + 660 * kl, 572), fill=RED_LINE, width=9)
    t_type = u - CARD_FADE
    if t_type > 0:
        if redacted:
            kr = ease_out(t_type / 0.3)
            d.rounded_rectangle((W / 2 - 390 * kr, 610, W / 2 + 390 * kr, 664), radius=6, fill=(90, 90, 90))
        else:
            nchar = int(t_type * 1000 / CARD_TYPE_MS)
            draw_spaced(d, (W / 2, 636), txt[:nchar], F_RULETXT, WHITE, 6)
        x0 = W / 2 - 3 * 70
        for i in range(7):
            bx = x0 + i * 70; m = i + 1
            b = (bx - 28, 760 - 28, bx + 28, 760 + 28)
            if m == n:
                d.rounded_rectangle(b, radius=8, fill=WHITE); draw_spaced(d, (bx, 760), str(m), font(800, 30), (0, 0, 0), 0)
            elif redacted and m == 7:
                d.rounded_rectangle(b, radius=8, outline=(72, 71, 76), width=3); d.rectangle((bx - 16, 755, bx + 16, 765), fill=(90, 90, 90))
            else:
                d.rounded_rectangle(b, radius=8, outline=(72, 71, 76), width=3); draw_spaced(d, (bx, 760), str(m), font(800, 30), (63, 64, 67), 0)

def draw_rule_overlay(d, t_in, n, txt, redacted):
    a = 1.0 if t_in < 1.5 else max(0.0, 1 - (t_in - 1.5) / 0.5)
    col = tuple(int(255 * a) for _ in range(3))
    if a <= 0: return
    draw_spaced(d, (97, 130), f'RULE {n}', F_RULE_OVER, col, 4, anchor='left')
    d.line((97, 148, 197, 148), fill=tuple(int(c * a) for c in RED_LINE), width=3)
    draw_spaced(d, (97, 168), 'CLASSIFIED' if redacted else txt, font(500, 18), tuple(int(170 * a) for _ in range(3)), 3, anchor='left')

# ---------- compose one frame ----------
def compose(f):
    t = f / FPS
    s = shot_at(f)
    t_in = (f - s['sf']) / FPS
    dur = max(1, s['ef'] - s['sf']) / FPS
    base = Image.new('RGB', (W, H), BG)
    card = card_at(t)
    caption_alpha = 1.0
    if f >= int(round(AUDIO_DUR * FPS)):
        return base  # black tail
    flash = one_frame_flash(f, BLACK_START) if s['scene'] == 'bigword' or f >= BLACK_START else None
    if flash == 'black':
        return base
    if card:
        d = ImageDraw.Draw(base)
        draw_card(base, d, t - card[0], card[1], card[2], card[3])
        caption_alpha = clamp((t - card[0] - CARD_BLACK) / 0.17, 0, 1)  # caption fades in with the title
    elif s['scene'] == 'bigword':
        d = ImageDraw.Draw(base)
        big_word(d, s['params']['word'], t_in, sub=NEXT_FILE, sub_after=3.0)
    else:
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        engine.paste_glow_later.clear()
        scenes._T[0] = t_in
        scenes.SCENES[s['scene']](d, layer, t_in, s['params'])
        for (gx, gy, gr) in list(engine.paste_glow_later):
            paste_glow(base, gx, gy, gr, alpha=120)
        base.paste(layer, (0, 0), layer)
        # 1.2 base zoom plus a measured slow push (0 to 4 percent, ease in and out, after 0.5 s). Dinner scenes push inside camera().
        cam = s['scene'].startswith('dinner') or s['scene'] in ('lights_out', 'photo', 'under_table')
        push = 0.0 if cam else 0.04
        z = (1.0 if cam else 1.2) * (1.0 + push * ease_in_out((t_in - 0.5) / max(dur - 0.5, 0.5)))
        cw, ch = int(W / z), int(H / z)
        base = base.crop(((W - cw) // 2, (H - ch) // 2, (W - cw) // 2 + cw, (H - ch) // 2 + ch)).resize((W, H), Image.BILINEAR)
        pf = pre_card_fade(t)
        if pf < 1.0:
            base = Image.eval(base, lambda v: int(v * pf)); caption_alpha = pf
    d = ImageDraw.Draw(base)
    draw_hud(d, f, t)
    ro = rule_overlay_at(t)
    if ro and not card: draw_rule_overlay(d, t - ro[0] - CARD_LEN, ro[1], ro[2], ro[3])
    if s['scene'] != 'bigword':
        fade = clamp((f - s['sf'] + 1) / 5, 0, 1)   # measured 5 frame caption fade
        draw_caption(base, d, s['text'], alpha=caption_alpha * fade)
    heavy = GLITCH.get(f)
    if heavy is not None:
        base = glitch_frame(base, 1.0, f, heavy)
    base = film_floor(base, seed=f)
    return base

# ---------- encode ----------
def render_shot(k):
    s = shots[k]
    out = f'{OUT}/shot_{k:03d}.mp4'
    if os.path.exists(out): return out
    tmp = f'{OUT}/shot_{k:03d}.tmp.mp4'
    cmd = ['ffmpeg', '-hide_banner', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-i', 'scan.png', '-filter_complex',
           '[0:v]rgbashift=rh=-2:bh=2,vignette=angle=PI/7,noise=alls=7:allf=t+u[v];[v][1:v]overlay=format=auto,format=yuv420p',
           '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(s['sf'], s['ef']):
        p.stdin.write(compose(f).tobytes())
    p.stdin.close(); p.wait()
    if p.returncode != 0: raise RuntimeError(f'ffmpeg failed on shot {k}')
    os.rename(tmp, out)
    return out

def make_scanlines():
    a = np.zeros((H, W, 4), dtype=np.uint8)
    a[::2, :, 3] = 4   # measured: no visible scanlines in the reference; keep a 1.5 percent texture
    Image.fromarray(a, 'RGBA').save('scan.png')

def make_sfx():
    import sfx
    cues = sfx.cues_for(shots, cards, [f for f, hv in GLITCH.items() if hv and GLITCH.get(f - 1) is None], FPS, CARD_LEN)
    sources, n = sfx.build_track(AUDIO_DUR + TAIL, cues, 'sfx.wav')
    json.dump({'cues': cues, 'sources': sources}, open(f'{OUT}/sfx_cues.json', 'w'), indent=1)
    print(f'sfx: {n} cues, sources: {sources}')
    return sources

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    make_scanlines()
    json.dump(shots, open(f'{OUT}/shots.json', 'w'), indent=1)
    if mode == 'preview':
        os.makedirs('preview', exist_ok=True)
        picks = {'cold_open': int(2.0 * FPS), 'seven_rules': int((shots[min(1, len(shots) - 1)]['start'] + 1.0) * FPS)}
        if cards:
            picks.update({'card_typing': int((cards[0][0] + 0.9) * FPS), 'after_card': int((cards[0][0] + 3.0) * FPS), 'card7': int((cards[-1][0] + 1.5) * FPS)})
        picks.update({'glitch': shots[min(3, len(shots) - 1)]['sf'] + 1, 'bigword': int((shots[-1]['start'] + 1.0) * FPS)})
        for name, f in picks.items():
            compose(f).save(f'preview/{name}.jpg', quality=90)
        print('previews written:', list(picks))
    elif mode == 'frame':
        f = int(sys.argv[2]); os.makedirs('preview', exist_ok=True); compose(f).save(f'preview/f{f}.jpg', quality=90)
    elif mode == 'shot':
        k = int(sys.argv[2]); out = f'{OUT}/shot_{k:03d}.mp4'
        if os.path.exists(out): os.remove(out)
        print(render_shot(k))
    else:
        t0 = time.time()
        with Pool(int(sys.argv[2]) if len(sys.argv) > 2 else 4) as pool:
            for i, r in enumerate(pool.imap_unordered(render_shot, range(len(shots)))):
                if i % 10 == 0: print(f'{i + 1}/{len(shots)} shots, {time.time() - t0:.0f}s', flush=True)
        with open(f'{OUT}/list.txt', 'w') as fh:
            for k in range(len(shots)): fh.write(f"file 'shot_{k:03d}.mp4'\n")
        subprocess.run(['ffmpeg', '-hide_banner', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{OUT}/list.txt', '-c', 'copy', f'{OUT}/video_silent.mp4'], check=True)
        make_sfx()
        subprocess.run(['ffmpeg', '-hide_banner', '-v', 'error', '-y', '-i', f'{OUT}/video_silent.mp4', '-i', 'voice.mp3', '-i', 'sfx.wav',
                        '-filter_complex', '[1:a]apad[v];[v][2:a]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]',
                        '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', 'final.mp4'], check=True)
        print('done in', round(time.time() - t0), 's')
