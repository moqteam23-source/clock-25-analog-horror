import React from 'react';
import {AbsoluteFill} from 'remotion';
import {COLORS} from '../theme';

export const TestCard: React.FC = () => (
  <AbsoluteFill
    style={{
      backgroundColor: COLORS.black,
      color: COLORS.white,
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'Arial, sans-serif',
      fontSize: 64,
      letterSpacing: 4,
    }}
  >
    SYSTEM TEST — 24 FPS
  </AbsoluteFill>
);
