#!/bin/bash
# bash one.sh <id> : sottotitoli + scena 3D + montaggio di un video
cd "$(dirname "$0")"
id="$1"
node render.js "$id" overlay 24 > "log_overlay_$id.txt" 2>&1
node render.js "$id" stage 24 > "log_stage_$id.txt" 2>&1
bash compose.sh "$id" > "log_compose_$id.txt" 2>&1
echo "FINITO $id $(date -u +%H:%M:%S)" >> batch_log.txt
