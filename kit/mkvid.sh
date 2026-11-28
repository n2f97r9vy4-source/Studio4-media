#!/bin/bash
# uso: mkvid.sh out.mp4 img1 img2 ...
out=$1; shift; n=$#; i=0; args=""; 
python3 - "$@" <<'P'
import sys
from PIL import Image, ImageFilter
for k,f in enumerate(sys.argv[1:]):
    s=Image.open(f).convert('RGB')
    bg=s.resize((1536,1920)).crop((228,0,1308,1920)).filter(ImageFilter.GaussianBlur(45));bg.paste(s,(0,285));bg.save(f'/tmp/ref/v{k}.png')
P
for ((k=0;k<n;k++)); do args="$args -loop 1 -t 3.2 -i /tmp/ref/v$k.png"; done
fc=""; prev="[0]"; off=2.8
for ((k=1;k<n;k++)); do lab="[x$k]"; [ $k -eq $((n-1)) ] && lab=",format=yuv420p,fps=30[v]"; fc="$fc$prev[$k]xfade=transition=fade:duration=0.4:offset=$off$lab"; [ $k -lt $((n-1)) ] && fc="$fc;"; prev="[x$k]"; off=$(python3 -c "print(round($off+2.8,1))"); done
ffmpeg -v error -y $args -filter_complex "$fc" -map "[v]" -c:v libx264 -preset veryfast -crf 20 -movflags +faststart $out
