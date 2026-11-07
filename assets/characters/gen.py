#!/usr/bin/env python3
"""
Reusable 2D analog-horror character asset pack.

One shared rig. Head, torso, arms and legs are the SAME primitives in every pose;
only joint rotations (and, for the dog, the head type) change. Limbs are two-segment
FK chains so a parent rotation swings the whole limb and a child rotation bends it.

Every body part is a named <g> with an id and a data-pivot="x,y" attribute. Each
rotatable group's transform is "translate(pivot) rotate(DEG)"; animate by editing DEG
(or set CSS transform-origin to the pivot). Palette: black, white, red, yellow only.
No gradients, no fur, no 3D.
"""
import os, math

W, H = 800, 1000
CX = 400
BLACK = "#000000"
WHITE = "#FFFFFF"
RED = "#F81C28"
YELLOW = "#F9DE75"

# ---- shared proportions (identical for human and dog) ----
NECK = (CX, 250)          # head pivot
TORSO = dict(x=-46, y=0, w=92, h=300, rx=46)   # drawn at translate(NECK)
SHO_L, SHO_R = (CX - 42, 282), (CX + 42, 282)   # shoulder pivots
HIP_L, HIP_R = (CX - 20, 545), (CX + 20, 545)   # hip pivots
UP_ARM = dict(hw=15, len=135)     # upper arm
FOREARM = dict(hw=14, len=120)
THIGH = dict(hw=18, len=160)
SHIN = dict(hw=16, len=155)

def rot(gid, pivot, deg, inner, pivot_attr=True):
    """Rotatable group. The joint is translated to the pivot, then an inner group rotates about it.
    To animate: change the rotate() on <g id="{gid}-joint">, or in CSS rotate that group (its origin
    is already the pivot, 0 0 in its own frame). data-pivot is the pivot in page coordinates."""
    px, py = pivot
    pa = f' data-pivot="{px:.0f},{py:.0f}"' if pivot_attr else ''
    return (f'<g id="{gid}"{pa} transform="translate({px:.1f},{py:.1f})">'
            f'<g id="{gid}-joint" transform="rotate({deg:.1f})">{inner}</g></g>')

def pill(hw, length, fill=WHITE):
    """A rounded capsule whose JOINT is at local (0,0), extending down +y."""
    return f'<rect x="{-hw}" y="{-hw}" width="{2*hw}" height="{length+hw}" rx="{hw}" ry="{hw}" fill="{fill}"/>'

def arm(side, sho_deg, elbow_deg):
    piv = SHO_L if side == 'L' else SHO_R
    fore = rot(f'forearm-{side}', (0, UP_ARM['len']), elbow_deg,
               pill(FOREARM['hw'], FOREARM['len']))
    # the forearm pivot is local to the upper-arm group; express its page pivot via translate inside
    inner = pill(UP_ARM['hw'], UP_ARM['len']) + \
            f'<g id="arm-{side}-lower" data-pivot="0,{UP_ARM["len"]}" transform="translate(0,{UP_ARM["len"]}) rotate({elbow_deg:.1f})">' + \
            pill(FOREARM['hw'], FOREARM['len']) + '</g>'
    return rot(f'arm-{side}', piv, sho_deg, inner)

def leg(side, hip_deg, knee_deg):
    piv = HIP_L if side == 'L' else HIP_R
    inner = pill(THIGH['hw'], THIGH['len']) + \
            f'<g id="shin-{side}" data-pivot="0,{THIGH["len"]}" transform="translate(0,{THIGH["len"]}) rotate({knee_deg:.1f})">' + \
            pill(SHIN['hw'], SHIN['len']) + \
            f'<ellipse id="foot-{side}" cx="10" cy="{SHIN["len"]}" rx="26" ry="14" fill="{WHITE}"/>' + '</g>'
    return rot(f'leg-{side}', piv, hip_deg, inner)

def torso():
    t = TORSO
    return (f'<g id="torso" data-pivot="{NECK[0]},{NECK[1]}" transform="translate({NECK[0]},{NECK[1]})">'
            f'<rect x="{t["x"]}" y="{t["y"]}" width="{t["w"]}" height="{t["h"]}" rx="{t["rx"]}" ry="{t["rx"]}" fill="{WHITE}"/></g>')

# ---------- heads ----------
def human_head(deg=0, closed=False):
    eye = (f'<line id="eye" x1="14" y1="-70" x2="34" y2="-70" stroke="{BLACK}" stroke-width="7" stroke-linecap="round"/>'
           if not closed else
           f'<line id="eye" x1="14" y1="-68" x2="34" y2="-68" stroke="{BLACK}" stroke-width="5" stroke-linecap="round"/>')
    inner = f'<circle id="skull" cx="0" cy="-70" r="70" fill="{WHITE}"/>' + eye
    return rot('head', NECK, deg, f'<g id="face">{inner}</g>')

def dog_head_profile(deg=0, red=False, closed=False):
    eyecol = RED if red else BLACK
    ears = (f'<polygon id="ear-L" points="-50,-120 -18,-150 -20,-70" fill="{WHITE}"/>'
            f'<polygon id="ear-R" points="18,-150 50,-120 46,-70" fill="{WHITE}"/>')
    skull = f'<circle id="skull" cx="0" cy="-70" r="58" fill="{WHITE}"/>'
    snout = f'<g id="snout" data-pivot="40,-62"><rect x="40" y="-82" width="78" height="42" rx="18" fill="{WHITE}"/></g>'
    if red:
        eye = f'<circle id="eye" cx="22" cy="-80" r="9" fill="{RED}"/>'
    elif closed:
        eye = f'<line id="eye" x1="12" y1="-80" x2="32" y2="-80" stroke="{BLACK}" stroke-width="5" stroke-linecap="round"/>'
    else:
        eye = f'<circle id="eye" cx="22" cy="-80" r="7" fill="{BLACK}"/>'
    inner = ears + snout + skull + eye
    return rot('head', NECK, deg, f'<g id="face">{inner}</g>')

def dog_head_front(deg=0, red=True, smile=False):
    eyecol = RED if red else BLACK
    ears = (f'<polygon id="ear-L" points="-58,-118 -30,-150 -14,-96" fill="{WHITE}"/>'
            f'<polygon id="ear-R" points="14,-96 30,-150 58,-118" fill="{WHITE}"/>')
    skull = f'<circle id="skull" cx="0" cy="-72" r="64" fill="{WHITE}"/>'
    snout = f'<g id="snout" data-pivot="0,-40"><ellipse cx="0" cy="-40" rx="30" ry="24" fill="{WHITE}"/><ellipse cx="0" cy="-48" rx="10" ry="7" fill="{BLACK}"/></g>'
    eyes = (f'<circle id="eye-L" cx="-26" cy="-88" r="10" fill="{eyecol}"/>'
            f'<circle id="eye-R" cx="26" cy="-88" r="10" fill="{eyecol}"/>')
    if smile:
        # wide unnatural grin: a red band of teeth, pivot at the jaw so it can animate
        mouth = (f'<g id="mouth" data-pivot="0,-28" transform="translate(0,-28) rotate(0)" style="transform-origin:0px -28px">'
                 f'<path d="M -62 -6 Q 0 70 62 -6 Q 0 26 -62 -6 Z" fill="{RED}"/>'
                 + ''.join(f'<rect x="{-50+i*20}" y="-2" width="13" height="22" fill="{WHITE}"/>' for i in range(6))
                 + '</g>')
    else:
        mouth = (f'<g id="mouth" data-pivot="0,-28" transform="translate(0,-28) rotate(0)" style="transform-origin:0px -28px">'
                 f'<line x1="-26" y1="-4" x2="26" y2="-4" stroke="{BLACK}" stroke-width="6" stroke-linecap="round"/></g>')
    inner = ears + skull + snout + eyes + mouth
    return rot('head', NECK, deg, f'<g id="face">{inner}</g>')

def tail(deg=0):
    piv = (CX - 46, 450)
    inner = (f'<path d="M 0 0 Q -70 40 -135 -40 Q -60 0 0 -30 Z" fill="{WHITE}"/>')
    return rot('tail', piv, deg, inner)

def stool():
    return (f'<g id="stool">'
            f'<rect x="{CX-60}" y="690" width="170" height="26" rx="8" fill="{WHITE}"/>'
            f'<rect x="{CX-54}" y="716" width="22" height="150" rx="6" fill="{WHITE}"/>'
            f'<rect x="{CX+84}" y="716" width="22" height="150" rx="6" fill="{WHITE}"/></g>')

def you_marker():
    return (f'<g id="you-marker" data-pivot="{CX},90">'
            f'<text x="{CX}" y="70" text-anchor="middle" font-family="Montserrat, Arial, sans-serif" '
            f'font-weight="800" font-size="34" letter-spacing="4" fill="{YELLOW}">YOU</text>'
            f'<polygon points="{CX-14},88 {CX+14},88 {CX},112" fill="{YELLOW}"/></g>')

def ground():
    return f'<line id="ground" x1="150" y1="865" x2="650" y2="865" stroke="{WHITE}" stroke-width="4" opacity="0.5"/>'

def bed():
    return (f'<g id="bed">'
            f'<rect x="120" y="560" width="620" height="90" rx="18" fill="{WHITE}"/>'
            f'<rect x="80" y="440" width="46" height="210" rx="10" fill="{WHITE}"/>'      # headboard
            f'<rect x="150" y="520" width="150" height="46" rx="18" fill="{BLACK}" stroke="{WHITE}" stroke-width="5"/>'  # pillow
            f'</g>')

# ---------- assembly ----------
def svg(title, body, bg=True):
    bgrect = f'<rect id="bg" x="0" y="0" width="{W}" height="{H}" fill="{BLACK}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n'
            f'<title>{title}</title>\n'
            f'<!-- Palette: black {BLACK}, white {WHITE}, red {RED}, yellow {YELLOW}. '
            f'Rotatable groups carry data-pivot and transform="translate(pivot) rotate(DEG)"; animate DEG. -->\n'
            f'{bgrect}\n{body}\n</svg>\n')

def human(pose, angles, head_closed=False, extra_pre='', extra_post='', whole=None):
    a = angles
    parts = []
    parts.append(tail(0)) if False else None
    parts += [
        leg('L', a['hipL'], a['kneeL']),
        leg('R', a['hipR'], a['kneeR']),
        torso(),
        arm('L', a['shoL'], a['elbL']),
        arm('R', a['shoR'], a['elbR']),
        human_head(a.get('head', 0), closed=head_closed),
    ]
    inner = extra_pre + '\n'.join(parts) + extra_post
    if whole:
        inner = f'<g id="character" transform="{whole}">{inner}</g>'
    else:
        inner = f'<g id="character">{inner}</g>'
    return inner

def dog(pose, angles, head='profile', red=True, smile=False, closed=False, extra_pre='', extra_post='', whole=None):
    a = angles
    if head == 'front':
        hd = dog_head_front(a.get('head', 0), red=red, smile=smile)
    else:
        hd = dog_head_profile(a.get('head', 0), red=red, closed=closed)
    parts = [
        tail(a.get('tail', 0)),
        leg('L', a['hipL'], a['kneeL']),
        leg('R', a['hipR'], a['kneeR']),
        torso(),
        arm('L', a['shoL'], a['elbL']),
        arm('R', a['shoR'], a['elbR']),
        hd,
    ]
    inner = extra_pre + '\n'.join(parts) + extra_post
    inner = f'<g id="character" transform="{whole}">{inner}</g>' if whole else f'<g id="character">{inner}</g>'
    return inner

# neutral hanging pose
NEUTRAL = dict(shoL=15, elbL=4, shoR=-15, elbR=-4, hipL=4, kneeL=-2, hipR=-4, kneeR=2, head=0, tail=0)

def A(**kw):
    d = dict(NEUTRAL); d.update(kw); return d

assets = {}

# 1 Human standing
assets['01_human_standing'] = svg('Human standing',
    ground() + human('standing', A(shoL=15, shoR=-15), extra_post=you_marker()))

# 2 Human sitting (side read: thighs forward to horizontal, shins down)
assets['02_human_sitting'] = svg('Human sitting',
    ground() + stool() + human('sitting', A(hipL=-86, kneeL=86, hipR=-86, kneeR=86, shoL=20, elbL=12, shoR=-20, elbR=-12),
                                whole='translate(0,150)'))

# 3 Human sleeping (whole figure horizontal on a bed, eyes closed)
assets['03_human_sleeping'] = svg('Human sleeping',
    bed() + human('sleeping', A(shoL=12, shoR=-12, hipL=5, hipR=-5), head_closed=True,
                  whole=f'translate(-168,352) rotate(-90 {CX} 250)'))

# 4 Human walking (mid stride)
assets['04_human_walking'] = svg('Human walking',
    ground() + human('walking', A(hipL=17, kneeL=0, hipR=-17, kneeR=0, shoL=-13, elbL=5, shoR=13, elbR=-5), whole='translate(0,4)'))

# 5 Upright dog standing on two legs
assets['05_dog_standing'] = svg('Upright dog standing',
    ground() + dog('standing', A(shoL=16, elbL=8, shoR=-16, elbR=8, tail=-18), head='profile', red=True))

# 6 Upright dog sitting
assets['06_dog_sitting'] = svg('Upright dog sitting',
    ground() + stool() + dog('sitting', A(hipL=-86, kneeL=86, hipR=-86, kneeR=86, shoL=20, elbL=12, shoR=-20, elbR=-12, tail=-20),
                   head='profile', red=True, whole='translate(0,150)'))

# 7 Upright dog walking
assets['07_dog_walking'] = svg('Upright dog walking',
    ground() + dog('walking', A(hipL=17, kneeL=0, hipR=-17, kneeR=0, shoL=-13, elbL=5, shoR=13, elbR=-5, tail=-34),
                   head='profile', red=True, whole='translate(0,4)'))

# 8 Upright dog lying in bed (like a person)
assets['08_dog_lying_bed'] = svg('Upright dog lying in bed',
    bed() + dog('lying', A(shoL=12, shoR=-12, hipL=5, hipR=-5, tail=-8), head='profile', red=True, closed=False,
                whole=f'translate(-168,352) rotate(-90 {CX} 250)'))

# 9 Upright dog facing camera
assets['09_dog_facing'] = svg('Upright dog facing camera',
    ground() + dog('facing', A(shoL=12, shoR=-12, tail=0), head='front', red=True, smile=False))

# 10 Upright dog with unnatural smile
assets['10_dog_smile'] = svg('Upright dog unnatural smile',
    ground() + dog('smile', A(shoL=12, shoR=-12, tail=0), head='front', red=True, smile=True))

os.makedirs('out', exist_ok=True)
for name, s in assets.items():
    open(f'out/{name}.svg', 'w').write(s)
print('wrote', len(assets), 'svgs:', ', '.join(assets))
