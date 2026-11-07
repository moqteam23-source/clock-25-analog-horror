"""Scene functions. Each takes (d, img, t, p): draw, image, seconds since shot start, params dict."""
import math, re
from PIL import Image, ImageDraw
from engine import *
import engine

_T = [0.0]  # seconds since shot start, set by the compositor before each scene call
def person(d, c, **kw):
    engine.person(d, c, t=_T[0], **kw)
def dog(d, c, **kw):
    kw.setdefault('wag', 'slow' if (kw.get('eyes') == RED or kw.get('pose') in ('two', 'flat')) else 'fast')
    engine.dog(d, c, t=_T[0], **kw)

CX = W // 2

def enter_x(t, frm, to, dur=0.9, delay=0.0):
    return frm + (to - frm) * ease_out((t - delay) / dur)

# ---- scenes ----
def sc_dog_two(d, img, t, p):
    """dog standing on two legs, optional person beside it"""
    floor_line(d)
    if p.get('person'):
        person(d, (CX - 300, GROUND), pose=p.get('pose', 'stand'), eyes=None)
        you_marker(d, (CX - 300, GROUND - 380), t)
    x = enter_x(t, CX + 700, CX + (260 if p.get('person') else 0)) if p.get('enter') else CX + (260 if p.get('person') else 0)
    dog(d, (x, GROUND), pose='two', eyes=RED if p.get('red') else None, smile=p.get('smile'), coat=p.get('coat'), scale=p.get('scale', 1.0))
    if p.get('label'): label_pill(d, (x, GROUND - 440), p['label'], t, color=RED if p.get('label_red') else YELLOW, textcolor=WHITE if p.get('label_red') else (0, 0, 0))
    if p.get('xmark'): x_mark(d, (x, GROUND - 200), 260, frac=(t - 0.5) / 0.4)

def sc_dog_four(d, img, t, p):
    floor_line(d)
    if p.get('person'):
        person(d, (CX - 340, GROUND), pose='stand')
    x = CX + (200 if p.get('person') else 0)
    dog(d, (x, GROUND), pose='four', eyes=RED if p.get('red') else None)
    if p.get('label'): label_pill(d, (x, GROUND - 300), p['label'], t)
    if p.get('check'): check_mark(d, (x + 280, GROUND - 200), 120)

def sc_dog_flat(d, img, t, p):
    bed(d, (CX, GROUND))
    dog(d, (CX + 120, GROUND - 60), pose='flat', eyes=RED if p.get('red') else None)
    if p.get('label'): label_pill(d, (CX, GROUND - 260), p['label'], t, color=RED, textcolor=WHITE)

def sc_person_lie(d, img, t, p):
    bed(d, (CX, GROUND))
    person(d, (CX + 120, GROUND - 60), pose='lie')
    if p.get('dog_watch'):
        x = enter_x(t, CX + 800, CX + 520, dur=1.2, delay=0.3)
        dog(d, (x, GROUND), pose='two', eyes=RED)
    if p.get('label'): label_pill(d, (CX, GROUND - 260), p['label'], t)
    if p.get('you'): you_marker(d, (CX - 120, GROUND - 200), t)

def sc_seven(d, img, t, p):
    seven_boxes(d, (CX, 470), current=p.get('current'), red=p.get('red'), redacted=p.get('redacted'), scale=1.6, t=t)

def sc_timeline(d, img, t, p):
    floor_line(d, 400, 1520)
    person(d, (CX - 380, GROUND), pose='stand')
    dog(d, (CX + 120, GROUND), pose='four')
    k = ease_out((t - 0.3) / 0.8)
    if k > 0:
        d.line((CX - 520, 380, CX - 520 + 1040 * k, 380), fill=WHITE, width=6)
        if k > 0.95:
            draw_spaced(d, (CX, 330), '30,000 YEARS', F_CARD, YELLOW, 4)
    if p.get('eye'):
        eye(d, (CX + 120, 380), scale=0.5, red=True, look=(30 * math.sin(t), 0))

def sc_eye(d, img, t, p):
    k = ease_out(t / 0.5)
    look = (40 * math.sin(t * 0.9), 10 * math.sin(t * 1.7))
    eye(d, (CX, 470), scale=1.6 * max(k, 0.01), red=p.get('red', True), closed=p.get('closed') or blink(t, 3.0), look=look)
    if p.get('xmark'): x_mark(d, (CX, 470), 420, frac=(t - 0.5) / 0.4)
    if p.get('label'): label_pill(d, (CX, 720), p['label'], t, color=RED, textcolor=WHITE)

def sc_fridge(d, img, t, p):
    floor_line(d)
    fridge(d, (CX + 260, GROUND), open_=p.get('open'))
    if p.get('dog_two'):
        dog(d, (CX - 120, GROUND), pose='two', eyes=RED if p.get('red') else None)
    elif p.get('dog'):
        dog(d, (CX - 160, GROUND), pose='four')
    if p.get('label'): label_pill(d, (CX - 120, GROUND - 440), p['label'], t)

def sc_keys(d, img, t, p):
    k = ease_out(t / 0.5)
    keys(d, (CX, 470), scale=1.8 * max(k, 0.01), color=YELLOW if p.get('yellow') else WHITE)
    if p.get('label'): label_pill(d, (CX, 720), p['label'], t)

def sc_tv(d, img, t, p):
    floor_line(d)
    tv(d, (CX + 320, GROUND))
    chair(d, (CX - 260, GROUND))
    person(d, (CX - 300, GROUND), pose='sit')
    if p.get('dog'):
        x = enter_x(t, CX + 900, CX + 40, dur=1.2) if p.get('enter') else CX + 40
        dog(d, (x, GROUND), pose='two', eyes=RED)
    if p.get('label'): label_pill(d, (CX - 300, GROUND - 360), p['label'], t)

def sc_table(d, img, t, p):
    floor_line(d)
    table(d, (CX + 120, GROUND))
    chair(d, (CX - 300, GROUND))
    person(d, (CX - 340, GROUND), pose='sit')
    if p.get('dog'):
        dog(d, (CX + 420, GROUND), pose='two', eyes=RED)
    if p.get('label'): label_pill(d, (CX - 340, GROUND - 360), p['label'], t)

def sc_stand_mirror(d, img, t, p):
    """person and dog standing the same way, dog copying"""
    floor_line(d)
    person(d, (CX - 260, GROUND), pose=p.get('pose', 'stand'))
    you_marker(d, (CX - 260, GROUND - 380), t, start=0.3)
    dog(d, (CX + 260, GROUND), pose='two', eyes=RED, smile=p.get('smile'))
    if p.get('arrow'):
        dashed_line(d, (CX - 170, 420), (CX + 170, 420), fill=RED, frac=ease_out((t - 0.4) / 0.6))
    if p.get('label'): label_pill(d, (CX + 260, GROUND - 440), p['label'], t, color=RED, textcolor=WHITE)
    if p.get('xmark'): x_mark(d, (CX + 260, GROUND - 200), 260, frac=(t - 0.5) / 0.4)

def sc_bubble(d, img, t, p):
    """speech bubble with a word, optional X. Background object first, bubble on top."""
    if p.get('dog'):
        floor_line(d)
        dog(d, (CX, GROUND), pose='two', eyes=RED)
    elif p.get('door'):
        floor_line(d)
        door(d, (CX, GROUND), handle_color=RED if p.get('red_handle') else WHITE)
    k = overshoot(t / 0.3)
    txt = p.get('word', '...')
    by = 290
    if k > 0.05:
        speech_bubble(d, (CX, by), txt, scale=1.0, color=WHITE if not p.get('red') else RED, textcolor=(0, 0, 0) if not p.get('red') else WHITE)
    if p.get('xmark'): x_mark(d, (CX, by), 260, frac=(t - 0.6) / 0.4)

def sc_phone(d, img, t, p):
    k = ease_out(t / 0.5)
    phone(d, (CX, 470), scale=1.0, camera=p.get('camera'), progress=p.get('progress'), play=p.get('play'))
    if p.get('xmark'): x_mark(d, (CX, 470), 420, frac=(t - 0.6) / 0.4)
    if p.get('label'): label_pill(d, (CX, 760), p['label'], t, color=RED if p.get('label_red') else YELLOW, textcolor=WHITE if p.get('label_red') else (0, 0, 0))

def sc_person_phone(d, img, t, p):
    floor_line(d)
    person(d, (CX - 280, GROUND), pose='phone')
    dog(d, (CX + 300, GROUND), pose='two', eyes=RED)
    if p.get('xmark'): x_mark(d, (CX - 190, GROUND - 320), 160, frac=(t - 0.6) / 0.4)
    if p.get('label'): label_pill(d, (CX + 300, GROUND - 440), p['label'], t, color=RED, textcolor=WHITE)

def sc_casefile(d, img, t, p):
    k = ease_out(t / 0.4)
    bx, by = CX, 450
    w, h = 900 * k, 300 * k
    d.rounded_rectangle((bx - w / 2, by - h / 2, bx + w / 2, by + h / 2), radius=10, outline=WHITE, width=5)
    if k > 0.95:
        draw_spaced(d, (bx, by - 90), 'ARCHIVE  //  CASE FILE', F_CARDSMALL, GREY, 5)
        draw_spaced(d, (bx, by - 10), p.get('title', 'CASE FILE 41'), F_CARD, WHITE, 4)
        draw_spaced(d, (bx, by + 70), p.get('sub', 'OHIO'), F_CARDSMALL, RED, 6)

def sc_door(d, img, t, p):
    floor_line(d)
    if p.get('bedroom'):
        # measured bedroom set: window with moon top left, bed with the person at left, solid white door, dog at right
        rrect(d, (CX - 760, 200, CX - 600, 400), 6, fill=(12, 12, 12), outline=WHITE, width=8)
        d.line((CX - 680, 200, CX - 680, 400), fill=WHITE, width=8); d.line((CX - 760, 300, CX - 600, 300), fill=WHITE, width=8)
        d.pieslice((CX - 660, 240, CX - 620, 280), 20, 320, fill=YELLOW)
        bed(d, (CX - 560, GROUND), scale=0.7); engine.person(d, (CX - 480, GROUND - 40), pose='lie', scale=0.7, t=t)
    if p.get('person') and not p.get('bedroom'):
        person(d, (CX - 330, GROUND), pose=p.get('pose', 'stand'), arm='up' if p.get('reach') else None)
    if p.get('solid', p.get('bedroom')):
        d.rounded_rectangle((CX + 10, GROUND - 380, CX + 230, GROUND), radius=10, fill=WHITE)
        circle(d, (CX + 190, GROUND - 190), 10, fill=RED if p.get('red_handle') else (0, 0, 0), outline=RED if p.get('red_handle') else (0, 0, 0))
        if p.get('lock'): rrect(d, (CX + 176, GROUND - 250, CX + 204, GROUND - 225), 4, fill=RED, outline=RED, width=2)
    else:
        door(d, (CX + 120, GROUND), lock=p.get('lock'), handle_color=RED if p.get('red_handle') else WHITE)
    if p.get('handle_move'):
        k = 0.5 + 0.5 * math.sin(t * 9)
        circle(d, (CX + 190, GROUND - 190 + 12 * k), 14, fill=RED, outline=RED)
    if p.get('dog_behind'):
        dog(d, (CX + 520, GROUND), pose='two', eyes=RED)
    if p.get('xmark'): x_mark(d, (CX + 120, GROUND - 190), 240, frac=(t - 0.6) / 0.4)
    if p.get('label'): label_pill(d, (CX + 120, GROUND - 430), p['label'], t, color=RED if p.get('label_red') else YELLOW, textcolor=WHITE if p.get('label_red') else (0, 0, 0))
    if p.get('check'): check_mark(d, (CX + 120, GROUND - 190), 160)

def sc_wall_ear(d, img, t, p):
    wall(d, CX, 200, 800)
    person(d, (CX - 320, GROUND), pose='lie') if p.get('lie') else None
    k = ease_out(t / 0.5)
    ear(d, (CX + 90, 480), scale=1.4 * max(k, 0.01), red=True)
    dog(d, (CX + 420, GROUND), pose='two', eyes=RED)
    if p.get('label'): label_pill(d, (CX + 420, GROUND - 440), p['label'], t, color=RED, textcolor=WHITE)

def sc_wave(d, img, t, p):
    waveform(d, (CX, 470), t, scale=2.0, broken=p.get('broken'), color=RED if p.get('broken') else YELLOW)
    if p.get('label'): label_pill(d, (CX, 720), p['label'], t, color=RED if p.get('broken') else YELLOW, textcolor=WHITE if p.get('broken') else (0, 0, 0))

def sc_doorbell(d, img, t, p):
    doorbell(d, (CX, 470), scale=1.8, ringing=p.get('ring'), t=t)
    if p.get('label'): label_pill(d, (CX, 760), p['label'], t)

def sc_narrator(d, img, t, p):
    floor_line(d)
    person(d, (CX, GROUND), pose='stand', sunglasses=True)
    if p.get('seal'): seal(d, (CX + 420, 420), scale=0.9, t=t)
    if p.get('label'): label_pill(d, (CX, GROUND - 400), p['label'], t, color=RED if p.get('label_red') else YELLOW, textcolor=WHITE if p.get('label_red') else (0, 0, 0))
    if p.get('ears'):
        # dog ears appear on the narrator
        k = ease_out((t - 0.8) / 0.4)
        if k > 0:
            hx, hy = CX, GROUND - 292
            d.polygon([(hx - 40, hy - 30), (hx - 10, hy - 40), (hx - 38, hy - 30 - 65 * k)], fill=WHITE)
            d.polygon([(hx + 10, hy - 40), (hx + 36, hy - 30), (hx + 34, hy - 30 - 65 * k)], fill=WHITE)

def sc_dog_bed(d, img, t, p):
    bed(d, (CX, GROUND))
    dog(d, (CX + 160, GROUND - 60), pose='four', scale=0.8)
    if p.get('label'): label_pill(d, (CX, GROUND - 300), p['label'], t)
    if p.get('check'): check_mark(d, (CX + 360, GROUND - 240), 120)

def sc_circle_dog(d, img, t, p):
    """dog turning in a circle: dog rotates position around a point"""
    floor_line(d)
    a = t * 2.2
    dog(d, (CX + 60 * math.cos(a), GROUND), pose='four', scale=0.9)
    circle(d, (CX, GROUND - 40), 180, outline=(70, 70, 70), width=4)
    if p.get('label'): label_pill(d, (CX, GROUND - 330), p['label'], t)

def sc_clock(d, img, t, p):
    clock(d, (CX, 470), scale=1.3, hour=p.get('hour', 3), t=t)
    if p.get('label'): label_pill(d, (CX, 720), p['label'], t)

def sc_walk_out(d, img, t, p):
    floor_line(d, 300, 1620)
    door(d, (CX + 500, GROUND))
    x = enter_x(t, CX - 200, CX + 250, dur=2.0)
    person(d, (x, GROUND), pose='walk' if t < 2.0 else 'stand', arm=None)
    if p.get('dog'):
        dog(d, (CX - 520, GROUND), pose='two', eyes=RED)
    if p.get('label'): label_pill(d, (x, GROUND - 400), p['label'], t)

def sc_blank(d, img, t, p):
    pass

SCENES = {k[3:]: v for k, v in globals().items() if k.startswith('sc_')}


# ---------- assignment for this script (keyword rules, first match wins) ----------
RULES = [
    (r'stands up on two legs', ('dog_two', {'person': True, 'enter': True, 'pose': 'stand'})),
    (r'there are seven rules', ('seven', {})),
    (r'break the third', ('seven', {'red': 3})),
    (r'need the seventh', ('seven', {'redacted': 7})),
    (r'30,000 years', ('timeline', {})),
    (r'long time to watch', ('timeline', {'eye': True})),
    (r'when you wake up', ('person_lie', {'dog_watch': True})),
    (r'where the food', ('fridge', {'dog': True})),
    (r'which pocket has the keys', ('keys', {'yellow': True})),
    (r'do nothing with this information', ('dog_four', {'person': True})),
    (r'rule one', ('tv', {'dog': True, 'label': 'ACT NORMAL'})),
    (r'keep doing it', ('tv', {'dog': True})),
    (r'keep eating', ('table', {'dog': True})),
    (r'keep watching', ('tv', {'dog': True})),
    (r'doing nothing at all', ('tv', {'dog': True, 'label': 'CONTINUE'})),
    (r'trained for this', ('tv', {'dog': True})),
    (r'do not stare', ('eye', {'red': False, 'xmark': True})),
    (r'not looking at you', ('stand_mirror', {})),
    (r'how you stand', ('stand_mirror', {'arrow': True})),
    (r'rule two', ('bubble', {'word': 'ITS NAME', 'xmark': True, 'dog': True})),
    (r'answer to that', ('bubble', {'word': '...', 'dog': True})),
    (r'do not say sit', ('bubble', {'word': 'SIT', 'xmark': True, 'dog': True})),
    (r'chair across from you', ('tv', {'dog': True, 'enter': True})),
    (r'the word walk', ('bubble', {'word': 'WALK', 'xmark': True, 'dog': True})),
    (r'not be saying it again', ('bubble', {'word': 'W...', 'red': True, 'dog': True})),
    (r'rule three', ('phone', {'camera': True, 'xmark': True})),
    (r'most people fail', ('seven', {'red': 3})),
    (r'want to film it', ('person_phone', {})),
    (r'hairy man', ('fridge', {'dog_two': True, 'red': True, 'label': 'SMALL HAIRY MAN'})),
    (r'very well online', ('phone', {'play': True, 'label': '2.6M VIEWS'})),
    (r'sees a camera', ('person_phone', {'label': 'LEARNING', 'xmark': True})),
    (r'being watched', ('eye', {'red': True})),
    (r'doing the watching', ('eye', {'red': True, 'label': 'ALWAYS'})),
    (r'keep it that way', ('dog_two', {'red': True})),
    (r'case file', ('casefile', {'title': 'CASE FILE 41', 'sub': 'OHIO'})),
    (r'refrigerator', ('fridge', {'dog_two': True, 'open': True})),
    (r'11 seconds', ('phone', {'progress': 1.0, 'label': '0:11'})),
    (r'first four', ('phone', {'progress': 0.36, 'label': '0:04', 'label_red': True})),
    (r'started to copy you', ('stand_mirror', {'arrow': True, 'label': 'COPYING'})),
    (r'the way you stand', ('stand_mirror', {})),
    (r'the way you walk', ('stand_mirror', {'pose': 'walk'})),
    (r'then, your face', ('stand_mirror', {'smile': True})),
    (r'built to smile', ('dog_two', {'red': True, 'smile': True})),
    (r'try anyway', ('dog_two', {'red': True, 'smile': True, 'label': 'TRYING', 'label_red': True})),
    (r'do not smile back', ('stand_mirror', {'smile': True, 'xmark': True})),
    (r'checking its work', ('eye', {'red': True})),
    (r'rule four', ('person_lie', {'label': 'USUAL TIME'})),
    (r'usual time', ('clock', {'hour': 10, 'label': '10:00 PM'})),
    (r'close the bedroom door', ('door', {'person': True, 'reach': True})),
    (r'lock it', ('door', {'person': True, 'lock': True, 'check': True})),
    (r'dogs cannot open doors', ('door', {'dog_behind': True, 'check': True})),
    (r'could not open doors', ('door', {'dog_behind': True, 'red_handle': True, 'label': 'YESTERDAY', 'label_red': True})),
    (r'handle moves', ('door', {'handle_move': True, 'dog_behind': True, 'xmark': True})),
    (r'know who is there', ('door', {'dog_behind': True, 'red_handle': True})),
    (r'raincoat', ('dog_two', {'coat': True, 'red': True, 'label': 'LITTLE RAINCOAT'})),
    (r'rule five', ('wall_ear', {'lie': True})),
    (r'call your name', ('bubble', {'word': 'YOUR NAME', 'door': True})),
    (r'someone you love', ('bubble', {'word': 'YOUR NAME', 'door': True})),
    (r'sound like you', ('bubble', {'word': 'YOU', 'red': True, 'door': True})),
    (r'through the wall', ('wall_ear', {'lie': True, 'label': 'LISTENING'})),
    (r'words will be right', ('wave', {})),
    (r'spaces between them', ('wave', {'broken': True, 'label': 'WRONG'})),
    (r'do not answer', ('bubble', {'word': '...', 'xmark': True, 'door': True})),
    (r'do not open the door', ('door', {'person': True, 'lock': True, 'xmark': True})),
    (r'good boy', ('bubble', {'word': 'GOOD BOY', 'xmark': True, 'dog': True})),
    (r'knows what it is', ('dog_two', {'red': True})),
    (r'your opinion', ('dog_two', {'red': True, 'label': 'NOT INTERESTED', 'label_red': True})),
    (r'doorbell rings', ('doorbell', {'ring': True})),
    (r'unprofessional', ('narrator', {'label': 'APOLOGIES'})),
    (r'rule six', ('dog_bed', {})),
    (r'back in its bed', ('dog_bed', {'check': True})),
    (r'tail wagging', ('dog_four', {'check': True})),
    (r'most dangerous part', ('dog_bed', {'label': 'DANGER'})),
    (r'dreamed it', ('person_lie', {'label': 'A DREAM?'})),
    (r'how it is lying', ('dog_flat', {})),
    (r'turns in a circle', ('circle_dog', {})),
    (r'flat on its back', ('dog_flat', {'red': True, 'label': 'PAWS FOLDED'})),
    (r'how you sleep', ('person_lie', {'you': True})),
    (r'take your keys', ('keys', {'yellow': True})),
    (r'leave the house', ('walk_out', {'dog': True})),
    (r'do not say goodbye', ('bubble', {'word': 'GOODBYE', 'xmark': True, 'dog': True})),
    (r'goodbye means', ('dog_two', {'red': True})),
    (r'six years', ('walk_out', {'dog': True})),
    (r'came back', ('door', {'person': True, 'dog_behind': True})),
    (r'rule seven', ('narrator', {})),
    (r'need this one', ('seven', {'redacted': 7})),
    (r'how we know', ('narrator', {})),
    (r'been waiting', ('eye', {'red': True})),
    (r'government agency', ('narrator', {'seal': True})),
    (r'we walk on two legs', ('narrator', {})),
    (r'always walked on two legs', ('narrator', {'ears': True})),
    (r'calm voice', ('narrator', {'ears': True, 'label': 'DO NOT ASK', 'label_red': True})),
    (r'^we are\.', ('narrator', {'ears': True})),
    (r'always were', ('dog_two', {'red': True})),
    (r'cooperation', ('narrator', {'seal': True})),
]

def assign(text):
    low = text.lower()
    for pat, (scene, params) in RULES:
        if re.search(pat, low):
            return scene, dict(params)
    return 'dog_two', {'red': True}


# =====================================================================================
# v3 scenes, built from the measured motion library (claude/animation-bible.md)
# =====================================================================================
def _dur(p): return p.get('dur', 3.0)

def sc_dog_rise(d, img, t, p):
    """Measured stand up: four legged dog, tail wags (damped) for 1.9 s, then the body rotates 90 degrees about the
    hip in 10 frames with ease out, head stays level, then a dead hold."""
    floor_line(d)
    if p.get('person'):
        person(d, (CX - 300, GROUND), pose=p.get('pose', 'stand'))
        if p.get('you'): you_marker(d, (CX - 300, GROUND - 380), t)
    x = CX + (260 if p.get('person') else 0)
    rise_at = p.get('rise_at', 1.9)
    ang = stand_up(t, rise_at, 0.33)
    if t < rise_at:
        dog(d, (x, GROUND), pose='four', wag='fast')
    elif ang >= 89.5:
        dog(d, (x, GROUND), pose='two', eyes=RED if (p.get('red') and t > rise_at + 1.0) else None, wag='none')
    else:
        # rotate the four legged dog about its hind feet
        lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        engine.dog(ld, (x, GROUND), pose='four', t=0.0, wag='none')
        piv = (x - 110, GROUND)
        lay = lay.rotate(ang, resample=Image.BICUBIC, center=piv)
        img.alpha_composite(lay)
    if p.get('label') and t > rise_at + 0.6: label_pill(d, (x, GROUND - 440), p['label'], t, start=rise_at + 0.6)

def sc_run(d, img, t, p):
    """Measured 'do not run': static running pose plus three speed lines, door at right, X draws in 2 frames."""
    floor_line(d, 300, 1620)
    x = CX - 200
    person(d, (x, GROUND), pose='walk')  # one frozen stride frame
    for i, (ly, L) in enumerate(((-230, 90), (-190, 130), (-150, 70))):
        d.line((x - 120 - L, GROUND + ly, x - 120, GROUND + ly), fill=WHITE, width=8)
    door(d, (CX + 420, GROUND))
    if p.get('xmark', True): x_mark(d, (x, GROUND - 160), 260, frac=draw_on(t, 2, 0.5))

def sc_living_room(d, img, t, p):
    """Measured opening set: armchair with person, window with moon, clock, dog, TV. dog: four / two / none.
    sight=True draws the red dotted line from the dog's eye to the person over 8 frames."""
    floor_line(d, 300, 1620)
    paste_glow_later.append((CX - 220, 300, 110))
    rrect(d, (CX - 300, 180, CX - 140, 400), 6, fill=(12, 12, 12), outline=WHITE, width=8)
    d.line((CX - 220, 180, CX - 220, 400), fill=WHITE, width=8); d.line((CX - 300, 290, CX - 140, 290), fill=WHITE, width=8)
    d.pieslice((CX - 200, 230, CX - 160, 270), 20, 320, fill=YELLOW)
    clock(d, (CX + 200, 240), scale=0.5, hour=3, t=0)
    chair(d, (CX - 560, GROUND)); person(d, (CX - 600, GROUND), pose='sit')
    tv(d, (CX + 560, GROUND))
    dp = p.get('dog', 'four')
    if dp == 'four': dog(d, (CX + 40, GROUND), pose='four', wag=p.get('wag', 'fast'))
    elif dp == 'two': dog(d, (CX + 40, GROUND), pose='two', eyes=RED if p.get('red') else None, wag='none')
    elif dp == 'rise':
        rise_at = p.get('rise_at', 1.9); ang = stand_up(t, rise_at, 0.33)
        if t < rise_at: dog(d, (CX + 40, GROUND), pose='four', wag='fast')
        elif ang >= 89.5: dog(d, (CX + 40, GROUND), pose='two', eyes=None, wag='none')
        else:
            lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            engine.dog(ld, (CX + 40, GROUND), pose='four', t=0.0, wag='none')
            img.alpha_composite(lay.rotate(ang, resample=Image.BICUBIC, center=(CX + 40 - 110, GROUND)))
    if p.get('sight'): sight_line(d, (CX + 70, GROUND - 300), (CX - 600, GROUND - 270), t, start=0.4, frames=8, color=RED)
    if p.get('check'): 
        k = ease_out((t - 0.4) / 0.1)
        if k > 0:
            circle(d, (CX - 330, 170), 28 * k, fill=GREEN, outline=GREEN); check_mark(d, (CX - 330, 172), 30 * k, color=(0, 0, 0), width=6)
    if p.get('label'): label_pill(d, (CX + 40, GROUND - 440), p['label'], t)

def sc_rows_five(d, img, t, p):
    """Measured: five four legged dogs, pitch 360 px at 1080p; stand=True rises the fourth one and dims the others."""
    xs = [CX - 720 + i * 360 for i in range(5)]
    rise = p.get('stand', False)
    for i, x in enumerate(xs):
        if rise and i == 3:
            ang = stand_up(t, 0.3, 0.33)
            if ang >= 89.5: dog(d, (x, GROUND - 60), pose='two', scale=0.6, eyes=RED if t > 1.5 else None, wag='none')
            else:
                lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
                engine.dog(ld, (x, GROUND - 60), pose='four', scale=0.6, t=0, wag='none')
                img.alpha_composite(lay.rotate(ang, resample=Image.BICUBIC, center=(x - 66, GROUND - 60)))
        else:
            lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            engine.dog(ld, (x, GROUND - 60), pose='four', scale=0.6, t=t, wag='fast' if not rise else 'none')
            if rise:
                a = lay.split()[3].point(lambda v: int(v * 0.35)); lay.putalpha(a)
            img.alpha_composite(lay)

def sc_heads_ring(d, img, t, p):
    """Measured: six dog face shields on a ring of radius 600 px around a standing person; red eyes on cue."""
    person(d, (CX, GROUND), pose='stand')
    red = p.get('red', False)
    for i in range(6):
        a = math.radians(-90 + i * 60 + 30)
        dog_face(d, (CX + 600 * math.cos(a), 430 + 250 * math.sin(a)), 0.42, red=red and t > p.get('red_at', 0.0))

def sc_dog_face(d, img, t, p):
    """Measured face close up: shield head, teeth appear instantly on cue and morph slowly (teeth=True)."""
    dog_face(d, (CX, 430), 1.0, red=p.get('red', False), teeth=False)
    if p.get('teeth'): teeth_smile(d, (CX, 575), 1.0, t, start=p.get('teeth_at', 0.0), morph_dur=2.5)
    if p.get('xmark'): x_mark(d, (CX, 470), 420, frac=draw_on(t, 2, 0.5))

def sc_reference(d, img, t, p):
    """Measured reference card: outlined rectangle with a smiley and 'REFERENCE', dog face with red eyes and an
    'ATTEMPT' label at right."""
    bx, by = CX - 330, 440
    d.rounded_rectangle((bx - 155, by - 200, bx + 155, by + 200), radius=8, outline=WHITE, width=6)
    circle(d, (bx, by), 95, outline=WHITE, width=8); circle(d, (bx - 32, by - 25), 9, fill=WHITE); circle(d, (bx + 32, by - 25), 9, fill=WHITE)
    d.arc((bx - 55, by - 30, bx + 55, by + 55), 20, 160, fill=WHITE, width=8)
    if p.get('xmark'): x_mark(d, (bx, by), 300, frac=draw_on(t, 2, 0.5))
    draw_spaced(d, (bx, by + 250), 'REFERENCE', F_TINY, (150, 150, 150), 5)
    fx = CX + 330
    dog_face(d, (fx, by), 0.8, red=True, teeth=True, t=t)
    draw_spaced(d, (fx, by + 250), p.get('attempt', 'ATTEMPT 214'), F_TINY, (150, 150, 150), 5)

def sc_eye_line(d, img, t, p):
    """Measured: eye icon at the left third, dog at the right third, white dotted line draws eye to dog in 10 frames
    with ease out, the dog's eye turns red the frame it arrives."""
    floor_line(d, 900, 1500)
    eye(d, (CX - 420, 440), scale=0.9, red=False, look=(0, 0))
    arrive = 0.4 + 10 / 30
    dog(d, (CX + 420, GROUND), pose='two', eyes=RED if t >= arrive else None, wag='none')
    sight_line(d, (CX - 300, 440), (CX + 445, GROUND - 310), t, start=0.4, frames=10)
    if p.get('label'): label_pill(d, (CX, 760), p['label'], t, color=RED, textcolor=WHITE)

def sc_photo(d, img, t, p):
    """Exhibit insert. p: path, label, lines, tight."""
    photo_insert(img, d, p.get('path', 'photos/exhibit_a.jpg'), t, label=p.get('label', 'EXHIBIT A'), lines=tuple(p.get('lines', ('YEAR: 1897',))), tight=p.get('tight', False), seed=p.get('seed', 1))

def sc_rec(d, img, t, p):
    """Measured REC overlay with the kitchen inside at half scale; views counter or progress bar outside."""
    box = (CX - 400, 200, CX + 400, 800)
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    g = GROUND
    engine.floor_line(ld, 560, 1360)
    table(ld, (CX - 250, g), scale=0.8)
    if p.get('person'): engine.person(ld, (CX - 330, g), pose='phone', t=t, scale=0.9)
    engine.dog(ld, (CX + 120, g), pose='two', t=t, wag='none', eyes=None)
    fridge(ld, (CX + 320, g), scale=0.9, open_=p.get('open'))
    lay = lay.resize((W // 2, H // 2), Image.LANCZOS)
    img.alpha_composite(lay, (CX - 400 + 10, 200 + 30))
    rec_frame(d, box, t, timecode=p.get('tc', '00:00:02'), live=not p.get('title'), views=p.get('views'), title=p.get('title'),
              progress=p.get('progress'), labels=p.get('labels'))
    if p.get('xmark'): x_mark(d, (CX, 500), 500, frac=draw_on(t, 2, 0.5))

def sc_word_card(d, img, t, p):
    word_card(d, p.get('word', 'SIT'), t, xmark=p.get('xmark', False), spread=p.get('spread', 0))
    if p.get('marker'):
        d.line((CX - 20, 500, CX + 20, 500), fill=RED, width=6)

def sc_counter(d, img, t, p):
    counter(d, (CX, 470), t, p.get('start', 1), p.get('end', 2190), label_top=p.get('top', 'MORNINGS'), label_bottom=p.get('bottom', '"GOODBYE"'))

def sc_narrator_v3(d, img, t, p):
    """Bust narrator. dog_head / red_eyes / tongue switch on at their cue times (put a glitch hit there)."""
    narrator_v3(d, (CX, 720), t, dog_head=p.get('dog_head') and t >= p.get('swap_at', 0), red_eyes=p.get('red_eyes') and t >= p.get('red_at', 0),
                tongue=p.get('tongue') and t >= p.get('tongue_at', 0))
    if p.get('seal'): seal_v3(d, (CX + 520, 430), scale=0.8, t=t)
    if p.get('qmarks'):
        for i, (qx, qy) in enumerate(((CX - 330, 300), (CX - 200, 170), (CX + 280, 220), (CX + 360, 400))):
            k = stagger_pop(t, i, start=0.4, gap=0.3)
            if k > 0: draw_spaced(d, (qx, qy), '?', font(800, int(90 * k)), WHITE, 0)
    if p.get('label'): label_pill(d, (CX, 330), p['label'], t, color=RED if p.get('label_red') else YELLOW, textcolor=WHITE if p.get('label_red') else (0, 0, 0))

def sc_seal(d, img, t, p):
    seal_v3(d, (CX, 430), scale=1.1, t=t)

# ---- dinner table coverage (Video B system) ----
def _dinner_draw(p, t):
    gk = {'red_eyes': p.get('red_eyes', True), 'fork_lift': arm_lift(t, p['lift_at']) if p.get('lift_at') is not None else 0.0,
          'smile_corner': clamp((t - p.get('smile_at', 99)) / 2.6, 0, 1) if p.get('smile') else 0.0,
          'jaw': clamp((t - p.get('jaw_at', 99)) / 0.7, 0, 1) if p.get('jaw') else 0.0}
    mk = {'tears': p.get('tears', False)}
    who = tuple(p.get('who', ('mother', 'father', 'kid', 'grandpa')))
    def draw_fn(d, img, s):
        dinner_table(d, img, s, t, lamp=p.get('lamp', True), who=who, grandpa_kw=gk, clock=p.get('clock', True), portrait=p.get('portrait', True))
        if p.get('tears'):
            pass
    return draw_fn

def _dinner_frame(d, img, t, p, target):
    lay = camera(_dinner_draw(p, t), target, t=t, push=p.get('push', 0.04), dur=_dur(p), move_to=p.get('move_to'), move_t=p.get('move_t', (0.0, 1.9)))
    if p.get('dim'):
        a = lay.split()[3].point(lambda v: int(v * p['dim'])); lay.putalpha(a)
    img.alpha_composite(lay)

def sc_dinner_wide(d, img, t, p):
    _dinner_frame(d, img, t, p, p.get('framing', 'WIDE'))
    if p.get('freeze'): freeze_outline(d, t)
    if p.get('bubble'):
        speech_bubble_dialogue(d, (CX - 300, 190), p['bubble'], t, start=0.3, tail_to=(CX - 300, 300))

def sc_dinner_medium(d, img, t, p):
    _dinner_frame(d, img, t, p, p.get('framing', 'MEDIUM'))
    if p.get('bubble'):
        side = p.get('side', 'right')
        bx = CX + 380 if side == 'right' else CX - 380
        speech_bubble_dialogue(d, (bx, 200), p['bubble'], t, start=0.3, tail_to=(bx - 120 if side == 'right' else bx + 120, 300))
    if p.get('sight'):
        for i, frm in enumerate(((CX - 560, 330), (CX - 180, 330), (CX + 560, 300))):
            sight_line(d, frm, (CX + 150, 360), t, start=0.6 + i * 0.2, frames=9, color=RED)
    if p.get('freeze'): freeze_outline(d, t)

def sc_dinner_close(d, img, t, p):
    _dinner_frame(d, img, t, p, p.get('framing', 'CLOSE'))
    if p.get('highlight'):
        k = ease_out((t - 0.3) / 0.1)
        if k > 0: d.ellipse((CX + 60, 560, CX + 150, 700), outline=YELLOW, width=4)

def sc_dinner_face(d, img, t, p):
    """Extreme close up: a dedicated, higher detail face asset (measured: pupils 5x apart but only 3.5x wide)."""
    def draw_fn(dd, im, s):
        lamp_cone(im, dd, (-300, -100), s, on=True, reach=900)  # a corner of the cone bottom left
        dd.rounded_rectangle((-200 * s, 600 * s, 60 * s, 1200 * s), radius=60 * s, fill=WHITE)  # chair back edge
    lay = camera(draw_fn, (960, 540, 1.0), t=t, push=0.02, dur=_dur(p))
    img.alpha_composite(lay)
    hr = 330
    x, y = CX, 470
    for i in range(8):
        a = math.radians(-50 + i * 100 / 7)
        for sgn in (-1, 1):
            bx, by = x + sgn * hr * 0.92 * math.cos(a), y - hr * 0.9 * math.sin(a)
            d.polygon([(bx, by - 40), (bx, by + 40), (x + sgn * hr * 1.5 * math.cos(a), by - hr * 0.25 * math.sin(a))], fill=WHITE, outline=OUTLINE)
    d.ellipse((x - hr, y - hr, x + hr, y + hr), fill=WHITE, outline=OUTLINE, width=6)
    grandpa_face(d, (x, y), hr, t, red_eyes=p.get('red_eyes', True), smile_corner=clamp((t - p.get('smile_at', 99)) / 2.6, 0, 1) if p.get('smile') else 0,
                 jaw=clamp((t - p.get('jaw_at', 99)) / 0.7, 0, 1) if p.get('jaw') else 0, s=2.0)
    if p.get('clock'):
        k = ease_out((t - 0.3) / 0.1)
        if k > 0:
            d.rounded_rectangle((CX + 650, 180, CX + 900, 430), radius=16, outline=WHITE, width=5)
            clock(d, (CX + 775, 305), scale=0.7, hour=6, t=0)

def sc_lights_out(d, img, t, p):
    """B 5:22 recipe: lights fail in 4 frames, eye pairs light 6 frames apart, lights back after 0.6 s."""
    br, pairs = lights_fail(t, p.get('at', 0.5))
    lay = camera(_dinner_draw(dict(p, red_eyes=False), t), 'WIDE', t=t, push=0.0, dur=_dur(p))
    if br < 1.0:
        a = lay.split()[3].point(lambda v: int(v * br)); lay.putalpha(a)
    img.alpha_composite(lay)
    seats = [230, 575, 900]
    for i in range(pairs):
        x = seats[i]; hy = 692 - 230 - 54
        for sgn in (-1, 1):
            d.ellipse((x + sgn * 34 - 11, hy - 11, x + sgn * 34 + 11, hy + 11), fill=RED)

def sc_under_table(d, img, t, p):
    """Under the table: four chair legs, three pairs of feet (slippers, socks, shoes), the fourth chair empty."""
    d.rectangle((CX - 760, 150, CX + 760, 200), fill=WHITE)
    for i in range(4):
        x = CX - 600 + i * 400
        for dx in (-130, 130): d.rounded_rectangle((x + dx - 18, 200, x + dx + 18, 800), radius=12, fill=WHITE)
        if i < 3 or p.get('four'):
            for dx in (-45, 45):
                d.rounded_rectangle((x + dx - 30, 200, x + dx + 30, 700), radius=28, fill=WHITE, outline=OUTLINE, width=5)
                d.rounded_rectangle((x + dx - 40, 690, x + dx + 50, 760), radius=20, fill=WHITE, outline=OUTLINE, width=5)
        elif p.get('dashed'):
            for dx in (-45, 45): dashed_line(d, (x + dx, 200), (x + dx, 760), fill=(120, 120, 120), width=4)
    if p.get('circle'):
        k = draw_on(t, 8, 0.5)
        d.arc((CX + 450, 700, CX + 750, 790), 0, int(360 * k), fill=RED, width=6)

SCENES.update({k[3:]: v for k, v in globals().items() if k.startswith('sc_')})

# ---------- new keyword rules (checked before the old list; first match wins) ----------
RULES_V3 = [
    (r'stands up on two legs', ('living_room', {'dog': 'rise'})),
    (r'not looking at you', ('dog_two', {'scale': 1.25})),
    (r'dogs cannot open doors|could not open doors|close the bedroom door|know who is there|handle moves', ('door', {'bedroom': True, 'dog_behind': True, 'lock': False})),
    (r'do not run', ('run', {'xmark': True})),
    (r'do not scream', ('dog_two', {'person': True, 'pose': 'stand'})),
    (r'see that you noticed', ('living_room', {'dog': 'two', 'sight': True})),
    (r'thirty thousand years|30,000 years', ('photo', {'label': 'EXHIBIT A', 'lines': ('YEAR: 1897', 'DOG: ALREADY ON A CHAIR')})),
    (r'long time to watch', ('photo', {'tight': True})),
    (r'most dogs do nothing', ('rows_five', {})),
    (r'^most\.', ('rows_five', {'stand': True})),
    (r'rule one', ('living_room', {'dog': 'two', 'label': 'ACT NORMAL'})),
    (r'keep doing it|keep watching|trained for this', ('living_room', {'dog': 'two', 'check': True})),
    (r'doing nothing at all', ('living_room', {'dog': 'two', 'check': True, 'label': 'CONTINUE'})),
    (r'do not say sit', ('word_card', {'word': 'SIT', 'xmark': True})),
    (r'the word walk', ('word_card', {'word': 'WALK', 'xmark': True})),
    (r'small, hairy man|hairy man', ('rec', {'tc': '00:00:02'})),
    (r'very well online', ('rec', {'tc': '00:00:07', 'views': 2218392})),
    (r'being watched', ('eye_line', {})),
    (r'doing the watching', ('heads_ring', {'red': True, 'red_at': 1.5})),
    (r'filmed his dog', ('rec', {'title': 'CASE 041', 'person': True, 'tc': '00:00:00', 'progress': 0.0})),
    (r'eleven seconds|11 seconds', ('rec', {'title': 'CASE 041', 'person': True, 'tc': '00:00:03', 'progress': 1.0, 'labels': [('LENGTH', '00:11', WHITE)]})),
    (r'first four', ('rec', {'title': 'CASE 041', 'person': True, 'tc': '00:00:04', 'progress': 0.36, 'labels': [('LENGTH', '00:11', WHITE), ('SUBJECT IN FRAME', '00:04', RED)]})),
    (r'then, your face', ('dog_face', {})),
    (r'built to smile', ('dog_face', {'teeth': True})),
    (r'try anyway', ('dog_face', {'teeth': True, 'teeth_at': 0.0})),
    (r'do not smile back', ('reference', {'xmark': True})),
    (r'checking its work', ('reference', {})),
    (r"it's me|spaces between", ('word_card', {'word': "IT'S   ME", 'spread': 6, 'marker': True})),
    (r'good boy', ('word_card', {'word': 'GOOD BOY', 'xmark': True})),
    (r'do not say goodbye', ('word_card', {'word': 'GOODBYE', 'xmark': True})),
    (r'six years', ('counter', {'start': 1, 'end': 2190})),
    (r'wondering how we know', ('narrator_v3', {'qmarks': True})),
    (r'government agency', ('narrator_v3', {'seal': True})),
    (r'^we are\.', ('narrator_v3', {'dog_head': True, 'swap_at': 0.0, 'tongue': True, 'tongue_at': 1.1})),
    (r'always were', ('narrator_v3', {'dog_head': True, 'swap_at': 0.0, 'tongue': True, 'tongue_at': 0.0, 'red_eyes': True, 'red_at': 0.3})),
    (r'cooperation', ('seal', {})),
    (r'unprofessional|apologies', ('narrator_v3', {})),
    # dinner table (grandpa type scripts)
    (r'sits down for (family )?dinner|family dinner', ('dinner_wide', {})),
    (r'pass the salt', ('dinner_medium', {'framing': 'MED_RIGHT', 'lift_at': 0.3})),
    (r'whole table stops', ('dinner_wide', {'freeze': True})),
    (r'turns to look', ('dinner_medium', {'framing': 'MEDIUM', 'sight': True, 'freeze': True})),
    (r'not blinked', ('dinner_face', {'clock': True})),
    (r'smile will go up', ('dinner_face', {'smile': True, 'smile_at': 0.3})),
    (r'jaw is not attached', ('dinner_close', {'highlight': True})),
    (r'hangs a little lower', ('dinner_face', {'jaw': True, 'jaw_at': 0.4})),
    (r'there are three of them', ('lights_out', {'at': 0.5})),
    (r'under the table|look under', ('under_table', {'dashed': True})),
    (r'how was your day', ('dinner_medium', {'framing': 'MED_LEFT', 'bubble': 'How was your day, Dad?', 'side': 'left'})),
    (r'"?quiet,?"? he says|he says', ('dinner_medium', {'framing': 'MED_RIGHT', 'bubble': 'Quiet.', 'side': 'right'})),
    (r'laugh', ('dinner_medium', {'framing': 'MED_LEFT', 'bubble': 'HA HA HA', 'side': 'left', 'tears': True})),
    (r'grandpa|grandfather', ('dinner_medium', {'framing': 'MED_RIGHT'})),
]
_assign_v2 = assign
def assign(text):
    low = text.lower()
    for pat, (scene, params) in RULES_V3:
        if re.search(pat, low):
            return scene, dict(params)
    return _assign_v2(text)
