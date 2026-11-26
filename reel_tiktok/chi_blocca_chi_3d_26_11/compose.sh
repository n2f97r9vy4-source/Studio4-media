#!/bin/bash
# bash compose.sh <id>  →  out/chi_blocca_chi_<id>.mp4 (1080x1920, 24 fps, H.264 + AAC)
set -e
cd "$(dirname "$0")"
id="$1"
mkdir -p out
ffmpeg -v error -y -i "overlay_$id.mp4" -i "stage_$id.mp4" -loop 1 -i mask.png -i "aud/$id.wav" \
 -filter_complex "[0:v]format=gbrp[o];[1:v]format=rgba[s];[2:v]format=gray[m];[s][m]alphamerge[sm];[o][sm]overlay=50:345:format=gbrp[v0];[v0]scale=out_color_matrix=bt709:out_range=tv,format=yuv420p[v]" \
 -map "[v]" -map 3:a -c:v libx264 -crf 21 -preset slow -pix_fmt yuv420p -r 24 \
 -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \
 -af "volume=4dB,alimiter=limit=0.891:attack=3:release=60:level=disabled" -c:a aac -b:a 160k -ar 44100 -shortest -movflags +faststart "out/chi_blocca_chi_$id.mp4"
ffprobe -v error -show_entries format=duration,size -of default=nw=1 "out/chi_blocca_chi_$id.mp4"
