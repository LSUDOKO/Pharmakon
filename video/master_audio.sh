#!/usr/bin/env bash
# Final master: limit the rendered mix, two-pass linear loudnorm to -14 LUFS / -1 dBTP, mux with the joined video.
set -e
cd "$(dirname "$0")/film/out"
ffmpeg -v error -y -i audio.wav -af "alimiter=limit=0.63:attack=2:release=60:level=disabled" -c:a pcm_s24le audio_lim.wav
M=$(ffmpeg -hide_banner -i audio_lim.wav -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
v(){ echo "$M" | grep "\"$1\"" | sed 's/.*: "\(.*\)".*/\1/'; }
echo "measured I=$(v input_i) TP=$(v input_tp) LRA=$(v input_lra)"
ffmpeg -v error -y -i video_only.mp4 -i audio_lim.wav -map 0:v -map 1:a -c:v copy \
  -af "loudnorm=I=-14:TP=-1:LRA=11:measured_I=$(v input_i):measured_TP=$(v input_tp):measured_LRA=$(v input_lra):measured_thresh=$(v input_thresh):offset=$(v target_offset):linear=true,aresample=48000" \
  -c:a aac -b:a 320k -movflags +faststart pharmakon_film.mp4
ffmpeg -hide_banner -i pharmakon_film.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -A14 Summary | grep -E "I:|LRA:|Peak:"
