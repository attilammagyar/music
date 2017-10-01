This script was used to render the cover image for my [Binary Black Holes
song][1]. It is a raytracer, but it uses Schwarzschild geometry instead of
Euclidean. Here's an [example rendering][0].

The algorithm in the `trace()` function was inspired by, or rather: stolen from
[Riccardo Antonelli's work][2]. But unlike that, the model in this script is
quite unscientific, because after reading a lot of interesting articles about
black hole visualization (e.g. [this][3] and [this][4]) and watching all the
relevant videos from [PBS SpaceTime][5] and [3Blue1Brown][6], I still failed to
implement the calculations for rendering a black hole binary properly.
Instead, I cheated by projecting and tiling a flat image far behind a single
black hole (and also behind the virtual camera), and then rendered the second
black hole with using the first rendering as a background image. Not very
scientific, but the result looks good enough for the cover image (except for
the extra reflections of the first black hole near the second one). Using pure
Python instead of [NumPy][7] to do a lot of linear algebra might seem like a
bad idea, but [PyPy][8] can make this script surprisingly fast. It uses
[Pillow][10] for image processing. The song is distributed under [CC-BY-SA
3.0][9], and this script is [WTFPL 2][11].

 [0]: https://github.com/attilammagyar/music/raw/master/binary_black_holes/cover_img/black_hole_glow.png
 [1]: https://soundcloud.com/athoshun/binary-black-holes
 [2]: http://rantonels.github.io/starless/
 [3]: http://adsabs.harvard.edu/full/1979A%26A....75..228L
 [4]: https://arxiv.org/abs/1502.03808
 [5]: https://www.youtube.com/playlist?list=PLsPUh22kYmNAmjsHke4pd8S9z6m_hVRur
 [6]: https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr
 [7]: http://www.numpy.org/
 [8]: http://pypy.org/
 [9]: http://creativecommons.org/licenses/by-sa/3.0/
 [10]: https://python-pillow.org/
 [11]: http://www.wtfpl.net
