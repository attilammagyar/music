#!/bin/bash

freq_color="0x668eff@1.0"
wave_color="0xcddaff@0.85"

ffmpeg \
    -i audio.mp3 \
    -r 60 \
    -loop 1 \
    -i background.png \
    -i grid.png \
    -filter_complex \
    "[2:v]crop=1880:300:20:760[grid]; \
     [0:a]showfreqs=mode=bar:win_size=w2048:ascale=log:fscale=log:colors=$freq_color|$freq_color:s=42x300[sfb]; \
     [sfb]crop=40:300:0:0[sfbc]; \
     [sfbc]minterpolate=180,tblend=all_mode=average,framestep=3[sfbci]; \
     [sfbci]scale=1880x300:flags=neighbor[sfbcis]; \
     [sfbcis][grid]overlay[sfg]; \
     [0:a]aformat=channel_layouts=mono,showwaves=s=1880x201:rate=60:split_channels=0:colors=$wave_color:mode=cline[sw]; \
     [sw]scale=1880x402:flags=fast_bilinear[sws]; \
     [1:v][sfg]overlay=x=20:y=760[tmp]; \
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
