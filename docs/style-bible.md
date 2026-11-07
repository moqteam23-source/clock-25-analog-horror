<!-- CANONICAL for the primary Python/Pillow/FFmpeg production pipeline (30 fps).
     The Remotion starter under src/ uses 24 fps and a slightly different red/yellow;
     see docs/remotion-compatibility.md for the mapping. Production palette is
     black #000000, white #FFFFFF, red #F81C28, yellow #F9DE75. -->

# PRODUCTION STYLE BIBLE: minimalist 2D analog-horror rules tape

A strict art-direction spec for recreating this visual language on any new story. It defines the look, not the plot. Learn the motion and the system; never copy a specific brand, seal text, logo, character face or sentence. Numbers are given at the delivery resolution 1920x1080, 30 fps. Where a value was measured at the 1280x720 source, the 1080p figure is 1.5x that.

Core idea in one line: a government archive tape left running. Black field, one white pictogram, one line of caption, one red or yellow accent, wrapped in CRT grain. The horror is stillness and repetition, not gore.

---

## 1. Color palette (exact)

Use these and nothing else. No gradients anywhere except the single lamp cone in rule 4.

| Role | Hex | RGB | Where it is allowed |
|---|---|---|---|
| Background | `#000000` | 0,0,0 | the whole field, always |
| Figure / object / text white | `#FFFFFF` | 255,255,255 | figures, icons, captions, card titles |
| Danger red | `#F81C28` | 248,28,40 | X marks, threat eyes, DON'T labels, timers, the abnormal event only |
| Rule-line red | `#E60C2F` | 230,12,47 | the wipe line under a RULE title and the current progress dash |
| Highlight yellow | `#F9DE75` | 249,222,117 | the YOU marker, keys, one highlighted prop. Never for danger |
| Check green | `#56ED72` | 86,237,114 | check marks only, nothing else |
| Lamp cone | `#FFC85A` at 42% over black | 255,200,90 | only a physical light source (open fridge, bulb), drawn behind figures |
| Bulb glow | `#FDFD75` | 253,253,117 | the hot center of a light source |
| HUD grey | `#303030` | 48,48,48 | the top overlay text and empty rule boxes |
| Dark object fill | `#0C0C0C` | 12,12,12 | the near-black inside of a phone, door, TV, fridge |

Rules:
- Black is true black but never literally flat: a 1 to 3 level grain floor sits on it so it reads as tape, not a PNG.
- Red means abnormal. If nothing is wrong on screen, there is no red.
- Yellow is a spotlight, not decoration. One yellow element per frame at most.
- Green appears only on a check mark and never anywhere else.

---

## 2. Typography

One family only: a bold condensed-feeling geometric sans. Montserrat is the reference (weights 500, 600, 700, 800, 900). Everything on screen is UPPERCASE except nothing. There is no lowercase and no second typeface.

| Element | Weight | Cap height / size at 1080p | Tracking | Position |
|---|---|---|---|---|
| Caption (bottom band) | SemiBold 600 | 53 px font | +3 | centered, baseline block at y 902 |
| Caption, 2 lines max | SemiBold 600 | 53 px, line pitch 60 | +3 | block stays centered on y 902 |
| HUD file label + timecode | Medium 500 | 17 px | +3 | top left x 97 / top right x -97, y 82 |
| RULE title word | ExtraBold 800 | 157 px font | +12 | card center, y 430 |
| Rule number in box | ExtraBold 800 | 112 px | 0 | white rounded square beside the title |
| Rule subtitle (typed) | Bold 700 | 69 px font | +4 | y 636, types at 25 ms per character |
| On-object label pill | Bold 700 | 26 px | +2 | pill, see section 4 |
| Small grey label under an icon | SemiBold 600 | 18 px | +4 | grey `#303030`, under the icon |
| Big word card | Black 900 | 216 px, auto-shrink and wrap to fit 1720 px | +6 | centered y 437 |

Rules:
- Caption lines break near the middle so the two lines are balanced, never widow-one-word.
- Caption never sits over the pictogram. If the art is low, the art moves up, not the text.
- The RULE title does not slide. It fades in over 6 frames. The subtitle types left to right with no cursor at 25 ms per character (about 40 characters per second).
- Minimum type size on screen is 32 px. The only thing allowed smaller is the HUD.

---

## 3. Character construction

Figures are flat white silhouettes built from a few primitives. No faces beyond a single eye dash. No mouth. No fingers. No feet detail.

Human ("YOU"):
- Round head, radius about 63 px at 1080p, one short horizontal dash for the eye, no mouth, no nose.
- Body is one rounded-pill torso about 57 px wide, two straight pill arms, two straight pill legs.
- Stroke weight for any outline is 11 px. Bodies are solid white fills, not outlines.
- The viewer surrogate carries a yellow "YOU" word and a small down triangle above the head.

Narrator:
- The same human with black sunglasses (a black bar with two lenses) and a thin black tie. This is the only figure with eyewear.

Animal / threat (the thing that is wrong):
- Built from the same primitives as the human so the wrongness reads as posture, not detail.
- Wrong = it stands upright like a person, arms hanging at human shoulder height, drawn at human height beside the human.
- The eye becomes a solid red dot only at the story beat it is revealed, never from the first frame.
- A threat face close-up is a flat shield head with two round eyes, a nose dot, and a teeth band (a dark rectangle with white tooth gaps) that appears instantly then widens a few px. Red eyes replace the black eyes. No shading, no texture, no fur.

Gray worker (institutional figure, if the story needs one):
- A mid-gray `#969696` featureless standing figure, no face at all, optionally holding a clipboard or reaching with one gloved forearm.

Rules:
- Every figure is readable as a black-and-white pictogram at thumbnail size.
- Recognition between characters comes from one silhouette cue only (a hat band, a bun, sunglasses, ears), never from facial detail.
- No two figures share the frame center. The human is left of center, the threat right of center.

---

## 4. Background and icons

Background:
- Pure black with a faint vignette (about a 10 percent corner falloff, no more) and the grain floor.
- A thin floor line in grey under figures when they stand in a room. No walls, no furniture unless the beat needs one named object.

Objects (one named object per shot):
- Phones, doors, TVs, fridges are drawn as white outlines with a near-black `#0C0C0C` fill.
- Beds, lamps, keys, animals are solid white silhouettes.
- A light source (open fridge, bulb, phone screen) gets the lamp cone or a soft radial glow, drawn behind the figures so a figure inside the light stays pure white, not tinted.

Icons and markers:
- The eye icon is two white arcs with a central disc (red disc when it is the threat watching).
- Label pills: a filled rounded rectangle, yellow for a neutral highlight with black text, red for a danger label with white text. They pop in over about 4 frames with a slight overshoot.
- Progress dashes and the seven numbered boxes are the only repeating UI. Everything else is a single icon.
- Draw order every frame: background object first, then characters, then labels, bubbles and markers last, so nothing is hidden behind a shape.

Forbidden in this layer: colorful app UI, realistic product renders, photographs except a deliberate archival black-and-white insert with a white frame and heavy grain.

---

## 5. Animation

The governing rule: nothing is a screensaver. Figures hold still during a beat. Life comes from cuts, one deliberate move per shot, the camera, and the film layer, not from idle wiggling.

Idle (default):
- Figures are still. Breathing, blinking and head sway are OFF by default. If a client insists, keep breathing under 1 px and never on the threat.
- A tail wags as two damped swings (about 30 degrees, 1.6 Hz) then stops. It does not loop.
- A light source glow may pulse gently. A clock or timer may tick. Nothing else moves during a hold.

The one move per shot:
- Each shot gets a single deliberate action that finishes in the first 0.3 to 1.0 s, then the shot holds dead still until the cut.
- Easing is ease-out for entrances and draw-ons (0.6 to 1.2 s), with a 10 percent overshoot only on a label pop.
- Examples: an element slides or rises in from one side; a hand or forearm rotates to a target; a red X draws on stroke by stroke in 2 frames; a dotted sight line draws from an eye to its target in about 10 frames and the target eye turns red the frame it arrives; a progress bar fills; a figure walks out with a simple leg swing; a counter runs up with a cubic ease-out over 2.5 s.
- Stand-up (animal rising onto two legs): the body rotates 0 to 90 degrees about the hips over 10 frames, ease-out, head kept level, then holds.

Walk:
- A step every 0.5 s, head bob about 4 px, arms counter-swing. For a walk in place the figure does not travel. For a menacing approach the figure translates at about 100 px per second, slow, not a slide.

Puppet discipline:
- Joints are implied, not drawn. Limbs are rigid pills that pivot. No squash and stretch, no secondary jiggle, no easing softer than ease-out. The motion should feel stiff and deliberate, like a cutout puppet moved by hand.

---

## 6. Camera and composition

Compositions are static and centered. The camera is a slow instrument.

- Base framing: the stage sits in the middle third, floor line near the lower third, caption band below it. The whole stage is drawn about 20 percent larger than feels natural (a 1.2 base zoom) so pictograms read big.
- Push: during a hold the frame may push in 0 to 4 percent with ease-in and ease-out after a 0.5 s delay. That is the only continuous camera move.
- Reframing one built scene: build the scene once, then cut between named framings (wide, medium, medium-left, medium-right, close, face) by cropping and scaling to a target center. Dialogue alternates medium-left and medium-right like shot-reverse-shot. A scare goes close, then a tighter face.
- Cut rhythm: a new shot every 2 to 4 seconds. One caption equals one shot.
- No handheld drift, no dolly, no rotation, no tilt. The camera never moves except the slow push.
- Negative space is the composition. One subject, centered or on a third, surrounded by black.

---

## 7. Glitch and VHS layer

Every frame carries a light film layer; cuts carry a heavy glitch.

At rest, on every frame:
- Chromatic bleed: red channel shifted about 1.5 px left, blue about 1.5 px right.
- Grain: temporal noise of 1 to 3 levels, lifting true black so it reads as tape. A few bright dust specks per second in any region.
- Scanlines: a barely-there horizontal texture at about 1.5 percent opacity, or none. They must not be an obvious stripe pattern.
- Vignette: about 10 percent at the corners.

At a cut (the glitch), about 5 frames in a heavy, heavy, heavy, light, light pattern:
- RGB split jumps to 10 to 27 px on heavy frames, 6 to 10 px on light frames.
- 6 or more horizontal slices, 15 to 100 px tall, shifted sideways up to 120 px.
- 30 to 80 thin white streaks scattered over the frame.
- The main shapes echoed 2 or 3 times horizontally at about 30 to 40 percent.
- The frame scaled about 1.03 on heavy frames.
- The glitch straddles the cut: 1 to 2 frames before, 3 to 4 after.

Also use a 3 to 5 frame glitch hit on a caption change inside a held scene, even when the picture does not cut. About 80 percent of cuts carry a glitch; the rest are hard cuts into quiet inserts.

Reserved transitions:
- Black flash only before the final word card: black 3 frames, 1 frame of picture, black 12 frames, then the word.
- A reveal that changes a character (a head swap, eyes turning on) happens inside a glitch so the change itself is never seen cleanly.

---

## 8. Audio

No music. The narration track carries its own bed; the build adds effects only.

- Effects sit about 20 to 28 dB under the voice. Final mix is normalized to loudnorm I=-16, TP=-1.5, LRA=11.
- Cue map: a static burst on every glitch cut; a low thud on every rule card; a soft click per typed subtitle character; a tick on each of the seven boxes and on a clock; a pop on every label or bubble; a scratch as an X draws; a whoosh on an entering element; a deep hit on the big word card; a breath only where the script mentions breathing. Add object sounds (a lock, a door, keys, footsteps) only for the named object in that shot.
- Tone is dry and close, like foley on a tape, not cinematic sound design. No reverb tails, no risers, no musical stings.
- Silence is allowed and useful. A held shot with only room tone is scarier than one filled with sound.

---

## 9. Forbidden elements

- No color beyond the palette in section 1. No teal, no orange grade, no pastel.
- No gradients except the single lamp cone. No drop shadows, no bevels, no glows except a light source.
- No 3D, no perspective, no realistic rendering, no photographic texture on a character.
- No faces beyond one eye dash. No mouths on normal characters, no fingers, no detailed monster, no gore.
- No modern app UI, no rounded colorful buttons, no emoji, no sticker, no meme text.
- No second typeface, no lowercase, no italic, no serif.
- No handheld camera, no zoom blur, no lens flare, no particle effects, no bokeh.
- No idle breathing or swaying as constant motion. No looping tail wag.
- No music, no ambient drone added by the build, no watermark, no logo bug.
- Nothing on screen under 32 px except the HUD.
- No em dashes in any on-screen text or supporting copy. Use commas, periods or colons.
- Never reproduce a real brand, channel name, seal wording, logo, mascot or a recognizable copyrighted character. Invent your own archive name and seal text.

---

## 10. Quality-control checklist

Run this against the contact sheet (one frame every 5 s, tiled) and the final file before delivery.

Color and type:
- [ ] Only palette colors appear. Red is present only where something is abnormal.
- [ ] At most one yellow element per frame. Green appears only on check marks.
- [ ] All on-screen text is uppercase, one typeface, tracked out.
- [ ] Captions are at most 2 lines, balanced, centered on y 902, never over the pictogram.
- [ ] Nothing on screen is under 32 px except the HUD.
- [ ] No em dashes anywhere, on screen or in the description and metadata.

Figures and layout:
- [ ] Every figure reads as a flat black-and-white pictogram at thumbnail size.
- [ ] Faces carry at most one eye dash. No mouths, fingers or 3D.
- [ ] A threat reads as wrong by posture, and its eye goes red only at the reveal beat, not from frame one.
- [ ] Background is black with a floor line and at most one named object per shot. Labels sit on top, not hidden.

Motion and camera:
- [ ] Each shot has exactly one deliberate move, finished early, then a dead hold.
- [ ] No constant idle wiggle. Tails wag twice and stop.
- [ ] The only camera move is a slow push of 4 percent or less. No drift, tilt or rotation.
- [ ] Cut rhythm is one caption per shot, roughly every 2 to 4 s.

Film layer and audio:
- [ ] A light grain and chromatic bleed sit on every frame; black is never flat.
- [ ] Most cuts carry the 5 frame glitch; caption changes inside a held scene get a short glitch hit.
- [ ] Character reveals happen inside a glitch, never seen cleanly.
- [ ] No music. Effects only, about 20 to 28 dB under the voice, mix at I=-16 LUFS.
- [ ] A black flash precedes only the final word card.

Structure and delivery:
- [ ] Rule cards fade in (no slide), red line wipes, subtitle types at 25 ms per character, seven progress boxes present.
- [ ] If the story is a seven-rule tape, there are seven rule cards and the count reads 7.
- [ ] Final duration equals the voice length plus 1.5 s of black tail.
- [ ] 1920x1080, 30 fps, H.264 yuv420p, AAC. Captions spot-checked against the audio at 3 random points.
- [ ] No real brand, name, seal text, logo, mascot or copyrighted character anywhere.
