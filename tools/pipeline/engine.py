"""Rules-horror video engine: procedural pictograms + HUD + rule cards + glitch, rendered with Pillow, encoded per shot by ffmpeg."""
import json, math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
FPS = 30
BG = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (248, 28, 40)
RED_LINE = (230, 12, 47)        # measured on the rule card line (was 172,24,50)
YELLOW = (249, 222, 117)
GREEN = (86, 237, 114)          # measured on the check marks (was 46,204,113)
GREY = (140, 140, 140)
CONE = (255, 200, 90)           # lamp cone color, drawn at 42 percent over black
BULB = (253, 253, 117)          # bulb glow
OUTLINE = (0, 0, 0)             # black outline of the dinner table figures
STROKE = 11
FONTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')

# Idle life. Measured reference: figures are pixel still during holds, so everything is off by default.
# set_idle('v2') restores the old breathing/blink behaviour if a client asks for it.
IDLE = {'breathe': 0.0, 'blink': False, 'sway': 0.0}
def set_idle(mode):
    if mode == 'v2': IDLE.update({'breathe': 1.0, 'blink': True, 'sway': 1.0})
    elif mode == 'subtle': IDLE.update({'breathe': 0.3, 'blink': False, 'sway': 0.3})
    else: IDLE.update({'breathe': 0.0, 'blink': False, 'sway': 0.0})

def font(weight, size):
    return ImageFont.truetype(os.path.join(FONTDIR, f'Montserrat-{weight}.ttf'), size)

F_CAP = font(600, 53)           # measured: cap height 25 px at 720p = 53 px font at 1080p (was 40)
F_HUD = font(500, 17)           # measured: cap height 8 px at 720p (was 20)
F_RULE = font(800, 157)         # measured: cap height 73 px at 720p (was 96)
F_RULENUM = font(800, 112)
F_RULETXT = font(700, 69)       # measured: cap height 32 px at 720p (was 34)
F_LABEL = font(700, 26)
F_BIG = font(900, 216)          # measured: cap height 101 px at 720p (was 150)
F_CARD = font(700, 56)
F_CARDSMALL = font(500, 24)
F_RULE_OVER = font(700, 22)
F_DIALOG = font(600, 30)        # dialogue bubble, mixed case
F_SMALLCAPS = font(600, 18)     # grey labels under objects
F_TINY = font(500, 15)
F_COUNTER = font(800, 236)

def ease_out(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3

def ease_in_out(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

def ease_in(x):
    x = max(0.0, min(1.0, x)); return x ** 3

def overshoot(x):
    x = max(0.0, min(1.0, x))
    return 1 + 2.2 * (x - 1) * (x - 1) * ((2.5 + 1) * (x - 1) + 2.5) if x < 1 else 1.0

def clamp(a, lo, hi): return max(lo, min(hi, a))

# ---------- text helpers ----------
def text_width(draw, s, f, spacing):
    return sum(draw.textlength(ch, font=f) for ch in s) + spacing * max(0, len(s) - 1)

def draw_spaced(draw, xy, s, f, fill, spacing, anchor='center'):
    x, y = xy
    tw = text_width(draw, s, f, spacing)
    if anchor == 'center': x = x - tw / 2
    elif anchor == 'right': x = x - tw
    for ch in s:
        draw.text((x, y), ch, font=f, fill=fill, anchor='lm')
        x += draw.textlength(ch, font=f) + spacing
    return tw

# ---------- glow cache ----------
_glow_cache = {}
def glow_blob(radius, color, alpha=120):
    key = (radius, color, alpha)
    if key not in _glow_cache:
        size = radius * 2
        im = Image.new('L', (size, size), 0)
        d = ImageDraw.Draw(im)
        d.ellipse((radius * 0.35, radius * 0.35, size - radius * 0.35, size - radius * 0.35), fill=alpha)
        im = im.filter(ImageFilter.GaussianBlur(radius * 0.32))
        col = Image.new('RGB', (size, size), color)
        _glow_cache[key] = (col, im)
    return _glow_cache[key]

def paste_glow(img, cx, cy, radius, color=YELLOW, alpha=120):
    alpha = int(round(alpha / 10.0) * 10)
    col, mask = glow_blob(radius, color, alpha)
    img.paste(col, (int(cx - radius), int(cy - radius)), mask)

# ---------- primitives ----------
def rrect(d, box, r, fill=None, outline=WHITE, width=STROKE):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)

def line(d, pts, fill=WHITE, width=STROKE):
    d.line(pts, fill=fill, width=width, joint='curve')
    for p in pts:
        d.ellipse((p[0] - width / 2, p[1] - width / 2, p[0] + width / 2, p[1] + width / 2), fill=fill)

def circle(d, c, r, fill=None, outline=WHITE, width=STROKE):
    d.ellipse((c[0] - r, c[1] - r, c[0] + r, c[1] + r), fill=fill, outline=outline, width=width)

def dashed_line(d, a, b, fill=RED, width=5, dash=18, gap=14, frac=1.0):
    L = math.hypot(b[0] - a[0], b[1] - a[1]) * frac
    if L <= 0: return
    ux, uy = (b[0] - a[0]) / math.hypot(b[0] - a[0], b[1] - a[1]), (b[1] - a[1]) / math.hypot(b[0] - a[0], b[1] - a[1])
    t = 0
    while t < L:
        t2 = min(t + dash, L)
        d.line((a[0] + ux * t, a[1] + uy * t, a[0] + ux * t2, a[1] + uy * t2), fill=fill, width=width)
        t += dash + gap

def x_mark(d, c, size, frac=1.0, color=RED, width=14):
    s = size / 2
    f1 = clamp(frac * 2, 0, 1); f2 = clamp(frac * 2 - 1, 0, 1)
    if f1 > 0: d.line((c[0] - s, c[1] - s, c[0] - s + 2 * s * f1, c[1] - s + 2 * s * f1), fill=color, width=width)
    if f2 > 0: d.line((c[0] + s, c[1] - s, c[0] + s - 2 * s * f2, c[1] - s + 2 * s * f2), fill=color, width=width)

def check_mark(d, c, size, color=GREEN, width=14):
    s = size / 2
    d.line((c[0] - s, c[1], c[0] - s * 0.25, c[1] + s * 0.7, c[0] + s, c[1] - s * 0.7), fill=color, width=width, joint='curve')

def label_pill(d, c, text, t, color=YELLOW, textcolor=(0, 0, 0), f=F_LABEL, pad=18, start=0.4, outline_only=False):
    """pop-in pill label. c = center. t = seconds since shot start."""
    k = overshoot((t - start) / 0.25) if t >= start else 0
    if k <= 0: return
    tw = text_width(d, text, f, 2)
    w, h = (tw + pad * 2) * k, (f.size + pad * 1.2) * k
    box = (c[0] - w / 2, c[1] - h / 2, c[0] + w / 2, c[1] + h / 2)
    if outline_only:
        d.rounded_rectangle(box, radius=10, outline=color, width=4)
        if k > 0.95: draw_spaced(d, (c[0], c[1]), text, f, color, 2)
    else:
        d.rounded_rectangle(box, radius=10, fill=color)
        if k > 0.95: draw_spaced(d, (c[0], c[1]), text, f, textcolor, 2)

def you_marker(d, c, t, start=0.5):
    """'YOU' label with a small down arrow above a figure."""
    k = ease_out((t - start) / 0.3) if t >= start else 0
    if k <= 0: return
    y = c[1] - 20 * (1 - k)
    draw_spaced(d, (c[0], y), 'YOU', F_LABEL, YELLOW, 3)
    d.polygon([(c[0] - 12, y + 24), (c[0] + 12, y + 24), (c[0], y + 40)], fill=YELLOW)

# ---------- pictograms ----------
def blink(t, period=3.3, phase=0.0):
    """True while the eye is closed (120 ms every period seconds). Off unless IDLE['blink']."""
    return IDLE['blink'] and ((t + phase) % period) < 0.12

def breathe(t, amp=3.0, rate=0.45, phase=0.0):
    """Breathing bob. Reference figures do not breathe, so this is scaled by IDLE['breathe'] (default 0)."""
    return IDLE['breathe'] * amp * math.sin(2 * math.pi * rate * t + phase)

def sway(t, amp=3.0, rate=0.6):
    return IDLE['sway'] * amp * math.sin(t * rate)

def person(d, c, pose='stand', scale=1.0, eyes=None, arm=None, sunglasses=False, t=0.0):
    """c = feet center. pose: stand, sit, lie, phone, keys, walk. Idle: breathing bob, blink, head sway."""
    s = scale
    x, y = c
    head_r = 42 * s
    bob = breathe(t, 2.5 * s, 0.4, x * 0.01)
    if pose == 'lie':
        body = (x - 200 * s, y - 70 * s - bob * 0.5, x + 20 * s, y - 10 * s)
        d.rounded_rectangle(body, radius=28 * s, fill=WHITE)
        circle(d, (x - 240 * s, y - 42 * s), head_r, fill=WHITE, outline=WHITE)
        d.rounded_rectangle((x + 10 * s, y - 60 * s, x + 110 * s, y - 20 * s), radius=18 * s, fill=WHITE)
        if eyes == RED:
            circle(d, (x - 250 * s, y - 50 * s), 6 * s, fill=RED, outline=RED)
        else:
            d.line((x - 258 * s, y - 50 * s, x - 240 * s, y - 50 * s), fill=(0, 0, 0), width=int(6 * s))
        return
    if pose == 'sit':
        d.rounded_rectangle((x - 40 * s, y - 230 * s - bob, x + 40 * s, y - 90 * s), radius=36 * s, fill=WHITE)
        d.rounded_rectangle((x - 30 * s, y - 110 * s, x + 110 * s, y - 60 * s), radius=22 * s, fill=WHITE)
        d.rounded_rectangle((x + 70 * s, y - 80 * s, x + 110 * s, y), radius=18 * s, fill=WHITE)
        hx, hy = x + sway(t, 3 * s), y - 270 * s - bob
    else:
        torso_top = y - 250 * s - bob
        d.rounded_rectangle((x - 38 * s, torso_top, x + 38 * s, y - 90 * s), radius=36 * s, fill=WHITE)
        if pose == 'walk':
            sw = walk_cycle(t)['leg']
            d.polygon([(x - 36 * s, y - 110 * s), (x - 4 * s, y - 110 * s), (x - 4 * s + 40 * s * sw, y), (x - 36 * s + 40 * s * sw, y)], fill=WHITE)
            d.polygon([(x + 4 * s, y - 110 * s), (x + 36 * s, y - 110 * s), (x + 36 * s - 40 * s * sw, y), (x + 4 * s - 40 * s * sw, y)], fill=WHITE)
        else:
            d.rounded_rectangle((x - 36 * s, y - 110 * s, x - 4 * s, y), radius=16 * s, fill=WHITE)
            d.rounded_rectangle((x + 4 * s, y - 110 * s, x + 36 * s, y), radius=16 * s, fill=WHITE)
        hx, hy = x + sway(t, 3 * s), y - 292 * s - bob
        if pose == 'phone':
            line(d, [(x + 30 * s, y - 220 * s - bob), (x + 95 * s, y - 250 * s - bob)], width=int(22 * s))
            rrect(d, (x + 80 * s, y - 300 * s - bob, x + 130 * s, y - 225 * s - bob), 8 * s, fill=(20, 20, 20), outline=WHITE, width=int(6 * s))
            paste_glow_later.append((x + 105 * s, y - 262 * s, int(70 * s)))
        elif pose == 'keys':
            jig = 4 * s * math.sin(t * 9)
            line(d, [(x + 30 * s, y - 220 * s - bob), (x + 85 * s, y - 180 * s - bob)], width=int(22 * s))
            circle(d, (x + 100 * s, y - 170 * s - bob + jig), 14 * s, outline=YELLOW, width=int(6 * s))
            d.line((x + 108 * s, y - 160 * s - bob + jig, x + 135 * s, y - 135 * s - bob + jig), fill=YELLOW, width=int(6 * s))
        elif arm == 'up':
            k = ease_out(t / 0.8)
            ax, ay = x + 80 * s, y - 300 * s
            line(d, [(x + 30 * s, y - 220 * s - bob), (x + 30 * s + (ax - x - 30 * s) * k, y - 180 * s + (ay - y + 180 * s) * k)], width=int(22 * s))
        elif pose == 'walk':
            sw = walk_cycle(t)['arm']
            line(d, [(x + 20 * s, y - 220 * s - bob), (x + 20 * s + 50 * s * sw, y - 140 * s)], width=int(20 * s))
    circle(d, (hx, hy), head_r, fill=WHITE, outline=WHITE)
    if sunglasses:
        d.rounded_rectangle((hx - 6 * s, hy - 10 * s, hx + 44 * s, hy + 6 * s), radius=6 * s, fill=(0, 0, 0))
        d.polygon([(hx - 10 * s, hy + 50 * s), (hx + 10 * s, hy + 50 * s), (hx, hy + 110 * s)], fill=(0, 0, 0))
    else:
        if eyes == RED:
            circle(d, (hx + 18 * s, hy - 4 * s), 6 * s, fill=RED, outline=RED)
        elif blink(t, 3.3, x * 0.001):
            d.line((hx + 10 * s, hy - 2 * s, hx + 28 * s, hy - 2 * s), fill=(0, 0, 0), width=int(4 * s))
        else:
            d.line((hx + 10 * s, hy - 4 * s, hx + 28 * s, hy - 4 * s), fill=(0, 0, 0), width=int(6 * s))

paste_glow_later = []

def tail(d, base, length, base_angle, t, amp=22, rate=5.0, width=14, mode='damped'):
    a = math.radians(base_angle + tail_wag(t, mode, amp, rate))
    tip = (base[0] + length * math.cos(a), base[1] - length * math.sin(a))
    mid = (base[0] + length * 0.55 * math.cos(a - 0.25), base[1] - length * 0.55 * math.sin(a - 0.25))
    line(d, [base, mid, tip], width=width)

def dog(d, c, pose='four', scale=1.0, eyes=None, smile=False, coat=False, t=0.0, wag='slow'):
    """c = ground center. pose: four, two, flat. wag: fast (happy), slow (wrong), none."""
    s = scale; x, y = c
    bob = breathe(t, 2.5 * s, 0.5, x * 0.013)
    amp, rate = {'fast': (30, 1.6), 'slow': (10, 0.8), 'none': (0, 0), 'loop': (28, 4.5)}[wag]
    tmode = 'loop' if wag == 'loop' else 'damped'
    if pose == 'two':
        sway_ = sway(t, 3 * s, 0.8)
        d.rounded_rectangle((x - 46 * s + sway_, y - 250 * s - bob, x + 46 * s + sway_, y - 80 * s), radius=40 * s, fill=WHITE)
        d.rounded_rectangle((x - 44 * s, y - 100 * s, x - 10 * s, y), radius=16 * s, fill=WHITE)
        d.rounded_rectangle((x + 10 * s, y - 100 * s, x + 44 * s, y), radius=16 * s, fill=WHITE)
        line(d, [(x - 40 * s + sway_, y - 210 * s - bob), (x - 90 * s + sway_, y - 150 * s - bob)], width=int(20 * s))
        line(d, [(x + 40 * s + sway_, y - 210 * s - bob), (x + 90 * s + sway_, y - 150 * s - bob)], width=int(20 * s))
        tail(d, (x + 30 * s, y - 100 * s), 80 * s, 40, t, amp, rate, int(14 * s), tmode)
        hx, hy = x + sway_ * 1.5, y - 300 * s - bob
        circle(d, (hx, hy), 46 * s, fill=WHITE, outline=WHITE)
        d.rounded_rectangle((hx + 20 * s, hy - 5 * s, hx + 80 * s, hy + 30 * s), radius=14 * s, fill=WHITE)
        flick = 6 * s * IDLE['sway'] if ((t + 1.1) % 4.0) < 0.15 else 0
        d.polygon([(hx - 40 * s, hy - 30 * s), (hx - 10 * s, hy - 40 * s), (hx - 38 * s - flick, hy - 95 * s)], fill=WHITE)
        d.polygon([(hx + 10 * s, hy - 40 * s), (hx + 36 * s, hy - 30 * s), (hx + 34 * s + flick, hy - 95 * s)], fill=WHITE)
        if coat:
            d.rounded_rectangle((x - 50 * s + sway_, y - 230 * s - bob, x + 50 * s + sway_, y - 120 * s), radius=20 * s, fill=YELLOW)
        ex, ey = hx + 16 * s, hy - 8 * s
    elif pose == 'flat':
        d.rounded_rectangle((x - 200 * s, y - 70 * s - bob * 0.5, x + 10 * s, y - 10 * s), radius=30 * s, fill=WHITE)
        circle(d, (x - 240 * s, y - 42 * s), 44 * s, fill=WHITE, outline=WHITE)
        d.rounded_rectangle((x - 300 * s, y - 50 * s, x - 250 * s, y - 25 * s), radius=10 * s, fill=WHITE)
        d.polygon([(x - 230 * s, y - 80 * s), (x - 200 * s, y - 60 * s), (x - 250 * s, y - 100 * s)], fill=WHITE)
        line(d, [(x - 110 * s, y - 75 * s - bob * 0.5), (x - 80 * s, y - 120 * s - bob)], width=int(16 * s))
        line(d, [(x - 70 * s, y - 75 * s - bob * 0.5), (x - 40 * s, y - 120 * s - bob)], width=int(16 * s))
        tail(d, (x + 5 * s, y - 40 * s), 70 * s, 10, t, amp * 0.4, rate, int(12 * s), tmode)
        ex, ey = x - 252 * s, y - 55 * s
    else:  # four legs, facing right
        d.rounded_rectangle((x - 150 * s, y - 150 * s - bob, x + 90 * s, y - 60 * s), radius=40 * s, fill=WHITE)
        for lx in (-130, -85, 30, 70):
            d.rounded_rectangle((x + lx * s, y - 80 * s, x + (lx + 30) * s, y), radius=12 * s, fill=WHITE)
        tail(d, (x - 150 * s, y - 130 * s - bob), 85 * s, 135, t, amp, rate, int(14 * s), tmode)
        hx, hy = x + 120 * s, y - 170 * s - bob
        circle(d, (hx, hy), 44 * s, fill=WHITE, outline=WHITE)
        d.rounded_rectangle((hx + 20 * s, hy - 5 * s, hx + 85 * s, hy + 30 * s), radius=14 * s, fill=WHITE)
        flick = 6 * s * IDLE['sway'] if ((t + 0.7) % 3.6) < 0.15 else 0
        d.polygon([(hx - 40 * s, hy - 30 * s), (hx - 10 * s, hy - 40 * s), (hx - 38 * s - flick, hy - 95 * s)], fill=WHITE)
        ex, ey = hx + 16 * s, hy - 8 * s
    if eyes == RED:
        circle(d, (ex, ey), 7 * s, fill=RED, outline=RED)
    elif blink(t, 4.1, x * 0.002):
        d.line((ex - 6 * s, ey, ex + 6 * s, ey), fill=(0, 0, 0), width=int(3 * s))
    else:
        circle(d, (ex, ey), 5 * s, fill=(0, 0, 0), outline=(0, 0, 0))
    if smile and pose == 'two':
        k = ease_out((t - 0.4) / 0.6)
        if k > 0: d.arc((hx + 22 * s, hy + 2 * s, hx + 78 * s, hy + 34 * s), 10, 10 + int(160 * k), fill=RED, width=int(6 * s))

def door(d, c, handle=True, lock=False, open_=False, handle_color=WHITE, scale=1.0):
    s = scale; x, y = c
    rrect(d, (x - 110 * s, y - 380 * s, x + 110 * s, y), 10 * s, fill=(12, 12, 12))
    if handle:
        circle(d, (x + 70 * s, y - 190 * s), 14 * s, fill=handle_color, outline=handle_color)
    if lock:
        rrect(d, (x + 56 * s, y - 250 * s, x + 84 * s, y - 225 * s), 4 * s, fill=RED, outline=RED, width=2)
        circle(d, (x + 70 * s, y - 262 * s), 11 * s, outline=RED, width=int(6 * s))

def bed(d, c, scale=1.0):
    s = scale; x, y = c
    d.rounded_rectangle((x - 260 * s, y - 70 * s, x + 260 * s, y), radius=18 * s, fill=WHITE)
    d.rounded_rectangle((x - 300 * s, y - 180 * s, x - 260 * s, y), radius=10 * s, fill=WHITE)  # headboard
    d.rounded_rectangle((x - 250 * s, y - 110 * s, x - 140 * s, y - 75 * s), radius=14 * s, fill=(30, 30, 30))  # pillow
    d.rectangle((x - 255 * s, y, x - 225 * s, y + 40 * s), fill=WHITE)
    d.rectangle((x + 225 * s, y, x + 255 * s, y + 40 * s), fill=WHITE)

def tv(d, c, scale=1.0, on=True):
    s = scale; x, y = c
    rrect(d, (x - 150 * s, y - 200 * s, x + 150 * s, y - 20 * s), 12 * s, fill=(10, 10, 10))
    d.rectangle((x - 20 * s, y - 20 * s, x + 20 * s, y), fill=WHITE)
    d.rectangle((x - 80 * s, y, x + 80 * s, y + 10 * s), fill=WHITE)
    if on: paste_glow_later.append((x, y - 110 * s, int(150 * s)))

def chair(d, c, scale=1.0):
    s = scale; x, y = c
    d.rounded_rectangle((x - 90 * s, y - 120 * s, x + 90 * s, y - 80 * s), radius=14 * s, fill=WHITE)
    d.rounded_rectangle((x - 100 * s, y - 280 * s, x - 60 * s, y - 100 * s), radius=14 * s, fill=WHITE)
    d.rectangle((x - 80 * s, y - 80 * s, x - 55 * s, y), fill=WHITE)
    d.rectangle((x + 55 * s, y - 80 * s, x + 80 * s, y), fill=WHITE)

def table(d, c, scale=1.0):
    s = scale; x, y = c
    d.rounded_rectangle((x - 200 * s, y - 150 * s, x + 200 * s, y - 125 * s), radius=8 * s, fill=WHITE)
    d.rectangle((x - 170 * s, y - 125 * s, x - 145 * s, y), fill=WHITE)
    d.rectangle((x + 145 * s, y - 125 * s, x + 170 * s, y), fill=WHITE)
    circle(d, (x, y - 162 * s), 40 * s, outline=WHITE, width=int(8 * s))

def fridge(d, c, scale=1.0, open_=False):
    s = scale; x, y = c
    rrect(d, (x - 110 * s, y - 400 * s, x + 110 * s, y), 14 * s, fill=(12, 12, 12))
    d.line((x - 110 * s, y - 270 * s, x + 110 * s, y - 270 * s), fill=WHITE, width=STROKE)
    d.rounded_rectangle((x + 70 * s, y - 360 * s, x + 86 * s, y - 300 * s), radius=6 * s, fill=WHITE)
    d.rounded_rectangle((x + 70 * s, y - 240 * s, x + 86 * s, y - 120 * s), radius=6 * s, fill=WHITE)
    if open_: paste_glow_later.append((x - 110 * s, y - 200 * s, int(140 * s)))

def phone(d, c, scale=1.0, glow=True, camera=False, progress=None, play=False):
    s = scale; x, y = c
    rrect(d, (x - 110 * s, y - 220 * s, x + 110 * s, y + 220 * s), 36 * s, fill=(14, 14, 14))
    if glow: paste_glow_later.append((x, y, int(230 * s)))
    if camera:
        circle(d, (x, y - 20 * s), 60 * s, outline=WHITE, width=int(10 * s))
        circle(d, (x, y - 20 * s), 20 * s, fill=WHITE, outline=WHITE)
        d.ellipse((x - 10 * s, y + 90 * s, x + 10 * s, y + 110 * s), fill=RED)
    if progress is not None:
        d.rounded_rectangle((x - 80 * s, y + 150 * s, x + 80 * s, y + 160 * s), radius=5 * s, fill=(60, 60, 60))
        d.rounded_rectangle((x - 80 * s, y + 150 * s, x - 80 * s + 160 * s * progress, y + 160 * s), radius=5 * s, fill=RED)
    if play:
        d.polygon([(x - 30 * s, y - 50 * s), (x - 30 * s, y + 50 * s), (x + 50 * s, y)], fill=WHITE)

def eye(d, c, scale=1.0, red=False, closed=False, look=(0, 0)):
    s = scale; x, y = c
    if closed:
        d.arc((x - 150 * s, y - 60 * s, x + 150 * s, y + 90 * s), 200, 340, fill=WHITE, width=int(12 * s))
        return
    d.arc((x - 150 * s, y - 80 * s, x + 150 * s, y + 80 * s), 200, 340, fill=WHITE, width=int(12 * s))
    d.arc((x - 150 * s, y - 80 * s, x + 150 * s, y + 80 * s), 20, 160, fill=WHITE, width=int(12 * s))
    px, py = x + look[0] * s, y + look[1] * s
    circle(d, (px, py), 42 * s, fill=RED if red else WHITE, outline=RED if red else WHITE)
    circle(d, (px, py), 16 * s, fill=(0, 0, 0), outline=(0, 0, 0))

def speech_bubble(d, c, text, scale=1.0, color=WHITE, textcolor=(0, 0, 0), f=None, tail='left'):
    s = scale; x, y = c
    f = f or F_CARD
    tw = text_width(d, text, f, 2) + 60 * s
    th = f.size + 50 * s
    d.rounded_rectangle((x - tw / 2, y - th / 2, x + tw / 2, y + th / 2), radius=24 * s, fill=color)
    if tail == 'left':
        d.polygon([(x - tw / 2 + 40 * s, y + th / 2 - 2), (x - tw / 2 + 90 * s, y + th / 2 - 2), (x - tw / 2 + 30 * s, y + th / 2 + 50 * s)], fill=color)
    draw_spaced(d, (x, y), text, f, textcolor, 2)

def wall(d, x, y0, y1):
    d.rectangle((x - 14, y0, x + 14, y1), fill=WHITE)

def ear(d, c, scale=1.0, red=False):
    s = scale; x, y = c
    col = RED if red else WHITE
    d.arc((x - 60 * s, y - 90 * s, x + 60 * s, y + 90 * s), 230, 130, fill=col, width=int(12 * s))
    d.arc((x - 30 * s, y - 50 * s, x + 30 * s, y + 10 * s), 200, 20, fill=col, width=int(10 * s))
    d.line((x + 20 * s, y, x + 20 * s, y + 60 * s), fill=col, width=int(10 * s))

def waveform(d, c, t, scale=1.0, color=YELLOW, bars=14, broken=False):
    s = scale; x, y = c
    gap = 26 * s
    x0 = x - gap * (bars - 1) / 2
    for i in range(bars):
        h = (30 + 60 * abs(math.sin(i * 1.3 + t * 6))) * s
        if broken and i in (4, 5, 9, 10): h = 6 * s
        d.rounded_rectangle((x0 + i * gap - 7 * s, y - h / 2, x0 + i * gap + 7 * s, y + h / 2), radius=7 * s, fill=color)

def doorbell(d, c, scale=1.0, ringing=False, t=0):
    s = scale; x, y = c
    rrect(d, (x - 50 * s, y - 90 * s, x + 50 * s, y + 90 * s), 16 * s, fill=(12, 12, 12))
    circle(d, (x, y + 30 * s), 22 * s, fill=RED if ringing else WHITE, outline=RED if ringing else WHITE)
    circle(d, (x, y - 40 * s), 14 * s, outline=WHITE, width=int(6 * s))
    if ringing:
        k = (t * 3) % 1
        for i in range(2):
            r = (60 + 50 * ((k + i * 0.5) % 1)) * s
            d.arc((x - r, y + 30 * s - r, x + r, y + 30 * s + r), 300, 60, fill=RED, width=int(6 * s))
            d.arc((x - r, y + 30 * s - r, x + r, y + 30 * s + r), 120, 240, fill=RED, width=int(6 * s))

def keys(d, c, scale=1.0, color=WHITE):
    s = scale; x, y = c
    circle(d, (x - 60 * s, y), 46 * s, outline=color, width=int(14 * s))
    d.line((x - 20 * s, y, x + 120 * s, y), fill=color, width=int(16 * s))
    d.line((x + 80 * s, y, x + 80 * s, y + 40 * s), fill=color, width=int(14 * s))
    d.line((x + 115 * s, y, x + 115 * s, y + 30 * s), fill=color, width=int(14 * s))

def clock(d, c, scale=1.0, hour=3, t=0.0):
    s = scale; x, y = c
    sa = math.radians(t * 6 * 10 - 90)
    d.line((x, y, x + 95 * s * math.cos(sa), y + 95 * s * math.sin(sa)), fill=RED, width=int(4 * s))
    circle(d, (x, y), 110 * s, outline=WHITE, width=int(10 * s))
    a = math.radians(hour * 30 - 90)
    d.line((x, y, x + 60 * s * math.cos(a), y + 60 * s * math.sin(a)), fill=WHITE, width=int(10 * s))
    d.line((x, y, x, y - 85 * s), fill=WHITE, width=int(8 * s))

def seven_boxes(d, c, current=None, red=None, redacted=None, scale=1.0, t=0):
    s = scale; x, y = c
    gap = 110 * s
    x0 = x - gap * 3
    for i in range(7):
        bx = x0 + i * gap
        k = ease_out((t + 0.1 - i * 0.05) / 0.25)
        if k <= 0: continue
        n = i + 1
        pulse = 1 + 0.05 * math.sin(2 * math.pi * 1.2 * t) if n in (red, current, redacted) else 1
        sz = 80 * s * k * pulse
        box = (bx - sz / 2, y - sz / 2, bx + sz / 2, y + sz / 2)
        if red == n:
            d.rounded_rectangle(box, radius=12 * s, fill=RED)
            draw_spaced(d, (bx, y), str(n), font(800, int(44 * s)), WHITE, 0)
        elif redacted == n:
            d.rounded_rectangle(box, radius=12 * s, outline=WHITE, width=int(6 * s))
            d.rectangle((bx - 24 * s, y - 8 * s, bx + 24 * s, y + 8 * s), fill=GREY)
        elif current == n:
            d.rounded_rectangle(box, radius=12 * s, fill=WHITE)
            draw_spaced(d, (bx, y), str(n), font(800, int(44 * s)), (0, 0, 0), 0)
        else:
            d.rounded_rectangle(box, radius=12 * s, outline=WHITE, width=int(6 * s))
            draw_spaced(d, (bx, y), str(n), font(800, int(44 * s)), WHITE, 0)

def seal(d, c, scale=1.0, t=0):
    s = scale; x, y = c
    k = ease_out(t / 0.6)
    circle(d, (x, y), 150 * s * k, outline=WHITE, width=int(8 * s))
    circle(d, (x, y), 120 * s * k, outline=WHITE, width=int(4 * s))
    if k > 0.9:
        draw_spaced(d, (x, y - 30 * s), 'DEPT. OF', font(700, int(26 * s)), WHITE, 4)
        draw_spaced(d, (x, y + 6 * s), 'DOMESTIC', font(700, int(26 * s)), WHITE, 4)
        draw_spaced(d, (x, y + 42 * s), 'ANOMALIES', font(700, int(26 * s)), WHITE, 4)

GROUND = 760  # y of the floor line in the stage

def floor_line(d, x0=560, x1=1360):
    d.line((x0, GROUND + 6, x1, GROUND + 6), fill=(70, 70, 70), width=4)


# =====================================================================================
# v3 additions, measured from the two reference videos (see claude/animation-bible.md)
# =====================================================================================

def tail_wag(t, mode='damped', amp=30, rate=1.6):
    """Tail angle offset in degrees. Measured: one damped wag of 2 swings (24 px at the tip of an 85 px tail,
    1.6 Hz) then still. 'loop' = the old continuous wag. 'none' = still."""
    if mode == 'none' or amp == 0: return 0.0
    if mode == 'loop': return amp * math.sin(2 * math.pi * rate * t)
    if t > 1.4: return 0.0
    return amp * math.exp(-t / 0.55) * math.sin(2 * math.pi * rate * t)

def walk_cycle(t, period=1.0):
    """Measured in-place walk: a step every period/2 (0.5 s), head bob 6 px p2p at 2 Hz, stride about 0.2 of height.
    Returns leg (-1..1), arm (-1..1, opposite phase), bob (px, down positive)."""
    ph = 2 * math.pi * t / period
    return {'leg': math.sin(ph), 'arm': -math.sin(ph), 'bob': -3.0 * (1 - math.cos(2 * ph))}

def run_cycle(t, period=0.5, animate=False):
    """The reference 'do not run' shot is a static running pose with three speed lines (0 px of change over 27
    frames). Default static. animate=True gives a 2 steps per second cycle for a figure that really runs."""
    if not animate: return {'leg': 1.0, 'arm': 1.0, 'bob': 0.0, 'lines': 1.0}
    ph = 2 * math.pi * t / period
    return {'leg': math.sin(ph), 'arm': -math.sin(ph), 'bob': -4.0 * (1 - math.cos(2 * ph)), 'lines': 1.0}

def stand_up(t, start=0.0, dur=0.33):
    """Dog rising on two legs: body rotates 0 to 90 degrees about the hip in 10 frames with ease out (measured
    per-frame steps about 15,20,20,15,10,5,3,2,1,0 degrees). Returns the angle in degrees."""
    return 90.0 * ease_out((t - start) / dur)

def draw_on(t, frames, start=0.0, fps=30):
    """Progress 0..1 of a draw on that takes `frames` frames with ease out (measured dotted lines: 40,25,15,10,10
    percent per 2 frames over 10 frames). X marks use frames=2."""
    return ease_out((t - start) / (frames / fps))

def arm_lift(t, start=0.0, frames=15, angle=70):
    """Forearm rotation to the mouth: about 70 degrees in 15 frames, ease out, then hold."""
    return angle * ease_out((t - start) / (frames / 30))

def stagger_pop(t, i, start=0.3, gap=0.3, frames=4):
    """Scale 0..1 for the i-th popped element. Measured: items 9 frames apart, each scales in over 4 frames
    with ease out and no overshoot (52, 92, 97, 100 percent)."""
    return ease_out((t - start - i * gap) / (frames / 30))

def head_turn(t, start=0.0, frames=4):
    """Reference never rotates a head; a turn is a 4 frame flip of the facing side. Returns -1 (left) .. 1 (right)."""
    return -1 + 2 * ease_out((t - start) / (frames / 30))

def eyes_light_up(t, start):
    """Instant. Measured: the red appears inside a 5 frame glitch or on the frame a sight line arrives.
    Returns True once lit. Pair with a glitch hit at `start` in the shot list."""
    return t >= start

def lights_fail(t, start, eye_gap=0.2, back_after=0.6):
    """B 5:22 recipe. Returns (scene_brightness 0..1, eye_pairs_lit 0..3). bright, dim, dimmer, bright, black over
    4 frames, then one pair of eyes every 6 frames, lights back 2 frames after back_after."""
    u = t - start
    if u < 0: return 1.0, 0
    seq = [1.0, 0.45, 0.25, 1.0]
    f = int(u * 30)
    if f < 4: return seq[f], 0
    if u < 0.13 + back_after:
        return 0.0, min(3, int((u - 0.13) / eye_gap) + 1)
    return min(1.0, 0.5 + (u - 0.13 - back_after) * 15), 3

def one_frame_flash(f, start_f, pattern=(3, -1, 12)):
    """Black flash pattern before the big word: black 3, picture 1, black 12 frames (measured). Returns
    'black', 'show' or None when outside the pattern. Negative numbers are picture frames."""
    k = f - start_f
    if k < 0: return None
    for n in pattern:
        L = abs(n)
        if k < L: return 'black' if n > 0 else 'show'
        k -= L
    return None

# ---------- film layer and glitch ----------
def glitch_frame(img, strength=1.0, seed=0, heavy=True):
    """Measured glitch frame. heavy: R left / B right 10 to 27 px at 1080p, 6+ slices 15 to 100 px tall shifted
    up to 120 px, 30 to 80 white streaks 1 to 3 px tall and 10 to 90 px long, 2 horizontal echoes at 40 percent,
    frame scaled 1.03. light: split 6 to 10 px, 10 to 20 streaks, no slices."""
    import numpy as np
    rng = random.Random(seed)
    a = np.asarray(img).copy(); h, w, _ = a.shape
    dx = int((rng.uniform(10, 27) if heavy else rng.uniform(6, 10)) * strength)
    def shift(arr, off):
        out = np.zeros_like(arr)
        if off > 0: out[:, off:] = arr[:, :-off]
        elif off < 0: out[:, :off] = arr[:, -off:]
        else: out[:] = arr
        return out
    base = a.copy()
    a[:, :, 0] = shift(base[:, :, 0], -dx)
    a[:, :, 2] = shift(base[:, :, 2], dx)
    if heavy:
        for _ in range(rng.randint(6, 10)):
            y = rng.randint(0, h - 100); hh = rng.randint(15, 100); off = rng.randint(-80, 80)
            a[y:y + hh] = shift(a[y:y + hh], off)
        for off in (rng.randint(20, 60), -rng.randint(20, 60)):
            echo = shift(base, off).astype(np.int16)
            a = np.clip(a.astype(np.int16) + (echo * 0.3).astype(np.int16), 0, 255).astype(np.uint8)
    for _ in range(rng.randint(30, 80) if heavy else rng.randint(10, 20)):
        y = rng.randint(0, h - 3); hh = rng.randint(1, 3); x0 = rng.randint(0, w - 100); L = rng.randint(10, 90)
        v = rng.randint(140, 255)
        a[y:y + hh, x0:x0 + L] = v
    im = Image.fromarray(a)
    if heavy:
        s = 1.03; cw, ch = int(w / s), int(h / s)
        im = im.crop(((w - cw) // 2, (h - ch) // 2, (w - cw) // 2 + cw, (h - ch) // 2 + ch)).resize((w, h), Image.BILINEAR)
    return im

GLITCH_PATTERN = [True, True, True, False, False, True, True, False, False, False]  # heavy/light per frame, measured

def film_floor(img, seed=0, floor=2, specks=2):
    """Lift pure black to a 1..3 grain floor and add a few bright dust specks (measured: 1 to 3 per second
    in any 60x100 block, up to 75..144 of 255). Call once per frame before the ffmpeg noise filter."""
    import numpy as np
    rng = np.random.default_rng(seed)
    a = np.asarray(img).astype(np.int16)
    a += rng.integers(0, floor + 2, size=a.shape[:2], dtype=np.int16)[:, :, None]
    h, w = a.shape[:2]
    for _ in range(specks):
        x, y = rng.integers(0, w - 3), rng.integers(0, h - 3)
        a[y:y + rng.integers(1, 3), x:x + rng.integers(1, 4)] = rng.integers(70, 150)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

# ---------- camera coverage ----------
# Named framings in 1920x1080 wide-scene coordinates: (center_x, center_y, zoom). Measured on Video B.
# Zoom here is body based (table top lands at 0.76 of the frame height, like the reference), which is smaller than
# the pupil based zoom in the bible because the reference redraws the face wider at close framings.
FRAMINGS = {'WIDE': (960, 500, 1.0), 'MEDIUM': (1089, 553, 1.5), 'MED_LEFT': (495, 568, 1.6),
            'MED_RIGHT': (1210, 568, 1.6), 'CLOSE': (1209, 574, 1.9), 'FACE': (1209, 372, 3.5)}

def camera(draw_fn, target='WIDE', zoom=None, t=0.0, push=0.0, dur=None, ss=2, move_to=None, move_t=(0.0, 1.9)):
    """Build once, then frame. draw_fn(d, img, s) must draw the whole scene in wide coordinates multiplied by s.
    target: a FRAMINGS name or (cx, cy, zoom). push: extra zoom fraction reached at the end of the shot with
    ease in/out after a 0.5 s delay (measured 0.03 to 0.05). move_to: another framing to push to between
    move_t[0] and move_t[1] seconds (measured continuous push: 1.9 s, ease in/out). Returns an RGBA image W x H."""
    cx, cy, z = FRAMINGS.get(target, target) if isinstance(target, str) else target
    if zoom: z = zoom
    if move_to:
        cx2, cy2, z2 = FRAMINGS.get(move_to, move_to) if isinstance(move_to, str) else move_to
        k = ease_in_out((t - move_t[0]) / max(0.01, move_t[1] - move_t[0]))
        cx, cy, z = cx + (cx2 - cx) * k, cy + (cy2 - cy) * k, z + (z2 - z) * k
    if push and dur:
        z *= 1 + push * ease_in_out((t - 0.5) / max(0.1, dur - 0.5))
    canvas = Image.new('RGBA', (W * ss, H * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    draw_fn(d, canvas, ss)
    cw, ch = W * ss / z, H * ss / z
    x0, y0 = cx * ss - cw / 2, cy * ss - ch / 2
    return canvas.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)

def lamp_cone(img, d, c, s=1.0, on=True, half_angle=45, reach=None, alpha=0.42, scale=1.0):
    """Measured lamp: white dome, bulb glow (253,253,117), cone of CONE color at 42 percent over black with a
    45 degree half angle starting at the bulb width. Draw FIRST, figures go on top untinted. c = bulb center."""
    x, y = c[0] * s, c[1] * s
    sc = s * scale
    reach = (reach or 470) * sc
    bw = 122 * sc  # half width of the bulb at 1080p
    if on:
        layer = Image.new('RGBA', img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
        spread = reach * math.tan(math.radians(half_angle))
        ld.polygon([(x - bw, y), (x + bw, y), (x + bw + spread, y + reach), (x - bw - spread, y + reach)], fill=CONE + (int(255 * alpha),))
        img.alpha_composite(layer)
        d.ellipse((x - bw, y - 14 * sc, x + bw, y + 14 * sc), fill=BULB)
    d.pieslice((x - 140 * sc, y - 120 * sc, x + 140 * sc, y + 100 * sc), 180, 360, fill=WHITE)
    d.rectangle((x - 4 * sc, y - 200 * sc, x + 4 * sc, y - 110 * sc), fill=WHITE)

def freeze_outline(d, t=0.0, inset=30, dash=30, gap=15, width=6, color=WHITE):
    """Measured 'the whole table stops' frame: white dashed rounded rectangle inset from the frame edge, instant."""
    x0, y0, x1, y1 = inset, inset + 100, W - inset, H - inset - 180
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    for a, b in zip(pts, pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L; u = 0
        while u < L:
            u2 = min(u + dash, L)
            d.line((a[0] + ux * u, a[1] + uy * u, a[0] + ux * u2, a[1] + uy * u2), fill=color, width=width)
            u += dash + gap

def dotted_line(d, a, b, frac=1.0, color=WHITE, dot=4, gap=8):
    """Dotted sight line (measured: dots 3 px, gap 5 px at 720p)."""
    L = math.hypot(b[0] - a[0], b[1] - a[1]); 
    if L <= 0: return
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L; u = 0
    while u < L * clamp(frac, 0, 1):
        d.ellipse((a[0] + ux * u - dot / 2, a[1] + uy * u - dot / 2, a[0] + ux * u + dot / 2, a[1] + uy * u + dot / 2), fill=color)
        u += dot + gap

def sight_line(d, frm, to, t, start=0.4, frames=10, color=WHITE):
    dotted_line(d, frm, to, draw_on(t, frames, start), color=color)

def speech_bubble_dialogue(d, c, text, t, start=0.2, tail_to=None, f=None, scale=1.0, caps=False):
    """Measured B bubble: white fill, black 5 px outline, radius 18, mixed case, pops over 3 frames with ease out,
    tail toward the speaker. c = bubble center. Holds until the cut."""
    k = ease_out((t - start) / 0.1)
    if k <= 0: return
    f = f or F_DIALOG
    s = scale * k
    tw = text_width(d, text, f, 1) + 50 * scale; th = f.size + 40 * scale
    x, y = c
    box = (x - tw / 2 * k, y - th / 2 * k, x + tw / 2 * k, y + th / 2 * k)
    d.rounded_rectangle(box, radius=18 * s, fill=WHITE, outline=OUTLINE, width=max(1, int(5 * s)))
    if tail_to and k > 0.8:
        tx, ty = tail_to
        bx = clamp(tx, box[0] + 30, box[2] - 30)
        d.polygon([(bx - 14, box[3] - 3), (bx + 14, box[3] - 3), (tx, min(ty, box[3] + 40))], fill=WHITE, outline=OUTLINE)
        d.line((bx - 13, box[3] - 2, bx + 13, box[3] - 2), fill=WHITE, width=6)
    if k > 0.95: draw_spaced(d, (x, y), text, f, (0, 0, 0), 1)

def thought_bubble(d, c, t, start=0.3, r=120, icon=None):
    k = ease_out((t - start) / 0.13)
    if k <= 0: return
    x, y = c
    d.ellipse((x - r * k, y - r * 0.7 * k, x + r * k, y + r * 0.7 * k), outline=WHITE, width=6)
    d.ellipse((x - r * 0.9 - 30, y + r * 0.6, x - r * 0.9 - 6, y + r * 0.6 + 24), outline=WHITE, width=5)
    d.ellipse((x - r * 0.9 - 56, y + r * 0.8, x - r * 0.9 - 42, y + r * 0.8 + 14), outline=WHITE, width=4)
    if icon and k > 0.9: icon(d, (x, y))

def photo_insert(img, d, path, t, label='EXHIBIT A', lines=('YEAR: 1897',), seed=0, tight=False, box=(400, 150, 1000, 830)):
    """Measured exhibit: photo at 0.6 of frame height, white 12 px frame, rotated 1.5 degrees, corner brackets,
    red bar + label + grey lines at right, heavy animated grain (std 20) on the photo only. tight=True is the
    1.31x jump cut used for the next caption (label gone)."""
    import numpy as np
    x0, y0, x1, y1 = box
    if tight:
        cx, cy = (x0 + x1) / 2 + 60, (y0 + y1) / 2 - 30; w, h = (x1 - x0) * 1.31, (y1 - y0) * 1.31
        x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    try:
        ph = Image.open(path).convert('L')
    except Exception:
        ph = Image.new('L', (400, 500), 60)
    ph = ph.resize((int(x1 - x0), int(y1 - y0)))
    a = np.asarray(ph).astype(np.int16)
    rng = np.random.default_rng(seed + int(t * 30))
    a = np.clip(a + rng.normal(0, 20, a.shape), 0, 255).astype(np.uint8)
    ph = Image.fromarray(a).convert('RGBA')
    frame = Image.new('RGBA', (ph.width + 24, ph.height + 24), WHITE + (255,))
    frame.paste(ph, (12, 12))
    frame = frame.rotate(-1.5, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(frame, (int(x0) - 12, int(y0) - 12))
    if not tight:
        bl = 30; bx0, by0, bx1, by1 = x0 - 30, y0 - 30, x1 + 30, y1 + 30
        for (px, py, sx, sy) in ((bx0, by0, 1, 1), (bx1, by0, -1, 1), (bx0, by1, 1, -1), (bx1, by1, -1, -1)):
            d.line((px, py, px + sx * bl, py), fill=GREY, width=3); d.line((px, py, px, py + sy * bl), fill=GREY, width=3)
        lx = x1 + 80
        d.rectangle((lx, y0 + 10, lx + 9, y0 + 64), fill=RED)
        draw_spaced(d, (lx + 30, y0 + 36), label, font(700, 34), WHITE, 5, anchor='left')
        for i, ln in enumerate(lines):
            draw_spaced(d, (lx + 30, y0 + 96 + i * 36), ln, F_SMALLCAPS, (170, 170, 170), 3, anchor='left')

# ---------- dinner table rigs (Video B style: white fill, black outline) ----------
def _o(s): return max(2, int(5 * s))

def diner(d, c, who='you', s=1.0, t=0.0, fork=True, fork_lift=0.0, red_eyes=True, smile_corner=0.0, jaw=0.0, tears=False, phone=False):
    """One seated family member. c = table edge center under the figure, in current canvas pixels; s = scale.
    who: mother (bun), father (cap), kid (small, spikes), you (plain, from behind), grandpa (spikes, red eyes, teeth)."""
    x, y = c
    k = 0.8 if who == 'kid' else 1.0
    hr = 90 * s * k
    # chair backs
    for dx in (-115, 115):
        d.rounded_rectangle((x + dx * s - 18 * s, y - 330 * s, x + dx * s + 18 * s, y - 20 * s), radius=18 * s, fill=WHITE, outline=OUTLINE, width=_o(s))
    # body: rounded shoulders
    d.rounded_rectangle((x - 110 * s * k, y - 230 * s * k, x + 110 * s * k, y + 10 * s), radius=70 * s, fill=WHITE, outline=OUTLINE, width=_o(s))
    # arms in a U on the table
    for sgn in (-1, 1):
        ax = x + sgn * 95 * s * k
        d.rounded_rectangle((ax - 26 * s, y - 150 * s * k, ax + 26 * s, y - 10 * s), radius=26 * s, fill=WHITE, outline=OUTLINE, width=_o(s))
        d.ellipse((ax - 30 * s, y - 50 * s, ax + 30 * s, y + 6 * s), fill=WHITE, outline=OUTLINE, width=_o(s))
    # fork (right hand), lifted by fork_lift degrees about the elbow
    if fork:
        ex, ey = x + 95 * s * k, y - 40 * s
        a = math.radians(90 + fork_lift)
        fx, fy = ex + 70 * s * math.cos(a), ey - 70 * s * math.sin(a)
        d.line((ex, ey, fx, fy), fill=OUTLINE, width=int(14 * s)); d.line((ex, ey, fx, fy), fill=WHITE, width=int(7 * s))
        hw = 16 * s
        head = [(fx + hw * math.sin(a), fy + hw * math.cos(a)), (fx - hw * math.sin(a), fy - hw * math.cos(a)),
                (fx - hw * math.sin(a) + 26 * s * math.cos(a), fy - hw * math.cos(a) - 26 * s * math.sin(a)), (fx + hw * math.sin(a) + 26 * s * math.cos(a), fy + hw * math.cos(a) - 26 * s * math.sin(a))]
        d.polygon(head, fill=WHITE, outline=OUTLINE)
        for i in (-0.5, 0.5):
            d.line((fx + i * hw * math.sin(a) + 8 * s * math.cos(a), fy + i * hw * math.cos(a) - 8 * s * math.sin(a), fx + i * hw * math.sin(a) + 24 * s * math.cos(a), fy + i * hw * math.cos(a) - 24 * s * math.sin(a)), fill=OUTLINE, width=max(1, int(2 * s)))
    if phone:
        d.rounded_rectangle((x - 20 * s, y - 120 * s, x + 20 * s, y - 50 * s), radius=6 * s, fill=(20, 20, 20), outline=WHITE, width=int(3 * s))
    # head
    hy = y - 230 * s * k - hr * 0.6
    d.ellipse((x - hr, hy - hr, x + hr, hy + hr), fill=WHITE, outline=OUTLINE, width=_o(s))
    if who == 'mother':
        d.ellipse((x - hr * 0.95, hy - hr * 1.25, x - hr * 0.35, hy - hr * 0.65), fill=WHITE, outline=OUTLINE, width=_o(s))
        d.arc((x - hr, hy - hr, x + hr, hy + hr * 0.4), 200, 340, fill=OUTLINE, width=_o(s))
        if tears:
            for (tx, ty) in ((x - hr * 0.55, hy + hr * 0.5), (x + hr * 0.5, hy + hr * 0.35)):
                d.polygon([(tx, ty - 14 * s), (tx - 9 * s, ty + 6 * s), (tx + 9 * s, ty + 6 * s)], fill=WHITE, outline=OUTLINE)
                d.ellipse((tx - 9 * s, ty - 2 * s, tx + 9 * s, ty + 14 * s), fill=WHITE, outline=OUTLINE, width=_o(s))
    elif who == 'father':
        d.chord((x - hr, hy - hr, x + hr, hy + hr), 200, 340, fill=WHITE, outline=OUTLINE, width=_o(s))
        d.line((x - hr * 0.9, hy - hr * 0.3, x + hr * 1.1, hy - hr * 0.3), fill=OUTLINE, width=_o(s))
        d.rounded_rectangle((x + hr * 0.5, hy - hr * 0.42, x + hr * 1.25, hy - hr * 0.18), radius=6 * s, fill=WHITE, outline=OUTLINE, width=_o(s))
    elif who == 'kid':
        for i, dx in enumerate((-0.45, 0.0, 0.45)):
            px = x + dx * hr
            d.polygon([(px - 22 * s, hy - hr * 0.85), (px + 22 * s, hy - hr * 0.85), (px, hy - hr * 1.35)], fill=WHITE, outline=OUTLINE)
        d.ellipse((x - hr, hy - hr, x + hr, hy + hr), fill=WHITE, outline=OUTLINE, width=_o(s))
        d.line((x - hr * 0.95, hy - hr * 0.2, x + hr * 0.95, hy - hr * 0.2), fill=OUTLINE, width=_o(s))
    elif who == 'you':
        d.arc((x - hr, hy - hr, x + hr, hy + hr * 0.3), 190, 350, fill=OUTLINE, width=_o(s))
    elif who == 'grandpa':
        for i in range(8):
            a = math.radians(-55 + i * 110 / 7); sgn = 1
            for sgn in (-1, 1):
                bx, by = x + sgn * hr * 0.95 * math.cos(a), hy - hr * 0.95 * math.sin(a) * (1 if sgn > 0 else -1)
                tx, ty = x + sgn * hr * 1.45 * math.cos(a), by - hr * 0.35 * math.sin(a)
                d.polygon([(bx, by - 16 * s), (bx, by + 16 * s), (tx, ty)], fill=WHITE, outline=OUTLINE)
        d.ellipse((x - hr, hy - hr, x + hr, hy + hr), fill=WHITE, outline=OUTLINE, width=_o(s))
        grandpa_face(d, (x, hy), hr, t, red_eyes=red_eyes, smile_corner=smile_corner, jaw=jaw, s=s)
        # napkin tucked in the collar, then the pointed collar on top
        d.polygon([(x + 5 * s, y - 215 * s), (x + 75 * s, y - 205 * s), (x + 40 * s, y - 120 * s)], fill=WHITE, outline=OUTLINE)
        d.polygon([(x - 48 * s, y - 232 * s), (x + 48 * s, y - 232 * s), (x, y - 170 * s)], fill=WHITE, outline=OUTLINE)

def grandpa_face(d, c, hr, t=0.0, red_eyes=True, smile_corner=0.0, jaw=0.0, s=1.0, detail=False):
    """Eyes: dark sockets with red fill and a highlight. Mouth: black band with white teeth. smile_corner 0..1 lifts
    the right corner toward the eye (measured 60 px at close framing over 2.6 s). jaw 0..1 drops the band."""
    x, y = c
    er = hr * 0.2; ex = hr * 0.38; ey = y - hr * 0.1
    for sgn in (-1, 1):
        cx = x + sgn * ex
        d.ellipse((cx - er, ey - er, cx + er, ey + er), fill=(40, 0, 0) if red_eyes else WHITE, outline=OUTLINE, width=_o(s))
        if red_eyes:
            d.ellipse((cx - er * 0.62, ey - er * 0.62, cx + er * 0.62, ey + er * 0.62), fill=RED)
            d.ellipse((cx - er * 0.3, ey - er * 0.35, cx - er * 0.02, ey - er * 0.07), fill=(255, 190, 190))
        else:
            d.ellipse((cx - er * 0.35, ey - er * 0.35, cx + er * 0.35, ey + er * 0.35), fill=OUTLINE)
    my = y + hr * 0.42 + jaw * hr * 0.12
    mw = hr * 0.62; mh = hr * 0.22 + jaw * hr * 0.1
    lift = smile_corner * hr * 0.75
    pts = [(x - mw, my - mh * 0.3), (x - mw * 0.5, my + mh * 0.5), (x, my + mh * 0.6), (x + mw * 0.5, my + mh * 0.5 - lift * 0.3), (x + mw, my - mh * 0.3 - lift)]
    d.polygon(pts + [(x + mw * 0.85, my - mh * 0.9 - lift * 0.9), (x, my - mh * 0.7), (x - mw * 0.85, my - mh * 0.9)], fill=OUTLINE)
    n = 7
    for i in range(n):
        tx = x - mw * 0.8 + i * (1.6 * mw / (n - 1))
        th = mh * 0.75
        d.rectangle((tx - mw * 0.07, my - mh * 0.55 - (lift * 0.5 * i / n), tx + mw * 0.07, my - mh * 0.55 + th - (lift * 0.5 * i / n)), fill=WHITE)

def dinner_table(d, img, s=1.0, t=0.0, lamp=True, who=('mother', 'father', 'kid', 'grandpa'), props=True, grandpa_kw=None, extra=None, clock=True, portrait=True):
    """The whole dinner scene in wide coordinates (1920x1080) times s. Lamp cone first, then table, figures, props.
    Seats at x = 230, 575, 900, 1220 (1080p wide coords); table top y = 690."""
    gk = grandpa_kw or {}
    lamp_cone(img, d, (740, 215), s, on=bool(lamp), reach=460)
    # table slab with gradient top (255 center to 150 at the left end)
    import numpy as np
    tw, th = int(1360 * s), int(90 * s)
    grad = np.linspace(150, 255, tw // 2); row = np.concatenate([grad, np.full(tw - tw // 2, 255)])
    slab = Image.fromarray(np.tile(row.astype(np.uint8), (th, 1))).convert('RGBA')
    img.alpha_composite(slab, (int(70 * s), int(690 * s)))
    d.rounded_rectangle((70 * s, 690 * s, 1430 * s, 780 * s), radius=10 * s, outline=OUTLINE, width=_o(s))
    seats = {'mother': 230, 'father': 575, 'kid': 900, 'grandpa': 1220, 'you': 575}
    for w in who:
        diner(d, (seats[w] * s, 692 * s), w, s, t, **(gk if w == 'grandpa' else {}))
    if props:
        for px in (230, 575, 900, 1220):
            d.ellipse(((px - 70) * s, 675 * s, (px + 70) * s, 720 * s), fill=WHITE, outline=OUTLINE, width=_o(s))
        d.ellipse((700 * s, 650 * s, 800 * s, 690 * s), fill=WHITE, outline=OUTLINE, width=_o(s))  # roast
        d.rounded_rectangle((1395 * s, 620 * s, 1425 * s, 695 * s), radius=4 * s, fill=WHITE, outline=OUTLINE, width=_o(s))  # glass
    if clock:
        d.ellipse((30 * s, 40 * s, 110 * s, 120 * s), outline=WHITE, width=int(6 * s))
        d.line((70 * s, 80 * s, 70 * s, 50 * s), fill=WHITE, width=int(5 * s)); d.line((70 * s, 80 * s, 92 * s, 92 * s), fill=WHITE, width=int(5 * s))
    if portrait:
        d.rounded_rectangle((1660 * s, 60 * s, 1760 * s, 190 * s), radius=6 * s, outline=WHITE, width=int(6 * s))
        d.ellipse((1685 * s, 85 * s, 1735 * s, 135 * s), fill=WHITE); d.rounded_rectangle((1675 * s, 140 * s, 1745 * s, 185 * s), radius=10 * s, fill=WHITE)
    if extra: extra(d, img, s)

# ---------- Video A composites ----------
def dog_face(d, c, s=1.0, red=False, teeth=False, t=0.0, teeth_start=0.0, black_eyes=True):
    """Shield shaped head 210 x 260 px at 720p (315 x 390 at 1080p), two eyes, nose, optional teeth band."""
    x, y = c
    w, h = 158 * s, 195 * s
    d.polygon([(x - w, y - h * 1.15), (x - w * 0.42, y - h * 0.55), (x + w * 0.42, y - h * 0.55), (x + w, y - h * 1.15), (x + w, y - h * 0.4), (x - w, y - h * 0.4)], fill=WHITE)
    d.rounded_rectangle((x - w, y - h * 0.6, x + w, y + h), radius=int(w * 0.7), fill=WHITE)
    for sgn in (-1, 1):
        ex = x + sgn * 42 * s; ey = y - 10 * s
        d.ellipse((ex - 14 * s, ey - 14 * s, ex + 14 * s, ey + 14 * s), fill=RED if red else (0, 0, 0))
    d.ellipse((x - 13 * s, y + 55 * s, x + 13 * s, y + 81 * s), fill=(0, 0, 0))
    if teeth and t >= teeth_start:
        d.rectangle((x - 60 * s, y + 120 * s, x + 60 * s, y + 150 * s), fill=(0, 0, 0))
        for i in range(5):
            tx = x - 50 * s + i * 25 * s
            d.rectangle((tx, y + 124 * s, tx + 17 * s, y + 146 * s), fill=WHITE)

def teeth_smile(d, c, s, t, start=0.0, morph_dur=2.5):
    """A teeth band that appears instantly at start and then widens by a few px over morph_dur (measured)."""
    if t < start: return
    k = clamp((t - start) / morph_dur, 0, 1)
    x, y = c
    hw = (60 + 10 * k) * s
    d.rectangle((x - hw, y - 15 * s - 4 * k * s, x + hw, y + 15 * s), fill=(0, 0, 0))
    n = 5 + int(k > 0.5)
    for i in range(n):
        tx = x - hw + 10 * s + i * (2 * hw - 20 * s) / n
        d.rectangle((tx, y - 11 * s, tx + 17 * s, y + 11 * s), fill=WHITE)

def rec_frame(d, box, t, timecode='00:00:02', live=True, views=None, title=None, progress=None, labels=None):
    """Measured REC overlay: rounded rect outline 6 px, 'REC' with a red dot, 'LIVE', timecode bottom right; optional
    views counter with hearts to the right, progress track and labels."""
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=24, outline=WHITE, width=6)
    if title:
        d.rectangle((x0 + 3, y0 + 3, x1 - 3, y0 + 60), fill=(40, 40, 40))
    draw_spaced(d, (x0 + 40, y0 + 34), 'REC', font(700, 22), WHITE, 3, anchor='left')
    if int(t * 2) % 2 == 0: d.ellipse((x0 + 18, y0 + 26, x0 + 32, y0 + 40), fill=RED)
    if live: draw_spaced(d, (x0 + 30, y1 - 30), 'LIVE', F_TINY, (150, 150, 150), 3, anchor='left')
    if title: draw_spaced(d, (x0 + 30, y1 - 30), title, F_TINY, (150, 150, 150), 3, anchor='left')
    draw_spaced(d, (x1 - 30, y1 - 32), timecode, font(700, 26), WHITE, 2, anchor='right')
    if views is not None:
        draw_spaced(d, (x1 + 60, y0 + 90), 'VIEWS', F_TINY, (150, 150, 150), 3, anchor='left')
        draw_spaced(d, (x1 + 60, y0 + 125), f'{int(views):,}', font(700, 34), WHITE, 1, anchor='left')
        for i in range(3):
            hy = y0 + 180 - ((t * 40 + i * 50) % 120)
            hx = x1 + 70 + i * 28 + 8 * math.sin(t * 3 + i)
            d.polygon([(hx, hy + 8), (hx - 8, hy), (hx - 4, hy - 6), (hx, hy - 2), (hx + 4, hy - 6), (hx + 8, hy)], fill=RED)
    if progress is not None:
        px0, py = x1 + 60, (y0 + y1) / 2
        d.rounded_rectangle((px0, py - 4, px0 + 330, py + 4), radius=4, fill=(70, 70, 70))
        d.rounded_rectangle((px0, py - 4, px0 + 330 * clamp(progress, 0, 1), py + 4), radius=4, fill=WHITE)
    if labels:
        for i, (k, v, col) in enumerate(labels):
            draw_spaced(d, (x1 + 60, y0 + 40 + i * 90), k, F_TINY, (150, 150, 150), 3, anchor='left')
            draw_spaced(d, (x1 + 60, y0 + 72 + i * 90), v, font(700, 30), col, 2, anchor='left')

def word_card(d, text, t, xmark=False, x_start=0.5, spread=0, c=None, f=None):
    """Measured word card: the word in a white outlined rounded rectangle, X draws in 2 frames."""
    f = f or font(700, 60)
    x, y = c or (W / 2, 435)
    tw = text_width(d, text, f, 3 + spread) + 70
    d.rounded_rectangle((x - tw / 2, y - 55, x + tw / 2, y + 55), radius=14, outline=WHITE, width=5)
    draw_spaced(d, (x, y), text, f, WHITE, 3 + spread)
    if xmark: x_mark(d, (x, y), 180, frac=draw_on(t, 2, x_start), width=16)

def counter(d, c, t, start, end, dur=2.5, label_top='', label_bottom='', t0=0.3):
    """Measured counter: cubic ease out over 2.5 s, digits ExtraBold, grey caps label above, quoted label below."""
    k = ease_out((t - t0) / dur)
    v = int(round(start + (end - start) * k))
    x, y = c
    if label_top: draw_spaced(d, (x, y - 150), label_top, F_TINY, (150, 150, 150), 5)
    draw_spaced(d, (x, y), f'{v:,}', font(800, 200), WHITE, 2)
    if label_bottom: draw_spaced(d, (x, y + 140), label_bottom, F_SMALLCAPS, (170, 170, 170), 5)

def seal_v3(d, c, scale=1.0, t=0, lines=('BUREAU OF', 'HOUSEHOLD', 'IRREGULARITIES')):
    """Our own seal (the reference seal text is not copied): double ring with sunglasses and three lines below."""
    s = scale; x, y = c
    k = ease_out(t / 0.6)
    circle(d, (x, y), 130 * s * k, outline=WHITE, width=int(6 * s))
    circle(d, (x, y), 112 * s * k, outline=WHITE, width=int(3 * s))
    if k > 0.9:
        d.rounded_rectangle((x - 60 * s, y - 14 * s, x + 60 * s, y + 14 * s), radius=8 * s, fill=WHITE)
        d.rectangle((x - 6 * s, y - 14 * s, x + 6 * s, y + 14 * s), fill=(0, 0, 0))
        draw_spaced(d, (x, y + 175 * s), '  '.join(lines), F_TINY, (160, 160, 160), 4)

def narrator_v3(d, c, t, dog_head=False, red_eyes=False, tongue=False, scale=1.0):
    """Bust of the narrator (measured 250 px wide at 720p). dog_head swaps the head for the dog shield with the
    same sunglasses; red_eyes adds pupils behind the lenses; tongue adds the red tab at the collar."""
    s = scale; x, y = c
    d.polygon([(x - 190 * s, y), (x - 160 * s, y - 120 * s), (x - 60 * s, y - 165 * s), (x + 60 * s, y - 165 * s), (x + 160 * s, y - 120 * s), (x + 190 * s, y)], fill=WHITE)
    d.polygon([(x - 50 * s, y - 165 * s), (x + 50 * s, y - 165 * s), (x, y - 90 * s)], fill=(0, 0, 0))
    d.polygon([(x - 12 * s, y - 150 * s), (x + 12 * s, y - 150 * s), (x + 8 * s, y - 40 * s), (x - 8 * s, y - 40 * s)], fill=(0, 0, 0))
    if tongue: d.rounded_rectangle((x - 12 * s, y - 185 * s, x + 12 * s, y - 150 * s), radius=8 * s, fill=(236, 70, 90))
    hy = y - 250 * s
    if dog_head: dog_face(d, (x, hy + 30 * s), 0.62 * s, red=False, black_eyes=False)
    else: d.ellipse((x - 82 * s, hy - 82 * s, x + 82 * s, hy + 82 * s), fill=WHITE)
    d.rounded_rectangle((x - 60 * s, hy - 16 * s, x + 60 * s, hy + 14 * s), radius=10 * s, fill=(0, 0, 0))
    d.rectangle((x - 6 * s, hy - 16 * s, x + 6 * s, hy + 14 * s), fill=WHITE)
    if red_eyes:
        for sgn in (-1, 1): d.ellipse((x + sgn * 33 * s - 9 * s, hy - 9 * s, x + sgn * 33 * s + 9 * s, hy + 9 * s), fill=RED)

def big_word(d, word, t, t0=0.0, sub=None, sub_after=3.0):
    """Measured big word: 216 px Black centered at y 437, pops from 1.41x in 2 frames, grey sub line after 3 s."""
    k = 1.0 + 0.41 * (1 - ease_out((t - t0) / 0.07))
    f = font(900, int(216 * k))
    draw_spaced(d, (W / 2, 437), word, f, WHITE, 6)
    if sub and t - t0 > sub_after: draw_spaced(d, (W / 2, 560), sub, F_TINY, (120, 120, 120), 5)
