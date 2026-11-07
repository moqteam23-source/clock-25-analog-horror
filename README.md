# Clock 25 Analog Horror — Remotion starter

This repository is a **starter workflow**, not a finished 8-minute video. It contains a project-level Claude skill, a minimal Remotion project, a 3-second setup test composition, a 20-second deterministic pilot placeholder, and local audio/frame-QC scripts. The first pilot graphics are placeholders and must be replaced or approved against the scene plan before story production.

## Requirements

- Node.js 20 or newer, npm, Git
- FFmpeg and ffprobe on PATH

## Setup and smoke test

```bash
git clone https://github.com/moqteam23-source/clock-25-analog-horror.git
cd clock-25-analog-horror
npm install
npm run render:test
```

The 3-second render checks the local Remotion setup; it does not use narration or story assets.

## Keep private files local

Put the WAV and script in the ignored `private/` folder. For Remotion, copy the approved WAV locally to `public/audio/narration.wav` (that path is gitignored too). Do not commit the WAV, script PDF, rendered video, or full-resolution source assets.

```bash
mkdir -p private public/audio
# Copy your files locally; do not add them to Git.
npm run inspect:audio -- private/narration.wav
```

The audio report gives metadata and candidate silences longer than 0.4 seconds. It cannot identify sentence boundaries or story beats; listen to the voice and verify all timing manually in `project/audio-analysis.md`.

## Approve the plan, then render only a pilot

1. Review the project skill in `.claude/skills/analog-horror-editor/SKILL.md` and supporting style/audio/QC documents.
2. Complete `project/audio-analysis.md` from the actual WAV and script. The project JSON's stated duration is a target to verify, not a substitute for inspection.
3. Write and approve `project/scene-plan.md` before adding story scenes.
4. Only after approval, render the 20-second `Pilot` preview:

```bash
npm run render:pilot -- --props='{"audioSrc":"audio/narration.wav"}'
```

If your Remotion CLI version does not pass props through npm's argument separator as expected, use:

```bash
npx remotion render src/index.ts Pilot out/pilot.mp4 --codec=h264 --scale=0.5 --props='{"audioSrc":"audio/narration.wav"}'
```

The audio path is relative to `public/`; the WAV itself stays untracked. The composition is 1920×1080 at 24 fps and 20 seconds (480 frames); `--scale=0.5` produces a 960×540 preview. The included visuals are only a test placeholder, not an approved story sequence.

## Frame extraction and review

```bash
npm run frames -- out/pilot.mp4 out/frames
```

Inspect the contact sheet and individual frames at 0, 5, 10, 15, and 19 seconds, then review the pilot with audio. Record issues and check `.claude/skills/analog-horror-editor/qc-checklist.md`. Do not continue to more scenes until the pilot is approved.

## Claude Code

Open this repository with Claude Code. The project skill is available at `.claude/skills/analog-horror-editor/SKILL.md`. Ask Claude to inspect the audio and repository, create the audio analysis and scene plan, and wait for approval. Never upload private voice/script files to a public repository.

## Suggested commits after review

```text
01-create-remotion-project
02-add-analog-horror-skill
03-add-audio-analysis
04-add-style-system
05-create-20-second-pilot
06-fix-pilot-after-qc
07-add-approved-scene-batch
```

---

## Python production pipeline (primary, 30 fps)

The primary analog-horror renderer is a Python/Pillow/FFmpeg pipeline under
`tools/pipeline/`. The Remotion project above stays as the setup check and pilot
preview. See `docs/remotion-compatibility.md` for how the two relate (the Python
pipeline runs at 30 fps, Remotion at 24 fps) and `docs/style-bible.md` for the
canonical visual spec.

### Requirements
- Python 3.10+ with `pillow` and `numpy` (`pip install pillow numpy`)
- FFmpeg and ffprobe on PATH
- Optional for the offline caption aligner: `pocketsphinx`, `num2words`

### Local render (private inputs stay local)
Keep the narration WAV and the script in the gitignored `private/` folder; they are
never committed. A render needs a `script.txt` (one sentence per line), a `voice.mp3`,
and a `channel.txt`, placed in a local working folder next to the pipeline:

```bash
cd tools/pipeline
# captions.json, voice.mp3, script.txt etc. are all gitignored and stay local
python render.py preview        # render a few preview frames, inspect, then:
python render.py all 2          # full render on 2 cores -> final.mp4 (local only)
```

`final.mp4`, the voice track, `captions.json` and all per-episode text are gitignored
and must not be committed to this public repository.

### Character assets
Approved, reusable SVG characters (one shared rig, named groups for animation) live in
`assets/characters/` with their own README and a preview contact sheet. Do not redesign
them; extend by adding new named-group SVGs.

### CI
`.github/workflows/render.yml` is manual only (`workflow_dispatch`). It runs a Python
syntax check, a pipeline import test, a structure check, and a secret/large-file guard,
and can optionally run the 3-second Remotion setup render. It never runs on push and
never calls paid AI services.
