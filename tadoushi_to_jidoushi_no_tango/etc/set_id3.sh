#!/bin/bash

# --set-text-frame=TSRC:QMEU31617484 \
cp lyrics.txt /tmp/
cp cover.jpg /tmp/

eyeD3 \
    --remove-all \
    "athoshun-tadoushi_to_jidoushi_no_tango.mp3"

eyeD3 \
    --no-tagging-time-frame \
    --to-v2.3 \
    --set-encoding=utf16-BE \
    -t "他動詞と自動詞のタンゴ (Tadoushi to Jidoushi no Tango)" \
    -a athoshun \
    -G Metal \
    -Y 2016 \
    --comment="eng:URL:https://soundcloud.com/athoshun" \
    "athoshun-tadoushi_to_jidoushi_no_tango.mp3"

eyeD3 \
    --no-tagging-time-frame \
    --set-encoding=utf16-BE \
    --lyrics="jpn:他動詞と自動詞のタンゴ (Tadoushi to Jidoushi no Tango) lyrics:$(cat /tmp/lyrics.txt)" \
    --add-image=/tmp/cover.jpg:FRONT_COVER \
    "athoshun-tadoushi_to_jidoushi_no_tango.mp3"
