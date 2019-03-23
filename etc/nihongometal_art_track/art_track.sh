#!/bin/bash

fps=30

ffmpeg \
    -i audio.mp3 \
    -r $fps \
    -loop 1 \
    -i background.png \
    -i lyrics.mkv \
    -filter_complex \
    "[1:v][2:v]overlay=721:110:shortest=1,fade=in:0:$fps[out]" \
    -map "[out]" \
    -map 0:a \
    -c:v libx264 \
    -preset slow \
    -crf 10 \
    -c:a copy \
    -r $fps \
    art_track.mkv
