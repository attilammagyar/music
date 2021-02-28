#!/bin/bash

freq_color="0x606060@1.0"
fps=30

frame_step=2
mintfps=$(($fps*$frame_step))

ffmpeg \
    -i audio.wav \
    -r $fps \
    -loop 1 \
    -i background.png \
    -i grid.png \
    -filter_complex \
    "[2:v]crop=1888:320:16:744[grid]; \
     [0:a]channelsplit[al][ar]; \
     [al]pan=stereo|c0=FL|c1=FL[afl]; \
     [ar]pan=stereo|c0=FR|c1=FR[afr]; \
     [afl]showfreqs=mode=bar:win_size=w2048:ascale=log:fscale=log:colors=$freq_color|$freq_color:s=60x320,crop=59:320:0:0[sfl]; \
     [afr]showfreqs=mode=bar:win_size=w2048:ascale=log:fscale=log:colors=$freq_color|$freq_color:s=60x320,crop=59:320:0:0[sfr]; \
     [sfl]minterpolate=$mintfps,tblend=all_mode=average,framestep=$frame_step,scale=944x320:flags=neighbor,hflip[sfli]; \
     [sfr]minterpolate=$mintfps,tblend=all_mode=average,framestep=$frame_step,scale=944x320:flags=neighbor[sfri]; \
     [sfli]pad=1888:360:0:0:0x000000@0.0[sflip]; \
     [sflip][sfri]overlay=944:0[sf]; \
     [sf][grid]overlay[sfg]; \
     [1:v][sfg]overlay=16:744:shortest=1,fade=in:0:$fps[out]" \
    -map "[out]" \
    -map 0:a \
    -c:v libx264 \
    -preset veryslow \
    -crf 16 \
    -c:a aac \
    -b:a 192k \
    -cutoff 19000 \
    -pix_fmt yuv420p \
    -movflags +faststart \
    -r $fps \
    art_track.mp4
