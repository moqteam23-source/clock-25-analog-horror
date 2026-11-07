# Audio Analysis — Clock-25 narration

**Status:** analysis only. No verbatim narration is stored in this public repo.
The voice track is the master timeline. Verbatim lines live locally outside Git.

## Master track

- Verified duration: **488.85 s** (00:08:08.85), measured with `ffprobe` on the
  supplied voice WAV. The aligned caption track ends at 488.88 s; the 0.03 s gap
  is the trailing tail and is within tolerance.
- The voice is the master timeline. Scene timings are read from the aligned
  caption data, not estimated from word counts.
- Alignment method: offline forced alignment (faster-whisper was unavailable, so
  the offline pocketsphinx path was used). 218 of 220 lines anchored directly;
  2 interpolated by word count.
- Silence snapping: none applied. The track carries a continuous ambience bed, so
  `silencedetect` found no true pauses; beat starts came straight from the word
  timestamps.

## Pilot window: 0 to 20 seconds

Timecodes and script line numbers only. Narration text is referenced by line
number into the private source script, never reproduced here.

| Beat | Script line | Start (s) | End (s) | Duration (s) |
| --- | --- | --- | --- | --- |
| 1 | L1 | 1.24 | 5.26 | 4.02 |
| 2 | L2 | 5.26 | 7.00 | 1.74 |
| 3 | L3 | 7.00 | 11.12 | 4.12 |
| 4 | L4 | 11.12 | 12.50 | 1.38 |
| 5 | L5 | 12.50 | 17.13 | 4.63 |
| 6 | L6 | 17.13 | 17.99 | 0.86 |
| 7 | L7 | 17.99 | 21.03 | 3.04 |

- Beats fully inside 0 to 20 s: L1 to L6 (L6 ends at 17.99 s).
- L7 starts at 17.99 s and ends at 21.03 s, straddling the 20 s mark. The pilot
  cut ends clean at 20.00 s inside L7, or extends to 21.03 s to close it; the
  exact cut is confirmed at render time.
- Pre-roll before first narration: 0.00 to 1.24 s (black / cold open hold).

## Pilot audio slice

- A 0 to 20 s slice of the master voice is prepared locally for the gated pilot
  render. It is not committed (audio is git-ignored and the slice lives under
  `private/`). Render fps: 30 (Python pipeline).
