#!/usr/bin/env node
import {spawnSync} from 'node:child_process';
import {mkdir, writeFile} from 'node:fs/promises';
import path from 'node:path';

const input = process.argv[2] ?? 'private/narration.wav';
const output = process.argv[3] ?? 'project/audio-analysis.md';

function run(command, args) {
  const result = spawnSync(command, args, {encoding: 'utf8'});
  if (result.error) throw new Error(`${command} could not start: ${result.error.message}`);
  if (result.status !== 0) throw new Error(result.stderr || `${command} exited with ${result.status}`);
  return result;
}

function timestamp(seconds) {
  const ms = Math.round(seconds * 1000);
  const h = Math.floor(ms / 3600000);
  const m = Math.floor((ms % 3600000) / 60000);
  const s = Math.floor((ms % 60000) / 1000);
  const milli = ms % 1000;
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}.${String(milli).padStart(3, '0')}`;
}

try {
  const metadata = JSON.parse(run('ffprobe', [
    '-v', 'error', '-select_streams', 'a:0', '-show_entries',
    'stream=sample_rate,channels,channel_layout:format=duration', '-of', 'json', input,
  ]).stdout);
  const stream = metadata.streams?.[0];
  const duration = Number(metadata.format?.duration);
  if (!stream || !Number.isFinite(duration)) throw new Error('No readable audio stream or duration found.');

  const detection = run('ffmpeg', [
    '-hide_banner', '-i', input, '-af', 'silencedetect=noise=-35dB:d=0.4', '-f', 'null', '-',
  ]);
  const log = detection.stderr;
  const starts = [...log.matchAll(/silence_start: ([\d.]+)/g)].map((match) => Number(match[1]));
  const ends = [...log.matchAll(/silence_end: ([\d.]+) \| silence_duration: ([\d.]+)/g)].map((match) => ({end: Number(match[1]), duration: Number(match[2])}));
  const silences = ends.map((item, index) => ({start: starts[index] ?? Math.max(0, item.end - item.duration), end: item.end, duration: item.duration}));
  if (starts.length > ends.length) {
    const start = starts.at(-1);
    if (Number.isFinite(start)) silences.push({start, end: duration, duration: Math.max(0, duration - start)});
  }

  const lines = [
    '# Audio Analysis', '',
    `- Source: \`${input}\``,
    `- Duration: ${timestamp(duration)} (${duration.toFixed(3)} seconds)`,
    `- Sample rate: ${stream.sample_rate} Hz`,
    `- Channels: ${stream.channels}${stream.channel_layout ? ` (${stream.channel_layout})` : ''}`,
    '- Silence detector: FFmpeg `silencedetect`, threshold -35 dB, minimum 0.4 seconds.',
    '- Note: detected silence is not a transcript or a verified story-beat boundary. Listen and align the script manually.', '',
    '## Detected pauses (review by listening)', '',
    ...(silences.length ? silences.map((item) => `- ${timestamp(item.start)}–${timestamp(item.end)} (${item.duration.toFixed(3)} s)`) : ['- No pauses met the configured threshold.']),
    '', '## Human-verified narration and story beats', '',
    'Fill this section after listening to the recording and checking the script. Keep the narration unchanged.',
    '', '| Start | End | Exact script reference / beat | Notes |', '|---|---|---|---|', '| | | | |', '',
  ];
  await mkdir(path.dirname(output), {recursive: true});
  await writeFile(output, lines.join('\n'), 'utf8');
  console.log(`Wrote ${output} (${timestamp(duration)}).`);
} catch (error) {
  console.error(error.message);
  console.error('Usage: npm run inspect:audio -- [input.wav] [output.md]');
  process.exitCode = 1;
}
