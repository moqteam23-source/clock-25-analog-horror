# Scene Plan: Clock-25 pilot (0 to 20 seconds)

**Status:** proposed, awaiting human approval. Do not render until approved.

Renderer: Python / Pillow / FFmpeg pipeline at 30 fps. Master timeline: the
supplied voice (verified 488.85 s; see `audio-analysis.md`).

## Assets and props (decision)

- **Characters:** the approved SVG figures in `assets/characters/` only. No new
  characters, no AI-generated figures.
- **Props:** deterministic, code-drawn vector pictograms rendered by the Python
  pipeline (`tools/pipeline/engine.py` drawing helpers), not image files and not
  AI-generated. They are parametric functions (for example a digital clock, a
  phone, a clipboard and pen, a drawer and small garment, the seven count boxes,
  an analog clock), so they are deterministic and reusable in any future scene by
  calling the same helper. This follows `docs/style-bible.md` section 4:
  objects are white outlines with near-black `#0C0C0C` fill, or solid white
  silhouettes.
- **Palette (canonical, unchanged):** black `#000000`, white `#FFFFFF`,
  red `#F81C28`, yellow `#F9DE75`. No other colors, no gray, no gradients
  (except the single lamp cone allowed by the style bible).

## Privacy

This public plan references narration by **script line number** (L1, L2, ...).
Verbatim voiceover is never reproduced here, including on-screen card copy, which
is referenced by line and kept in the local private plan. The template's
"Narration" and "Text" fields carry line references, not the exact phrases.

---

```text
Scene 01: opening clock
Time: 00:00:00.000-00:00:05.260
Narration: beat L1
Characters: viewer figure (you-marker); 03_human_sleeping.svg in bed
Props: digital clock pictogram (code-drawn, impossible hour reading), bed
Pose: sleeper lying in bed; clock static
Movement: black hold 0.000 to 1.240; clock pictogram fades in at 1.240; digits hold; no figure movement
Camera: locked
Text: clock prop art only (the hour reading); no narration copy on screen
Colors: white figure and clock on black; red glow on the hour digits only
SFX: low tick at 1.240; static cut into scene (synth stand-ins until real files provided)
Transition: hard cut in; hard cut out
End frame: clock pictogram lit, sleeper still, red digit glow
QC notes: digit legibility at 1080p; red used only on digits; sync L1 start 1.24

Scene 02: device beat
Time: 00:00:05.260-00:00:07.000
Narration: beat L2
Characters: viewer figure (you-marker)
Props: phone pictogram (code-drawn, white outline with near-black fill, reads 1:59)
Pose: phone held upright, screen to camera
Movement: screen snaps on at 5.300; slight glitch jitter at 6.200
Camera: locked
Text: prop screen reading only; no narration copy on screen
Colors: white phone outline and reading, black field; no red
SFX: click at 5.300; static at 6.200
Transition: hard cut
End frame: phone screen lit
QC notes: keep yellow out; short beat (1.74 s), avoid crowding

Scene 03: intruder and the offered object
Time: 00:00:07.000-00:00:11.120
Narration: beat L3
Characters: 03_human_sleeping.svg in bed; 01_human_standing.svg as a white faceless figure near the bed
Props: clipboard and pen pictograms (code-drawn)
Pose: sleeper still; standing figure extends the offered object toward the viewer
Movement: object extends in over 7.000 to 8.500; holds; red accent appears on the object tip at 9.800 (reveal beat only)
Camera: locked
Text: none
Colors: white bed, sleeper and standing figure on black; the figure stays pure white and faceless (at most one eye dash, no face, no gray); red only on the object tip at the reveal
SFX: paper rustle at 7.200; low breath bed under the beat
Transition: hard cut
End frame: object held out, red tip, sleeper unmoving
QC notes: the intruder reads as wrong by posture, not by color; no gray anywhere; red limited to the tip and only at 9.800; longest early beat (4.12 s)

Scene 04: cold-open count
Time: 00:00:11.120-00:00:12.500
Narration: beat L4
Characters: none
Props: seven count boxes (code-drawn; the style bible's allowed repeating UI)
Pose: n/a
Movement: boxes draw in left to right across 11.120 to 12.300
Camera: locked
Text: count label per L4 (copy in private plan); enters 11.200, exits at scene end; upper center
Colors: white boxes and label on black; one box tinted red
SFX: seven ticks, one per box, 11.120 to 12.300
Transition: hard cut
End frame: seven boxes, label above
QC notes: box spacing even; red on a single box only; sync ticks to box draws

Scene 05: drawer beat
Time: 00:00:12.500-00:00:17.130
Narration: beat L5
Characters: none
Props: drawer and single small garment pictograms (code-drawn, white silhouettes)
Pose: n/a
Movement: drawer slides open 12.700 to 13.800; garment lifts out and drifts 14.500 to 16.800
Camera: locked
Text: none
Colors: white drawer and garment on black; no red
SFX: pop at 12.700 (drawer); soft tick bed
Transition: hard cut
End frame: open drawer, garment mid-air
QC notes: motion stays slow and uneasy; longest pilot beat (4.63 s); keep yellow out

Scene 06: first rule card
Time: 00:00:17.130-00:00:17.990
Narration: beat L6
Characters: none
Props: RULE card (code-drawn label card)
Pose: n/a
Movement: card slams in at 17.130; holds
Camera: locked
Text: rule-card copy per L6 (copy in private plan); enters 17.130, holds to scene end; centered
Colors: white card and text, black field; red underline on the rule number
SFX: thud at 17.130
Transition: hard cut in
End frame: first rule card full frame
QC notes: very short beat (0.86 s); text must land instantly; check card copy spelling against private plan

Scene 07: clock steps back
Time: 00:00:17.990-00:00:20.000
Narration: beat L7 (straddles the 20 s pilot edge; full beat ends 21.030)
Characters: none
Props: analog clock pictogram (code-drawn)
Pose: n/a
Movement: clock hand steps back one hour starting 18.200; pilot holds the frame at 20.000
Camera: locked
Text: none
Colors: white clock on black; no red
SFX: tick at 18.200
Transition: pilot cut at 20.000 (clean). Full render continues the beat to 21.030
End frame: clock hand mid-step back
QC notes: this beat crosses the 20 s pilot boundary; confirm exact cut (20.000 vs 21.030) at render time
```

---

Pilot coverage: 00:00:00.000 to 00:00:20.000, scenes contiguous, no overlaps.
Scenes beyond this window are not planned here. The first render is this 0 to 20
second pilot only, after approval.
