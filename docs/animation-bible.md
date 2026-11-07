# ANIMATION BIBLE: rules horror motion system, measured from two reference videos

Written for the video making chat. Read this before every render, together with `claude/rules-horror-master-prompt-v3.md`. Every number below was measured on extracted frames at 1280x720 (the source resolution) unless marked "estimate" or "not measured". Our engine renders at 1920x1080: multiply 720p numbers by 1.5. Where this file disagrees with the master prompt, this file wins, because the prompt was written from memory and this was measured.

Sources: Video A = "If Your Dog Ever Stands On Two Legs" (272.8 s, 30 fps, 1280x720). Video B = "If Your Dead Grandpa Comes To Dinner" (501.0 s, 30 fps, 1280x720). Our render = `Dog_Two_Legs_v2_animated_sfx.mp4` (274.3 s, 1920x1080), same script as Video A.

Method: ffmpeg scene detection (`gt(scene,0.08)`, cuts closer than 0.5 s merged), a whole video pass at 640x360 (per frame luminance, stage motion energy, caption band change, RGB channel shift), targeted 30 fps bursts, pixel bounding boxes and blob centroids in named regions, FFT of the resulting signals.

## 0. The one thing to understand first

Nothing idles. In Video A the standing dog is pixel identical for 44 consecutive frames (white count 19307 on every frame, bounding box fixed). The seated person in the opening is pixel identical for 70 frames (count 2375). In Video B all four figures, the lamp and the bulb are constant for 72 frames in the wide shot (bulb luminance 202 on every frame). 45.8 percent of all Video A frames have zero stage motion; in Video B it is 10 percent, and that 10 percent is only because B pushes the camera in slowly during holds.

The feeling of life comes from four other things, in this order of importance:
1. Cut rhythm: a new shot every 2 to 4 seconds, and a glitch hit on almost every caption change even when the picture does not change.
2. One deliberate move per shot, finished in the first 0.3 to 1.0 s, then a dead hold.
3. Camera: B reframes the same scene at 4 sizes and pushes in slowly during holds. A uses jump cuts to a 1.3x tighter framing.
4. Film layer: 2 px RGB split at rest, temporal grain of 1 to 3 levels on black, a few bright dust specks per second, heavy grain on photographs.

So the master prompt's "every figure breathes, blinks, sways, tails wag all the time" is not what the reference does. Keep breathing and blink available as options, but default them OFF, and spend the effort on cuts, glitch hits, entrances and camera instead. A still figure after a good entrance reads as tension; a bobbing figure reads as a screensaver.

## 1. Rhythm

| | Video A | Video B | Our render |
|---|---|---|---|
| Duration | 272.8 s | 501.0 s | 274.3 s |
| Detected shots | 62 | 188 | 97 (one per caption) |
| Cuts per minute | 13.4 | 22.4 | 21 |
| Mean / median shot | 4.40 s / 3.57 s | 2.66 s / 2.23 s | 2.8 s / 2.7 s |
| Longest hold | 18.9 s (bedroom sequence, captions changing inside it) | 14.6 s (under the table) | 5 s |
| Shots under 2 s | 14 of 62 | 71 of 188 | 17 of 97 |
| Caption band changes | 134 (97 captions plus re-triggers at cuts) | 226 | 93 |
| Median caption hold | 1.93 s | 2.10 s | 2.67 s |
| Glitch events per minute | 19.4 | 21.2 | 10.1 |
| Cuts carried by a glitch | 50 of 61 (82%) | 162 of 187 (87%) | 46 of 96 |
| Hard cuts (no glitch) | 11 | 25 | 50 |
| Glitch hits on a caption change with no cut | 31 | 11 | 0 |
| Glitch hits mid shot, nothing else changing | 4 | 3 | 0 |
| Black flashes | only in the ending (3 + 1 + 12 frames before the big word) | only the last 4 frames | 4 (we add one before "there are seven rules") |
| Frames with zero stage motion | 45.8% | 10.0% | 14.5% (our grain hides stillness) |

How motion is distributed inside a shot (Video A, per shot motion energy): the move happens in the first 10 to 30 frames, then the shot is flat until the cut. Shots with continuous motion are the exceptions and each is a specific device: the walk cycle (1:58), the counter (3:38), the camera push on the TV (4:08), a photograph with live grain (0:20).

Rule for us: one caption = one shot is fine, but add a glitch hit (3 to 5 frames) on every caption change that is not a cut, and allow a scene to hold across 2 to 4 captions with only the caption and a small element changing (A does this for the living room, the bedroom and the REC frame).

## 2. Idle life rules (what actually moves during a hold)

Measured as "nothing" unless listed:
- Breathing, head sway, blink: 0 px in both videos (70 frame and 44 frame holds pixel identical). Our engine's 2.5 px bob at 0.4 Hz and 120 ms blink every 3.3 s are our invention. Default them off. If a client asks for them, keep amplitude at 1 px or less at 1080p and never on the threat figure.
- Tail wag (A, four legged dog, 0:00 to 0:02): one damped wag, not a loop. Tail tip top edge 312 to 336 to 312 px over 19 frames (0.63 s, 1.6 Hz), second swing 312 to 323 to 320, then still from frame 42. Amplitude 24 px vertical at the tip of an 85 px tail, about 30 degrees. In the "copying" shots the standing dog's tail hangs and does not move.
- Ear flick: not observed (0 px on the two legged dog over 44 frames).
- Lamp and bulb (B): bulb luminance 202 constant over 44 frames, no flicker. The cone region fluctuates plus or minus 1.5 percent per frame, which is the film grain, not a flicker.
- Clock: the living room clock in A is static (count 1192 constant). B's inset clocks are static. Our sweeping second hand is an invention; harmless, keep it only on clock inserts.
- Steam (B, roast at 2:16 and 5:34): three wavy lines above the dish. Present, animation not measured (the shot is 1.6 s).
- Knee bounce (B 3:48): white area oscillates plus or minus 0.5 percent at about 3 Hz, a few px, on one leg only.
- Camera push during a hold (B): the hallway dog grows 5 percent over 2.5 s (top edge 368 to 351, left edge 696 to 660), under the table 2.5 percent over 2.8 s. Ease in, ease out, starts after a 0.5 s delay. This is the only "always moving" thing in B.
- Film layer (both): RGB split 1 px each way at 720p at rest (R left, B right, so 1.5 px each at 1080p); background grain temporal std 2.2 to 3.1 levels in A, 1.0 in B, on a floor of 1 to 3 (not 0); 1 to 3 bright specks (up to 75 to 144 of 255) per second in any 60x100 px dark block; photographs carry temporal std 20.

So the engine's default idle should be: figure still, film layer on, optional slow push (1.0 to 1.05 over the shot, ease in and out), and nothing else.

## 3. Motion library (measured examples)

Frames are at 30 fps. Px at 1280x720.

| Motion type | Example (video, time) | What moves | Frames | Easing | Amplitude px | Loop or one shot | Notes |
|---|---|---|---|---|---|---|---|
| Stand up (dog) | A 1.97 to 2.27 | whole dog body rotates 0 to 90 deg about the hip; head counter rotates to stay level; front legs become hanging arms | 10 | ease out: about 15, 20, 20, 15, 10, 5, 3, 2, 1, 0 deg per frame | pivot at hind feet, body 185 px long | one shot | tail wags during the 1.9 s before it |
| Tail wag | A 0.37 to 1.0 | tail tip | 19 then 11 | sine, damped | 24 px vertical | 2 swings then still | see section 2 |
| Walk in place | A 118.0 to 119.5 | legs and arms, head bob | step every 15 frames, full cycle 30 | smooth | head bob 4 px p2p at 2.0 Hz; stride about 60 px on a 290 px figure | loop | person and dog cycle in sync, no travel, short ground line under each |
| Walk with travel | A 221.5 to 224.5 | figure translates right | 90 | linear | 83 px per s, step period 16 frames | loop | leading edge wobbles 10 px with each step |
| Walk in from edge | A 140.0 to 142.5 | two legged dog enters from the right and stops at the door | about 75 | linear | about 100 px per s | one shot | slow, menacing; not an ease out slide |
| Run | A 5.9 to 7.0 | nothing | 0 | none | 0 | static | a running pose icon plus three speed lines; the X draws over it |
| Pea roll | B 120.3 to 123.6 | pea on the table top | 100 | near linear (estimate) | about 800 px in 3.3 s | one shot | estimate from a 10 fps burst, blob tracking failed on the grain |
| Fork to mouth | B 94.2 to 94.7 | forearm rotates about the elbow, fork tip ends at the mouth | 15 | ease out | about 70 deg | one shot | hold 1.2 s at the mouth, no chewing |
| Salt pour | B 134.0 to 135.6 | 3 to 5 grain dots fall each frame | 48 | linear | about 20 px per frame | loop while held | shaker tilted about 45 deg, static |
| Napkin drop | B 217.3 to 218.0 | napkin falls and rotates | 21 | accelerating | about 250 px, 90 deg | one shot | cut to under the table with a 2 frame glitch |
| Jaw hang | B 183.8 to 184.5 | lower mouth shape | about 20 | linear | a few px | one shot | preceded by a yellow outline ellipse highlighting the hinge for 1.7 s |
| Smile too far | B 164.5 to 167.1 | right mouth corner extends upward toward the eye | 78 | linear | about 60 px at the close framing | one shot | the other corner stays |
| Mouth morph "tries to smile" | A 123.0 to 124.3 | mouth outline | about 40 | linear | 750 px squared of area | one shot | subtle; the teeth appear instantly at the cut 1.6 s earlier |
| Dotted sight line (white) | A 93.13 to 93.47 | line from the eye icon to the dog's eye | 10 | ease out (40, 25, 15, 10, 10 percent per 2 frames) | 600 px | one shot | the dog's eye turns red the frame the line arrives |
| Dotted sight line (red) | A 8.73 to 9.0 | line from the dog's eye to the seated person | 8 | near linear | 460 px, dots 3 px, gap 5 px | one shot | drawn from the watcher toward the watched |
| Sight lines, group | B 70.9 to 71.5 | three red dotted lines from three heads to the speaker | 9 each, start 6 frames apart | ease out | 150 to 300 px | one shot | this is how "everyone turns to look" is done; no head rotates |
| X mark | A 6.15 to 6.22 | two red strokes | 1 + 1 | none | 160 px X, stroke about 8 px | one shot | the second X (seven boxes, 12.4) is drawn inside a glitch burst |
| Check mark | A 38.0 | green circle with check pops top left of the window | about 3 (estimate) | ease out | 50 px | one shot | not frame measured |
| Freeze outline | B 63.6 to 72.2 | white dashed rounded rectangle inset 20 px from the frame edge | 0 (instant) | none | dash 20, gap 10, stroke 4 | holds across 4 shots (8.6 s) | the picture inside keeps cutting |
| Label pop | A 229.17, 229.47, 229.77 | three question marks around the narrator | 4 each, 9 frames apart | ease out, no overshoot (52, 92, 97, 100 percent) | 40 px glyphs | one shot | stagger is the trick, not the bounce |
| Dialogue bubble | B 41.5 | bubble scales in above the speaker | 2 to 3 | ease out | 300 x 73 px bubble | one shot, holds 1.7 s | mixed case text, see section 6 |
| Thought bubble | A 196.0, B 285 | cloud with an icon inside | about 3 (estimate) | ease out | 160 px | one shot | |
| Card fade in | A 34.56 to 34.73 | whole "RULE 1" block | 6 | linear opacity 25 to 100 percent | 0 px (no slide) | one shot | preceded by 5 black frames with faint streaks |
| Red line wipe | A 34.66 to 34.73 | line under the title grows left to right | 3 | ease out | 440 px | one shot | starts on frame 3 of the fade |
| Typewriter | A 34.76 to 35.0, B 18.8 to 19.3 | subtitle characters | about 1.3 chars per frame | linear | 10 chars in 7 frames; 21 chars in 15 frames | one shot | 24 to 25 ms per character, no cursor |
| Counter | A 218.2 to 220.7 | number 1 to 2,190 | 75 | cubic ease out (26, 295, 540, 764, 966, 1148, 1311, 1457, 1585, 1697, 1795, 1878, 1949, 2008, 2057, 2096, 2126, 2150, 2166, 2177, 2184, 2188, 2189, 2190 at 0.1 s steps) | 110 px tall digits | one shot | label above and below static |
| Seven boxes fly to HUD | B 17.7 to 18.3 | the big boxes tumble up and right and shrink into the HUD row | 18 | ease in | from 56 px boxes at y 140 to 21 px boxes at y 56 | one shot | each box rotates about 30 deg on the way |
| Push in (continuous) | B 16.6 to 18.5 | whole scene scales about a target | 57 | ease in, ease out (lamp edge steps 1, 1, 2, 2, 4, 5, 7, 9, 11, 13, 17, 21 px per frame on the way in) | zoom 1.0 to 1.47 | one shot | wide to medium framing |
| Push in (hold) | B 446.4 to 449.0 | whole scene | 78 | ease in, ease out, 15 frame delay | zoom 1.0 to 1.05 | one shot | the idle substitute |
| Jump cut zoom | A 46.2, A 17.0, A 20.5 | framing jumps tighter in one frame | 1 | none | photo 603 to 792 px wide (1.31x) | one shot | A never pushes continuously |
| Scene dim | A 54.8 to 55.1 | everything fades to black before a card | 8 | linear | luminance 41 to 3 | one shot | then 12 black frames with streaks, then the card fades in |
| Lights fail | B 322.2 to 322.5 | whole scene | 4 | bright, dim, dimmer, bright, black | | one shot | then eye pairs light at 322.5, 322.7, 322.9 (6 frames apart); lights back 323.1 to 323.2 |
| Head swap | A 256.0 to 256.2 | round head replaced by a dog head with the same sunglasses | inside a 5 frame glitch | none | | one shot | the audience never sees the change itself |
| Eyes turn red (narrator) | A 257.7 to 257.9 | pupils appear behind the sunglasses | inside a 5 frame glitch | none | 10 px dots | one shot | preceded 0.3 s earlier by a red tongue popping in |
| Big word pop | A 260.8, B 490.0 | STAY. / SCROLL. | 2 | scale 1.41 to 1.0 | word 410 x 101 px | one shot | the small "NEXT FILE" line appears 2.8 to 3.4 s later |
| Card exit (rule 7) | A 228.47 to 228.57 | whole card slides up and scales up out of frame | 3 | ease in | about 200 px | one shot | other cards exit by glitch cut |
| Glitch, cut | A every cut | RGB split, slice shifts, streak field, echo | median 5 (1 to 13) | heavy, heavy, heavy, light, light, heavy, heavy, light, light, light | split 7 to 18 px heavy, 4 to 7 light; slices 10 to 70 px tall shifted up to 80 px | per cut | see section 7 |
| Glitch, micro | B every cut | same, smaller | median 2 (1 to 4) | | split 3 to 6 px | per cut | one frame before the cut, one or two after |
| Photo grain | A 17 to 23 | grain over the photograph only | continuous | random | temporal std 20 levels | loop | vector content has std 0 |

Not found in either video: an arm raise to a light switch, a figure stepping into the light, a rotating head turn, a rigged run cycle, a glow pulse, a drifting stage.

## 4. Camera coverage system (Video B)

B builds one dinner table scene and frames it at least 6 ways. 116 of the 188 shots (287 s of 501) are this scene.

Framings, measured on the distance between grandpa's two pupils (33 px in the wide, the ruler for zoom) and his pupil midpoint:

| Code | What is in frame | Shots | Mean length | Zoom vs wide | Where the camera centers (wide coordinates, 1280x720) | Grandpa pupil midpoint in frame |
|---|---|---|---|---|---|---|
| W wide | whole table, lamp, 4 figures, clock inset left, portrait right | 38 | 2.63 s | 1.0 | (640, 360) | (806, 288) |
| M medium | 3 figures, lamp top left | 14 | 2.56 s | 1.47 to 1.66 | (726, 334) | (777, 280) |
| ML medium left | mother, father, kid | 13 | 2.73 s | about 1.9 | about (330, 335) estimate | |
| MR medium right | kid and grandpa | 29 | 2.50 s | 1.93 to 1.98 | (807, 361) | (639, 219) |
| C close | grandpa, shoulders up, kid's shoulder at the edge | 11 | 1.68 s | 2.3 | (806, 335) | (640, 252) |
| XC extreme close | grandpa face fills 450 px | 11 | 2.25 s | 3.3 to 5.0 | (806, 295) | (636, 326) |
| T table top | plates, hands, props, from the diner's eye line | 15 | 2.51 s | separate drawing | | |
| U under table | legs, slippers, socks, chair legs | 10 | 3.78 s | separate drawing | | |
| H hallway | door, coat rack, the dog | 6 | 2.66 s | separate drawing | | |
| I inserts | phone, clock, photos, case file, calendar, floor plan, CCTV grid | 37 | 2.79 s | | | |

The extreme close up is not a pure zoom: in the XC the pupils are 165 px apart but each pupil is only 63 px wide (ratio 2.6), while in the wide they are 33 apart and 18 wide (ratio 1.8). The face at XC is a separately drawn, higher detail asset (teeth with gaps, eye highlights, 8 hair spikes). M, MR and C are consistent with the same drawing scaled.

Cutting order (116 table shots, 77 adjacent pairs): tighter 27, wider 21, same size 29. Most common pairs: W to W 10 (same size, a small reframe or a new element), W to M 7, M to W 7, MR to MR 6, W to MR 5, MR to W 5, W to C 4, C to XC 3, MR to XC 3. Scares go C to XC or MR to XC. Dialogue alternates ML and MR like shot reverse shot. Example runs: `W > MR > ML > MR > ML` (dinner conversation), `C > XC > C > XC > MR` (the smile), `MR > C > XC > XC` (the jaw), `W > W > M > W > W > M > W > C > C > M` (the laugh).

Lighting per size:
- Bulb glow: (253, 253, 117), about #FDFD75, an ellipse under the white dome, constant.
- Cone: a triangle from the bulb with a 45 degree half angle (edges move 1 px sideways per 1 px down, measured on 12 rows), apex width equal to the bulb (163 px), color over black (108, 84, 37), which is #FFC85A at 42 percent opacity. Drawn BEHIND the figures and the table: a figure inside the cone is pure (255, 255, 255), not tinted. The cone reaches the table top and is clipped by it.
- Table: a white slab whose top surface fades from 255 in the middle to about 150 at the left end over 400 px (measured row y 515: 149, 163, 181, 201, 217, 236, 252, 255). Chairs are plain white pills, two per figure, behind the shoulders.
- Background: 1 to 3, no visible vignette at any size.
- At M and C the cone appears as a diagonal band of the same color crossing behind the heads. At XC a corner of it is still visible bottom left. Under a rule card the cone switches off (cone pixel 92 to 15) and the whole scene drops to 65 percent (white 207 to 136).

Recipe for the engine (implemented as `camera()` in engine.py):
1. Draw the whole scene once on a canvas 3x the frame size at wide scale, lamp cone first, then table, chairs, figures, props, then labels.
2. A framing is `(center_x, center_y, zoom)` in wide coordinates. Crop `W/zoom x H/zoom` around the center and resize to the frame. The engine's named targets (engine.FRAMINGS) are WIDE (960, 500, 1.0), MEDIUM (1089, 553, 1.5), MED_LEFT (495, 568, 1.6), MED_RIGHT (1210, 568, 1.6), CLOSE (1209, 574, 1.9), FACE (1209, 372, 3.5) at 1080p. These zooms are smaller than the pupil based zooms in the table above because the reference redraws the face wider at closer framings; the body based numbers put the table top at 0.76 of the frame height, as in the reference, so the caption never lands on the white table.
3. For a slow push, interpolate zoom by 3 to 5 percent over the shot with ease in and out and a 0.5 s delay. For a cut, pick the next framing from the table above. For a continuous push (used once per 90 s in B), interpolate center and zoom over 1.9 s with ease in and out.
4. Dialogue: ML for the family line, MR for the reply, hold 1.5 to 2.5 s each.
5. Scare: MR or C, then XC with the detailed face, hold 2 to 3 s, cut back to MR.

## 5. Rig specs

Measured sizes at 1280x720; our engine draws at 1920x1080 under a 1.2 base zoom, so multiply by about 1.25 to match on screen.

Video A, person "you": ISO pictogram style, no face at all. Round head radius 15 to 22 px, 6 px gap to the body, torso a 46 px wide rounded slab with two arms drawn as attached pills with a 2 px inner stroke, two legs. Standing height 200 to 290 px depending on the shot. Parts that ever move: legs and arms (walk cycle), one arm (phone up, arms up for "do not scream"). Seated in the armchair (190 px tall group), lying in bed (head left).

Video A, dog on four legs: 185 x 155 px, solid white, pointed ears, snout right, tail up at 135 degrees, 85 px long. Parts that move: tail (wag), whole body (the stand up rotation).

Video A, dog on two legs (the wrong one): 320 px tall when alone, 200 px beside a person. Head up, snout horizontal, ears up, body leaning 5 degrees forward, arms hanging with an inner outline stroke OR both arms extended forward at shoulder height (copying, reaching for a handle), tail hanging. One eye dot; it is red when the dog is watching. In measurable terms the wrongness is: upright torso, arms at human positions, the dog is drawn at the same height as the person next to it, and the eye becomes red only at the narrative moment (never from the first frame).

Video A, dog face: shield shape 210 x 260 px, flat top with two triangular ears, rounded bottom, two black round eyes 16 px, black nose 16 px lower. Teeth: a dark band 80 x 20 px with 5 white rectangles. Red eyes are 16 px red disks replacing the black ones.

Video A, narrator: bust 250 px wide, round head radius 55, black sunglasses bar 70 x 18 with two lenses, white collar V, black tie 12 px wide. Full body version for "we walk on two legs" with a ground line. The twist swaps the head for a dog head with the same sunglasses, then adds a red tongue, then red pupils.

Video B, family (white fill, black outline 3 to 4 px, so 5 to 6 px at 1080p):
- Head circle radius 60 in the wide (mother, father, grandpa), 50 for the kid.
- Mother: a bun (circle radius 18) at the top left of the head plus a curved hair band across the head.
- Father: a flat cap: a band across the forehead and a short brim to the right.
- Kid: smaller head, three triangular hair spikes on top and a cap band.
- You: seen from behind in ML shots, plain head with a hair line, no face.
- Body: rounded shoulders 150 px wide, arms in a U on the table ending in mitten hands, a fork held upright in one hand. Chair backs: two white pills 24 x 160 px behind the shoulders.
- Nobody has a face except grandpa. Recognition comes only from the hat or hair shape, so each must be readable at 30 px.

Video B, grandpa (the wrong one), measurable: 6 to 8 triangular hair spikes radiating from the sides of the head; two eyes that are dark sockets (radius 18 at wide, 63 at XC) with red (233, 37, 48) fill and a small white highlight; a wide mouth with 6 to 8 white rectangular teeth in a black band; a pointed collar and a napkin triangle; the eyes never blink (2.8 s hold measured at 0 change); the body never moves except the fork arm; the smile corner can rise 60 px; the jaw outline can drop a few px. Everyone else is drawn with the same body, which is the point.

Video B, dog: the four legged A dog, seated facing a wall in the hallway cone.

## 6. Text and card choreography

Caption (both videos identical):
- Montserrat SemiBold or Bold, all caps, cap height 25 px at 720p (38 at 1080p), which is a 53 px font at 1080p. Our render uses 40 px: 25 percent too small. Tracking about 2 px (3 at 1080p).
- Block vertical center y = 601.5 of 720 (902 of 1080). One line: cap top 589. Two lines: cap tops 569 and 609 (line pitch 40 px, 60 at 1080p), the block stays centered on the same y. Lines break near the middle of the sentence (balanced), max width about 650 px (975 at 1080p).
- Appears with a 5 frame fade (56, 76, 87, 95, 99 percent). Changes 1 frame after the cut. Before a rule card it fades out with the scene over 8 frames.
- Dim state: under a card in A the caption fades in with the card. In our render the caption is instant: add the 5 frame fade.

HUD: text cap height 8 px at 720p (12 at 1080p, a 17 px Montserrat Medium), color (48, 48, 48), file label at x 65 and y 55 (97, 82 at 1080p), timecode right aligned at x 1215. Seven boxes 21 x 23 px, pitch 23.5 px, centered, current one filled (151, 142, 138) with a dark number, others outlined (41, 41, 41). In A the boxes do not exist in the HUD until the first rule card. Ours: brighter (90), bigger pitch (40 at 1080p vs 35), 26 px higher on the frame.

Rule card, Video A (full black card):
- Frame 0 to 4: black with a faint white streak field (3 of the 5 frames).
- Frame 5 to 10: "RULE" plus the number box fade in together from 25 to 100 percent, no slide, no pop. "RULE" in Montserrat ExtraBold, cap height 73 px (110 at 1080p, about a 157 px font), tracking 12 px, centered as a block with the box. Number box 130 px square (195 at 1080p), radius 14, white, number ExtraBold cap 75 px, black. Block vertical center y 287 (430 at 1080p).
- Frame 8 to 10: red line (230, 12, 47) wipes left to right, 440 x 6 px at y 381 (660 x 9 at y 572).
- Frame 10 onward: subtitle types at 25 ms per character, Montserrat Bold cap height 32 px (48 at 1080p, a 69 px font), tracking 6, y 424 (636), no cursor.
- Mini boxes: 7 squares 38 px (57 at 1080p), pitch 47 (70), y 507 (760); current white with a black number; others outline (72, 71, 76) with numbers (63, 64, 67).
- Hold until 2.24 s, exit by glitch cut (rule 7 exits by a 3 frame slide up and scale up).
- Rule 7 first card: a grey (90, 90, 90) bar 520 x 36 px where the subtitle would be; the HUD box 7 shows a bar too. Rule 4 and rule 7 cards fade in slower (about 15 frames) with the caption dim.
- Before every card the previous scene fades to black in 8 frames and the black holds 12 frames.

Rule card, Video B (corner overlay): the scene stays, dimmed to 65 percent with the lamp cone off; "RULE 1" with its box top left at about x 60, y 90, cap height about 36 px (estimate); red line 2 px; subtitle 16 px types at 24 ms per character; 3.2 s; the big seven boxes in the scene fly into the HUD 0.7 s before the card.

Big word card: Montserrat Black, cap height 101 px at 720p (152 at 1080p, a 216 px font), centered at y 292 (437 at 1080p), appears with a 2 frame scale down from 1.41 to 1.0; after 2.8 to 3.4 s a grey 12 px caps line "NEXT FILE: 042" appears 60 px below it; held 8 to 11 s to the end; black 3 + 1 + 12 frames before it. B adds a 40 px scroll icon above the word.

Counter card: digits Montserrat ExtraBold cap height about 95 to 110 px, centered; grey 10 px caps label above ("MORNINGS" at y 232) and a quoted 12 px label below (y 405); count with cubic ease out over 2.5 s.

Dialogue bubble (B): white fill, black 3 px outline (5 at 1080p), radius 12, about 300 x 73 px for 13 characters, text Montserrat SemiBold mixed case, cap height about 20 px (30 at 1080p), a 20 px triangular tail toward the speaker's mouth, placed above the head between y 60 and y 140, pops in over 2 to 3 frames, holds 1.5 to 2.0 s, disappears at the cut. "HA HA HA" in caps. The grandpa's bubble sits to his right.

Word card (A): a bare word ("SIT", "WALK", "IT'S ME", "GOOD BOY", "GOODBYE", "WHO'S A GOOD BOY?") in a white outlined rounded rectangle, Montserrat Bold about 40 px, centered at y 290; the X draws over it in 2 frames; for "IT'S ME" the letters are spread with a red marker under the gap.

Labels (A): small grey caps 12 px with 4 px tracking under an object ("REFERENCE", "ATTEMPT 214"), or a line of 10 px grey caps above a big number. Pills with yellow fill as in our engine were not seen; the YOU marker in A is a plain grey "YOU" word with no arrow.

Exhibit insert (A): photograph 390 x 455 px with a white 8 px frame, rotated about 1.5 degrees, corner brackets 12 px outside it; to the right a red 6 x 36 px bar, "EXHIBIT A" Bold cap 20 px, two lines of grey 11 px caps underneath ("YEAR: 1897", "DOG: ALREADY ON A CHAIR"); holds 3.5 s, then a jump cut to a 1.31x tighter crop of the same photo with the label gone; photo grain temporal std 20. Exhibit C is a color photo in the same frame. We will use public domain or our own photos.

UI gags measured: REC frame 530 x 400 px, 4 px white outline, radius 16, "REC" with a red dot top left, "LIVE" grey bottom left, timecode 18 px bold bottom right, the scene inside at 0.5 scale; a views counter "2,218,392" in 22 px with three small hearts rising to the right of the frame; a 220 px progress track outside the frame with "LENGTH 00:11" and a red "SUBJECT IN FRAME 00:04". Case file folder with a red "041" stamp. B: phone mock 200 x 420 with a contact list, "DISCONNECTED" in red, typing dots; a 170 px rounded square clock inset top right; a floor plan with a dotted path; a 2x2 CCTV grid with "CAM 1 DINING ROOM" labels; a laugh sync waveform panel; a battery panel.

## 7. Transition specs

Glitch at a cut (A): 5 frames (range 1 to 13, median 5). Frame pattern heavy, heavy, heavy, light, light (then heavy, heavy, light, light, light when 10 frames). Heavy frame: R shifted left and B shifted right 7 to 18 px at 720p (10 to 27 at 1080p), 6 or more horizontal slices 10 to 70 px tall displaced up to 80 px, 30 to 80 white streaks 1 to 2 px tall and 6 to 60 px long scattered over the whole frame, the main shapes echoed 2 or 3 times horizontally at 40 percent, the frame scaled 1.03. Light frame: split 4 to 7 px, 10 to 20 streaks, no slices. The last frame before the cut is usually heavy too (the glitch straddles the cut, 1 to 2 frames before, 3 to 4 after). Our render: constant 8 px split for 8 frames, no streaks, fewer slices: it reads as a filter, not a glitch.

Glitch at a cut (B): 2 frames (1 to 4). Split 3 to 6 px, a few streaks, slight slices. One frame before the cut, one or two after.

Glitch hit without a cut (A): 31 times, on caption changes, same recipe, 3 to 5 frames. Use this on every caption change inside a held scene.

Hard cut: 18 percent of A cuts, 13 percent of B. Use when the next shot is a quiet insert.

Scene to card: fade out 8 frames, black 12 frames with 3 streak frames, card fades in 6 frames.

Black flash: not used mid video. Only before the big word: black 3 frames, 1 frame of picture, black 12 frames, then the word. Remove our black flash before "there are seven rules".

At rest: R left 1 px, B right 1 px at 720p (1.5 each at 1080p). Our rgbashift=rh=-2:bh=2 at 1080p is fine in size; the sign is reversed but that does not show.

## 8. Scare recipes (step by step)

1. The look (A 0:08): cut in with a 6 frame glitch, dog already standing. Hold 0.4 s. Draw a red dotted line from the dog's eye to the person over 8 frames. Hold 3 s with no motion. Caption changes once inside the hold, with a glitch hit.
2. The watched eye (A 1:32 to 1:35): eye icon left, dog right, hold 0.4 s, white dotted line draws eye to dog over 10 frames with ease out, the dog's eye dot turns red on the arrival frame, hold 1.9 s, glitch cut.
3. The face (A 2:00 to 2:08): cut to the dog face, black eyes, hold 1.6 s. Cut: teeth appear (instant). Hold 1 s then let the mouth morph by a few px over 2.5 s. Cut to the reference smiley with a red X (2 frames). Cut to smiley next to the face with red eyes and "ATTEMPT 214". No movement in the last shot.
4. The handle (A 2:18 to 2:26): bedroom wide, dog walks in from the right at 100 px per s over 4 s while two captions change with glitch hits. Cut: the dog's paw on the handle. Word card "WHO'S HERE?" with an X.
5. The twist (A 4:12 to 4:20): word card "WHO'S A GOOD BOY?", glitch hit with a red X. Cut to the narrator bust. 5 frame glitch, head is now a dog head with the same sunglasses. Hold 1.1 s still. Red tongue pops in. 0.3 s later a 5 frame glitch, red pupils behind the glasses. Hold 2.5 s. Cut to the seal alone.
6. The ending (A 4:20 to 4:33): seal 3.5 s, black 3 frames, picture 1 frame, black 12 frames, "STAY." pops from 1.41x in 2 frames, deep hit, "NEXT FILE" line after 3.4 s, hold to the end.
7. Not blinked (B 1:28): cut MR to XC face, clock inset pops top right, hold 2.8 s with zero change. The stillness is the scare.
8. Smile too far (B 2:44): C framing, cut to XC, the right mouth corner rises linearly for 2.6 s toward the eye. Cut back to MR.
9. Lights out (B 5:22): wide with the family. Luminance bright, dim, dimmer, bright, black over 4 frames. Red eye pairs light one by one 6 frames apart. After 0.6 s the lights come back in 2 frames and the red eyes stay on in the lit scene for 0.6 s.
10. The jaw (B 3:02): C framing, a thin yellow ellipse outline pops around the jaw hinge and holds 1.7 s, then the mouth drops a few px per word over 0.7 s.
11. Everyone turns (B 1:10): freeze outline on, forks held in the air (static), three red dotted sight lines draw from three heads to the speaker 6 frames apart.

## 9. Inserts

Photo cutaway: see section 6 (Exhibit). Build: black frame, photo at 0.6 of frame height, white 8 px border, rotate 1.5 degrees, corner brackets, label block right with a red bar, two grey lines, heavy animated grain (std 20) on the photo only, hold 3.5 s, then a 1.31x jump cut on the photo for the next caption.

Rows of five (A 0:30): five four legged dogs, 110 px wide each, pitch 240, one row at y 290; on the next caption one dog rotates up to two legs (10 frames) and the other four drop to 35 percent brightness.

Heads around the person (A 1:36): six dog face shields 100 px wide on a ring of radius about 400 px around a standing person pictogram 230 px tall; black eyes, then on the next caption all six get red eyes (instant, with a glitch hit).

Reference card (A 2:08): a 205 x 265 px white outlined rectangle with an outline smiley, "REFERENCE" under it in 12 px grey caps; 300 px to the right the dog face with red eyes and teeth, "ATTEMPT 214" under it.

Eye with a dotted line (A 1:34): eye icon 160 px wide at left third, dog at right third, line as in section 8 item 2.

REC frame (A 1:24, 1:44): see section 6.

## 10. Style numbers vs our engine

| Item | Measured | engine.py / render.py now | Change |
|---|---|---|---|
| Background | 1 to 3 everywhere, corners 1 | 0, pure black, vignette filter | keep black; vignette at most a 10 percent corner falloff; add a grain floor so black reads 1 to 3 |
| Figure white | 255, 255, 255 | #FFFFFF | same |
| Danger red (X, eyes) | X core about (235, 20, 30), B eyes (233, 37, 48) | #F81C28 (248, 28, 40) | close, keep |
| Rule line red | (230, 12, 47) | RED_LINE #AC1832 | change to #E60C2F |
| Yellow | key (244, 225, 93) | #F9DE75 | keep |
| Green check | (86, 237, 114) | #2ECC71 | change to #56ED72 |
| Lamp cone | #FFC85A at 42 percent, 45 degree half angle, behind figures | none | add lamp_cone() |
| Bulb glow | (253, 253, 117) | glow #F9DE75 radius 80 | add |
| Outline stroke on icons | 5 px at 720p (clock), 4 px (REC frame), 8 px (eye) | 11 px at 1080p | 11 is right for the eye; use 6 to 8 for frames and clocks |
| B figure outline | 3 to 4 px black at 720p | none | 5 px at 1080p on the family rigs |
| Caption font | cap 25 px at 720p, about 53 px font at 1080p, pitch 60, center y 902 | 40 px, pitch 52, y 900 | 53 px, pitch 60 |
| Caption appear | 5 frame fade | instant | add fade |
| HUD text | cap 8 px at 720p, color 48, y 55 of 720 | 20 px Montserrat Medium, color 90, y 56 of 1080 | 17 px, color 48, y 82 |
| HUD boxes | 21 x 23 px, pitch 23.5, fill (151, 142, 138), outline (41, 41, 41), absent before rule 1 | 26 x 26, pitch 40, fill 200, outline 90, always shown | 32 x 34, pitch 35, dimmer, hide until rule 1 |
| Card title | fade in 6 frames, no slide; ExtraBold cap 110 px at 1080p; box 195 px | slide in 0.27 s; 96 px; box 120 | fade, 157 px font, 195 px box |
| Card subtitle | Bold cap 48 px at 1080p, 25 ms per char, no cursor | 34 px, 40 ms per char, cursor | 69 px font, 25 ms, no cursor |
| Card progress | 7 mini boxes 57 px pitch 70 at y 760 | 7 dashes 44 x 6 at y 620 | mini boxes |
| Card lead in | 8 frame fade out, 12 black frames, 6 frame fade in | glitch cut | implement |
| Big word | 216 px Black at y 437, 2 frame pop, NEXT FILE line after 3 s | 150 px at y 500 | 216 px, y 437 |
| Vignette | not visible | vignette=angle=PI/4.3 | reduce to angle=PI/6 or remove |
| Grain | temporal std 2 to 3 on black (A), 1 (B), floor 1 to 3, sparse specks; photos std 20 | noise=alls=9 but black stays 0 | add a 2 level floor plus specks; heavy grain on photo inserts only |
| Scanlines | none (even and odd rows equal within 0.5) | 2 px lines at 5 percent | remove or set to 1 percent |
| RGB split at rest | 1 px each way at 720p | 2 px at 1080p | same |
| Glitch | 5 frames, split 10 to 27 px at 1080p, streak field, slices, echo | 8 frames constant 12 px, 6 slices | rewrite, see section 7 |
| Base zoom and drift | none; B pushes 3 to 5 percent on holds | 1.2 base, 1.0 to 1.02 drift | drop the drift, use an optional 1.0 to 1.04 push with ease in and out |
| Idle bob and blink | 0 | 2.5 px at 0.4 Hz, blink every 3.3 s | default off |
| Tail wag | 2 damped swings then still | continuous 4.5 Hz | damped, 2 swings |

## 11. Gaps, ranked by how much they show on screen

1. Camera coverage: we draw every scene at one size. B lives on W, M, MR, C, XC of one scene plus slow pushes. Added `camera()` and the dinner table scenes.
2. Glitch quality: ours is a steady 8 frame channel offset. Theirs is a 5 frame heavy and light pattern with streaks, slices and echo, used on cuts AND on caption changes. Added `glitch_frame()` and the hit on caption changes.
3. Rule card: ours slides and types slowly with dashes; theirs fades, types fast, has mini boxes, is preceded by a fade to black and is 25 percent bigger. Updated `draw_card()`.
4. Captions 25 percent too small and instant; HUD too bright and too high. Updated.
5. Entrances: theirs are rigged (the dog rotates up on the hip, the forearm rotates to the mouth, the napkin falls and spins, question marks stagger). Ours slide in. Added `stand_up()`, `walk_cycle()`, `arm_lift()`, `stagger_pop()`.
6. Lamp cone lighting and the B figure family with hats. Added `lamp_cone()` and the hat variants.
7. Word cards, counter cards, reference card, heads ring, rows of five, REC frame, freeze outline, dialogue bubbles with mixed case. Added as scenes.
8. Photo inserts with heavy grain and a jump zoom. Added `photo_insert()`.
9. Scares that happen inside the glitch (head swap, eyes on). Added `eyes_light_up()` and `teeth_smile()` that can be told to switch inside a glitch.
10. Our fake life (bob, blink, drift) covers stillness that should be deliberate. Defaults changed.

Things that could not be measured: the glass slide at B 0:34 (the burst shows the hand pouring and the glass static, so the slide may be a cut), the B bubble font size exactly (text bounding box contaminated by the grandpa's hair spikes, estimate 20 px cap), the steam line animation (1.6 s shot), the exact frame the mini boxes appear on the A card (cropped out of the burst), the B corner card title size (estimate 36 px cap), the knee bounce amplitude in px (only the area oscillation was measurable), the pea's exact velocity curve (grain defeated the blob tracker; the 10 fps burst gives about 240 px per s).


## 12. What the code now does (for the render chat)

- `engine.IDLE` defaults to still figures. `engine.set_idle('v2')` brings back the old breathing and blink. Tail wag is damped (2 swings) through `tail_wag()`; `wag='loop'` restores the continuous wag.
- New helpers in engine.py: `ease_in_out`, `tail_wag`, `walk_cycle`, `run_cycle`, `stand_up`, `draw_on`, `arm_lift`, `stagger_pop`, `head_turn`, `eyes_light_up`, `lights_fail`, `one_frame_flash`, `glitch_frame` (+ `GLITCH_PATTERN`), `film_floor`, `camera` (+ `FRAMINGS`), `lamp_cone`, `freeze_outline`, `dotted_line`, `sight_line`, `speech_bubble_dialogue`, `thought_bubble`, `photo_insert`, `diner`, `grandpa_face`, `dinner_table`, `dog_face`, `teeth_smile`, `rec_frame`, `word_card`, `counter`, `seal_v3` (our own seal text), `narrator_v3`, `big_word`.
- New scenes in scenes.py: `dog_rise`, `run`, `living_room`, `rows_five`, `heads_ring`, `dog_face`, `reference`, `eye_line`, `photo`, `rec`, `word_card`, `counter`, `narrator_v3`, `seal`, `dinner_wide`, `dinner_medium`, `dinner_close`, `dinner_face`, `lights_out`, `under_table`. `RULES_V3` is checked before the old `RULES`. All 46 scenes pass the smoke test at t = 0, 0.5 and 2.0 with 159 parameter sets.
- render.py: caption 53 px with a 5 frame fade and balanced two line breaks; HUD numbers from section 6 and boxes hidden until rule 1; card build from section 6 with the 8 frame fade out, 12 black frames and 6 frame fade in; measured glitch pattern 2 frames before and 3 after each cut, a hard cut every 6th, a 3 frame hit mid shot on holds over 6 s; black flash only before the big word (3, 1, 12); big word 216 px with the NEXT FILE line after 3 s; the 1.2 base zoom now carries a 4 percent ease in/out push instead of the linear drift, and camera scenes skip the base zoom; `film_floor` lifts black to 1..3 with dust specks; scanline alpha 4 of 255; vignette angle PI/7.
- The old seal text was the reference channel's own line and has been replaced by `seal_v3` with our own three words. Change `lines=` to the client's department name.
- Photos: `sc_photo` reads `photos/<name>.jpg` from the working folder and falls back to a grey card. Supply public domain or own photos.
