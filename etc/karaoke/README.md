Quick&dirty CLI tool to generate karaoke lyrics overlay video from a textfile
that specifies durations of notes&syllables. Supports ruby-annotations. Usage
example:

    cat lyrics.txt \
        | python3 karaoke.py - - \
        | ffmpeg \
            -y -f image2pipe -r 30 -i - \
            -c:v libx264 -preset veryslow -qp 0 -r 30 lyrics.mkv

The generated video can be used on its own or can be composited into an
existing video using chroma keying.
