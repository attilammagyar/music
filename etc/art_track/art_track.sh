#!/bin/bash

ffmpeg \
    -i audio.mp3 \
    -r 60 \
    -loop 1 \
    -i background.png \
    -i grid.png \
    -filter_complex \
    "[2:v]crop=1880:300:20:760[grid]; \
     [0:a]showfreqs=mode=bar:ascale=log:fscale=log:colors=gray gray:s=40x300[sf]; \
     [sf]crop=40:300:0:0[sfc]; \
     [sfc]minterpolate=300,tblend=all_mode=average,framestep=5[sfci]; \
     [sfci]scale=1880x300:flags=neighbor[sfcis]; \
     [sfcis][grid]overlay[sfcisg]; \
     [0:a]showwaves=s=940x200:rate=60:colors=white:mode=p2p[sw]; \
     [sw]scale=1880x400:flags=bicubic[sws]; \
     [1:v][sfcisg]overlay=x=20:y=760[tmp]; \
     [tmp][sws]overlay=shortest=1:x=20:y=480:format=yuv420[tmp2]; \
     [tmp2]fade=in:0:36[out]" \
    -map "[out]" \
    -map 0:a \
    -c:v libx264 \
    -preset slow \
    -crf 10 \
    -c:a copy \
    -r 60 \
    art_track.mkv
