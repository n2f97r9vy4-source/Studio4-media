#!/bin/bash
# Video TikTok 9:16 dalle slide: prima slide 3 s, altre 4,5 s, ultima 5 s, scorrimento 0,4 s, audio muto (la musica la mette Valerio dall'app).
set -e
p=$1; out=$2; X=0.4
fs=($(ls $p/s*.png | sort -V)); n=${#fs[@]}
inp=(); filt=""
for i in "${!fs[@]}"; do d=4.5; [ $i -eq 0 ] && d=3; [ $i -eq $((n-1)) ] && d=5
  inp+=(-loop 1 -t $d -framerate 30 -i ${fs[$i]}); filt+="[$i:v]scale=1080:1920,format=yuv420p,setsar=1[v$i];"; durs[$i]=$d; done
prev=v0; acc=${durs[0]}
for ((i=1;i<n;i++)); do o=$(echo "$acc-$X" | bc); filt+="[$prev][v$i]xfade=transition=slideleft:duration=$X:offset=$o[x$i];"; prev=x$i; acc=$(echo "$o+${durs[$i]}" | bc); done
ffmpeg -y -loglevel error "${inp[@]}" -f lavfi -i anullsrc=r=44100:cl=stereo -filter_complex "${filt%;}" -map "[$prev]" -map $n:a -shortest -c:v libx264 -preset medium -crf 20 -r 30 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart $out
