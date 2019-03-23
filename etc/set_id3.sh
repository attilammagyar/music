#!/bin/bash

main()
{
    set_id3 "file.mp3" \
        "ISRCX1234567" track_number "track title" "album title"
}

set_id3()
{
    local file="$1"
    local isrc="$2"
    local track="$3"
    local title="$4"
    local album="$5"

    local artist="Attila M. Magyar"
    local genre="Rock"
    local year="2019"
    local total_tracks="1"
    # 512X512 -- not progressive
    local image="cover-512.jpg"
    local url="soundcloud.com/athoshun"
    local lyrics="lyrics.txt"

    # iconv -f utf-8 -t UTF-16BE "$lyrics" >/tmp/lyrics.txt
    # lyrics="/tmp/lyrics.txt"

    eyeD3 \
        --remove-all \
        "$file"

    # --encoding "utf16-be" \
    eyeD3 \
        --to-v2.3 \
        --text-frame="TSRC:$isrc" \
        --artist="$artist" \
        --album="$album" \
        --title="$title" \
        --genre="$genre" \
        --release-year="$year" \
        --track="$track" \
        --track-total="$total_tracks" \
        --add-comment="$url:URL:eng" \
        --add-image="$image:FRONT_COVER" \
        --add-lyrics="$lyrics:$title:eng" \
        "$file"
}

main "$@"
exit $?
