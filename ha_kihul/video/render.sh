#!/bin/bash

fps=24 ; python animation.py ha_kihul1_scene.js ha_kihul1_events.js $fps 50 \
    | ffmpeg -y -f image2pipe -r $fps -i - -c:v libx264 -preset slow -qp 0 -r $fps scene1.mkv

fps=24 ; python animation.py ha_kihul2_scene.js ha_kihul2_events.js $fps 66 \
    | ffmpeg -y -f image2pipe -r $fps -i - -c:v libx264 -preset slow -qp 0 -r $fps scene2.mkv

fps=24 ; python animation.py ha_kihul3_scene.js ha_kihul3_events.js $fps 25 \
    | ffmpeg -y -f image2pipe -r $fps -i - -c:v libx264 -preset slow -qp 0 -r $fps scene3.mkv
