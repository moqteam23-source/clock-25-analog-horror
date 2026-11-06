import React from 'react';
import {AbsoluteFill, Audio, staticFile, useCurrentFrame} from 'remotion';
import {COLORS} from '../theme';

export type PilotProps = {
  /** Optional path relative to public/, e.g. audio/narration.wav. Keep the file untracked. */
  audioSrc?: string;
};

/**
 * A deliberately small pipeline-check placeholder, not a finished story scene.
 * Replace it only after the scene plan and visual direction have been approved.
 */
export const Pilot: React.FC<PilotProps> = ({audioSrc = ''}) => {
  const frame = useCurrentFrame();
  const clockScale = frame >= 288 ? 1.04 : 1;
  const textOpacity = frame < 24 ? frame / 24 : 1;

  return (
    <AbsoluteFill style={{backgroundColor: COLORS.black, color: COLORS.white, fontFamily: 'Arial, sans-serif'}}>
      {audioSrc ? <Audio src={staticFile(audioSrc)} /> : null}
      {/* Deterministic scanlines overlay the entire composition, including text. */}
      <AbsoluteFill style={{pointerEvents: 'none', zIndex: 5, opacity: 0.13}}>
        <svg width="100%" height="100%" viewBox="0 0 1920 1080" preserveAspectRatio="none">
          <defs>
            <pattern id="scanlines" width="2" height="6" patternUnits="userSpaceOnUse">
              <rect width="2" height="2" fill="#FFFFFF" />
            </pattern>
          </defs>
          <rect width="1920" height="1080" fill="url(#scanlines)" />
        </svg>
      </AbsoluteFill>
      <div style={{position: 'absolute', top: 110, left: 0, right: 0, textAlign: 'center', fontSize: 48, letterSpacing: 8, opacity: textOpacity}}>
        IF YOUR CLOCK EVER SAYS
      </div>
      <div style={{position: 'absolute', top: 215, left: 0, right: 0, textAlign: 'center', color: COLORS.red, fontSize: 160, fontWeight: 700, letterSpacing: 12, transform: `scale(${clockScale})`}}>
        25:00
      </div>
      {/* Simple geometric placeholder: person under a blanket. */}
      <svg style={{position: 'absolute', left: 330, top: 515}} width="1260" height="400" viewBox="0 0 1260 400" aria-label="Simple figure lying in bed">
        <path d="M80 320 H1160" stroke={COLORS.white} strokeWidth="8" fill="none" />
        <circle cx="390" cy="250" r="58" stroke={COLORS.white} strokeWidth="8" fill={COLORS.black} />
        <path d="M448 260 H900 L1050 318 H480 Z" stroke={COLORS.white} strokeWidth="8" fill={COLORS.black} />
        <path d="M480 318 H1040" stroke={COLORS.white} strokeWidth="8" fill="none" />
        <path d="M345 320 V360 M1090 320 V360" stroke={COLORS.white} strokeWidth="8" fill="none" />
      </svg>
      <div style={{position: 'absolute', bottom: 76, left: 0, right: 0, textAlign: 'center', fontSize: 30, letterSpacing: 5}}>
        DO NOT GET OUT OF BED
      </div>
    </AbsoluteFill>
  );
};
