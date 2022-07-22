Art Track Generator
===================

User `art_track.sh` to generate a video (featuring a waveform and an audio
power spectrum display, similar to [Winamp][wa]'s), from the cover art of a
song (or a podcast) in order to upload it to video-sharing sites like
[YouTube][yt]

  [yt]: https://www.youtube.com
  [wa]: https://en.wikipedia.org/wiki/Winamp

Usage
-----

 * Edit `template.xcf` in [GIMP][gimp]. Follow the instructions on the layers.
 * Hide the layer named **BlackOverlay** if the background looks too dark.
 * Save the image as `background.png`.
 * Use the contents of the layer named **GridMask** as a layer mask to create a
   copy from your background image where every pixel is transparent, except for
   those where the mask is white. Save this image as `grid.png`. This image
   will be used for separating the bars of the audio power spectrum display.
 * Make a copy of your song in high-quality MP3 format as `audio.wav`.
 * Run `art_track.sh` (make sure that a recent version of [FFmpeg][ffmpeg] is
   on your `PATH`) to generate `art_track.mkv`.

  [gimp]: https://www.gimp.org
  [ffmpeg]: https://www.ffmpeg.org
