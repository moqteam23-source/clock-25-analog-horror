#!/usr/bin/env bash
set -euo pipefail

input="${1:-out/pilot.mp4}"
out_dir="${2:-out/frames}"
if [[ ! -f "$input" ]]; then
  echo "Video not found: $input" >&2
  echo "Usage: bash scripts/extract-frames.sh [video.mp4] [output-directory]" >&2
  exit 1
fi
mkdir -p "$out_dir"
# Representative pilot timestamps: entrance, action, text hold, transition, ending.
for point in 0 5 10 15 19; do
  ffmpeg -hide_banner -loglevel error -y -ss "$point" -i "$input" -frames:v 1 -q:v 2 "$out_dir/frame-${point}s.jpg"
done
ffmpeg -hide_banner -loglevel error -y -pattern_type glob -i "$out_dir/frame-*s.jpg" -vf 'scale=640:-1,tile=3x2:padding=12:margin=12:color=black' -frames:v 1 "$out_dir/contact-sheet.jpg"
echo "Frames and contact sheet saved in $out_dir"
