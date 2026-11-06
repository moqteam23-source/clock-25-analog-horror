# Audio Sync Rules

- Narration is the master timeline; preserve its original duration, sample rate, pitch, speed, pauses, and content.
- Keep narration, music, and sound effects as separate timeline layers/tracks. Do not bake them together during planning.
- `npm run inspect:audio -- private/narration.wav` reports media metadata and silence intervals at the configured threshold. Silence detection is a technical aid, not sentence/paragraph transcription or story-beat analysis.
- Confirm sentence/paragraph and story-beat timecodes by listening to the recording and comparing against the script. Record uncertain boundaries for human review.
- For a pilot, use the relevant excerpt from the original WAV without changing its playback rate. A 20-second composition naturally limits playback to the composition duration; do not time-stretch the source.
- Put audio into the ignored local path `public/audio/narration.wav` only when rendering with Remotion. Never commit it.
- Align visual events and sound-effect cues to approved timecodes. Do not add a sound effect over narration without checking intelligibility.
