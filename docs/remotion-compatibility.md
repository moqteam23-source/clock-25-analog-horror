# Remotion compatibility and the two-pipeline setup

This repository holds two renderers for the same analog-horror style. They are both
valid; they differ in frame rate and in two accent hex values. Read this before you
touch colors or timing so the two stay in sync.

## The two pipelines

| | Primary: Python pipeline | Starter: Remotion |
|---|---|---|
| Location | `tools/pipeline/` | `src/` + `package.json` |
| Language | Python, Pillow, FFmpeg | React, TypeScript, Remotion |
| Frame rate | **30 fps** | **24 fps** |
| Role | primary production renderer for finished episodes | setup check and a short pilot preview |
| Entry | `python render.py all <cores>` (see README) | `npm run render:test`, `npm run render:pilot` |

The Python pipeline is the **primary** production path. The Remotion project is kept as
the setup/test path and the quick pilot preview. Neither replaces the other; do not
delete the Remotion project.

## Palette: one canonical set

The canonical production palette (used by the approved SVG asset pack and the Python
pipeline) is:

| Role | Canonical (Python, `tools/pipeline`, `assets/`) | Remotion starter (`src/theme.ts`) |
|---|---|---|
| Background | `#000000` | `#000000` |
| Figure / text white | `#FFFFFF` | `#FFFFFF` |
| Danger red | **`#F81C28`** (canonical) | `#D71920` |
| Highlight yellow | **`#F9DE75`** (canonical) | `#E6C84F` |
| Green | not used | not used |

Only these four colors are used. No gradients, no extra colors.

The red and yellow differ slightly between the two. **`#F81C28` and `#F9DE75` are
canonical.** If you want the Remotion pilot to match the primary pipeline exactly,
update `src/theme.ts`:

```ts
export const COLORS = {
  black: '#000000',
  white: '#FFFFFF',
  red: '#F81C28',    // was #D71920
  yellow: '#F9DE75', // was #E6C84F
} as const;
```

This change is intentionally **not** applied here, because the brief for this branch is
"do not redesign" and "do not silently pick one." It is offered as a one-line reconcile
you can approve separately.

## Frame rate: always state it

Every render instruction must name its fps, because the two pipelines differ:

- Python pipeline renders and encodes at **30 fps**. Caption timings in that pipeline are
  computed in seconds, so they are fps-independent, but the encoder and the glitch frame
  counts assume 30 fps.
- Remotion compositions are defined at **24 fps** (`durationInFrames` is frames, so a 20 s
  pilot is 480 frames at 24 fps). Converting a beat sheet between the two means recomputing
  frame counts: `frames_30 = seconds * 30`, `frames_24 = seconds * 24`.

The SVG character assets in `assets/characters/` are static vector art with no baked frame
rate, so they are safe to use from either pipeline.

## Glitch timing note

The Python glitch is a 5 frame heavy/light burst at 30 fps (about 167 ms). If you recreate
it in Remotion at 24 fps, use 4 frames (about 167 ms) to keep the same wall-clock duration,
not 5.
