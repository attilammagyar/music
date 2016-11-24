#!/bin/bash

main()
{
    local sound_ogg="$1"
    local width="$2"
    local height="$3"

    if [[ "$sound_ogg" = "" || "$width" = "" || "$height" = "" ]]
    then
        echo "Usage: <script> sound.ogg width height" >&2
        return 1
    fi

    for i in libvisual_infinite libvisual_jakdaw libvisual_oinksie goom goom2k1
    do
        echo "Generating $i.ogg"
        gst-launch filesrc location="$sound_ogg" \
            ! queue \
            ! tee name=stream \
            ! queue \
            ! oggdemux \
            ! vorbisparse \
            ! oggmux name=mux \
            ! filesink location="$i.ogg" stream. \
            ! queue \
            ! oggdemux \
            ! vorbisdec \
            ! audioconvert \
            ! queue \
            ! "$i" \
            ! ffmpegcolorspace \
            ! video/x-raw-yuv,framerate=30/1,width="$width",height="$height" \
            ! theoraenc \
            ! mux.
    done
}

main "$@"
exit $?
