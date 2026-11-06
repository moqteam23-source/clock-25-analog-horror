import React from 'react';
import {Composition} from 'remotion';
import {Pilot} from './scenes/Pilot';
import {TestCard} from './scenes/TestCard';

export const Root: React.FC = () => (
  <>
    <Composition
      id="TestCard"
      component={TestCard}
      durationInFrames={72}
      fps={24}
      width={1920}
      height={1080}
    />
    <Composition
      id="Pilot"
      component={Pilot}
      durationInFrames={480}
      fps={24}
      width={1920}
      height={1080}
      defaultProps={{audioSrc: ''}}
    />
  </>
);
