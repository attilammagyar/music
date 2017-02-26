#!/usr/bin/python3

import sys
import os
import os.path
import re
import math
import argparse

from PIL import Image, ImageDraw, ImageFont


def main(argv):
    """
    cat lyrics.txt \\
      | karaoke.py - - \\
      | ffmpeg -y -f image2pipe -r 30 -i - \\
            -c:v libx264 -preset veryslow -qp 0 -r 30 out.mkv

    cat lyrics.txt \\
      | karaoke.py - - \\
      | ffmpeg -y -f image2pipe -r 30 -i - -vcodec mpeg4 -qscale 1 -r 30 out.mp4
    """

    parser = argparse.ArgumentParser(description="Generate karaoke lyrics overlay video frames.")
    parser.add_argument(
        "-f", "--first-stanza",
        type=int,
        default=1,
        help="Skip stanzas before the given one"
    )
    parser.add_argument(
        "-l", "--last-stanza",
        type=int,
        default=0,
        help="Skip stanzas after the given one (0 or negative to render till the end)"
    )
    parser.add_argument(
        "input",
        default="-",
        help="Input file to read the lyrics from (or - for STDIN)"
    )
    parser.add_argument(
        "output",
        default="/tmp/",
        help="Output directory to put the images of individual frames"
            + " (or - to dump them to STDOUT to feed them to ffmpeg image2pipe)"
    )
    args = parser.parse_args()

    if args.input != "-" and not os.path.isfile(args.input):
        print(
            "Input must be the name of an existing file or - for STDIN",
            file=sys.stderr
        )
        return 1

    if args.output != "-" and not os.path.isdir(args.output):
        print(
            "Output must be the name of an existing directory or - for STDOUT",
            file=sys.stderr
        )
        return 1

    try:
        render_karaoke(args.input, args.output, args.first_stanza, args.last_stanza)

    except Exception as error:
        print(
            "ERROR: {} - {}".format(type(error).__name__, error),
            file=sys.stderr
        )
        return 2

    return 0


def render_karaoke(input_name, output, first_stanza, last_stanza):
    lyrics_raw = ""

    if input_name == "-":
        lyrics_raw = sys.stdin.read()
    else:
        with open(input_file, "r") as f:
            input_file = open(input_file)

    dummy_draw = ImageDraw.Draw(Image.new("RGB", (1, 1), Style.BLACK))
    parser = Parser(dummy_draw, Fonts)
    lyrics = parser.parse(lyrics_raw)

    last_stanza = min(last_stanza, len(lyrics.stanzas))
    last_stanza = max(0, last_stanza)
    first_stanza = max(first_stanza - 1, 0)
    first_stanza = min(first_stanza, len(lyrics.stanzas))

    if last_stanza < 1:
        last_stanza = len(lyrics.stanzas)

    stanzas = lyrics.stanzas[first_stanza:last_stanza]

    last_progress = None

    if output == "-":
        stdout = os.fdopen(sys.stdout.fileno(), 'wb')

        for frame, img in LyricsRenderer().render(lyrics, stanzas):
            last_progress = print_progress(last_progress, frame, stanzas)
            img.save(stdout, "PNG")
    else:
        for frame, img in LyricsRenderer().render(lyrics, stanzas):
            last_progress = print_progress(last_progress, frame, stanzas)
            img.save(os.path.join(output, "{:010d}.png".format(frame)), "PNG")


def print_progress(last_progress, frame, stanzas):
    if len(stanzas) == 0:
        return

    progress = 10000.0

    first = stanzas[0].first_frame
    last = stanzas[-1].last_frame
    total = last - first

    if total > 0:
        progress = float((frame - first) * 10000) / float(total)

    progress = "{}".format(int(progress / 100.0))

    if progress != last_progress:
        print("Generating karaoke lyrics video: {}%      ".format(progress), file=sys.stderr)

    return progress


class LyricsRenderer:
    def __init__(self):
        self.line_renderer = LineRenderer()

    def render(self, lyrics, stanzas):
        if len(stanzas) == 0:
            return

        frames = stanzas[0].first_frame

        for stanza in stanzas:
            shadow_img = self.render_shadow_stanza(lyrics, stanza)

            revealing_img = shadow_img.copy()
            revealing = ImageDraw.Draw(revealing_img)

            mask_img = Image.new("1", (lyrics.width, lyrics.height), 0)
            mask = ImageDraw.Draw(mask_img)

            for line in stanza.lines:
                self.line_renderer.render_border(revealing, line, LineRenderer.REVEALED)
                self.line_renderer.render_text(revealing, line, LineRenderer.REVEALED)

                for i in range(line.first_frame, line.last_frame):
                    ball, bbox = line.get_reveal_pos(frames)
                    x0, y0, w, h = bbox
                    x1 = x0 + w + 1
                    y1 = y0 + h + 1
                    mask.rectangle((x0, y0, x1, y1), 1)
                    frame_img = Image.composite(revealing_img, shadow_img, mask_img)
                    self.render_ball(frame_img, ball)
                    yield frames, frame_img
                    frames += 1

                pos = (
                    line.bbox_left,
                    line.bbox_top,
                    line.bbox_left + line.bbox_width + 1,
                    line.bbox_top + line.bbox_height + 1,
                )
                mask.rectangle(pos, 1)

    def render_ball(self, frame_img, ball):
        ball_size, ball_color, ball_pos = ball

        if ball_size == 0 or ball_pos is None:
            return

        x, y = ball_pos
        x0, y0 = int(float(x) - float(ball_size) / 2.0), y
        x1, y1 = int(float(x) + float(ball_size) / 2.0), y + ball_size
        frame = ImageDraw.Draw(frame_img)
        frame.ellipse((x0, y0, x1, y1), fill=ball_color)

    def render_shadow_stanza(self, lyrics, stanza):
        shadow_img = Image.new("RGB", (lyrics.width, lyrics.height), lyrics.background)
        shadow = ImageDraw.Draw(shadow_img)

        for line in stanza.lines:
            self.line_renderer.render_border(shadow, line, LineRenderer.SHADOW)

        for line in stanza.lines:
            self.line_renderer.render_text(shadow, line, LineRenderer.SHADOW)

        return shadow_img


class LineRenderer:
    SHADOW = "shadow"
    REVEALED = "revealed"

    def render_border(self, draw, line, state):
        self.render_line(draw, line, state, self.draw_text_border)

    def render_text(self, draw, line, state):
        self.render_line(draw, line, state, self.draw_text)

    def render_line(self, draw, line, state, draw_text_fn):
        for note in line.notes:
            self.render_note(draw, note, state, draw_text_fn)

    def render_note(self, draw, note, state, draw_text_fn):
        if state == self.SHADOW:
            text_color = note.style.shadow_color
            ruby_color = note.style.shadow_color
            border_color = note.style.shadow_border_color
        elif state == self.REVEALED:
            text_color = note.text_color
            ruby_color = note.ruby_color
            border_color = note.style.border_color
        else:
            raise ValueError(
                "State should be one of {!r}, unexpected state: {!r}".format(
                    [self.SHADOW, self.REVEALED],
                    state
                )
            )

        self.draw_note(draw, note, text_color, ruby_color, border_color, draw_text_fn)

    def draw_note(self, draw, note, text_color, ruby_color, border_color, draw_text_fn):
        s = note.style
        f = Fonts.get(s.font, s.text_size)
        bw = s.border_width
        bc = border_color
        p = (note.text_left, note.text_top)

        draw_text_fn(draw, f, p, note.text, text_color, bc, bw)

        if note.ruby:
            p = (note.ruby_left, note.ruby_top)
            f = Fonts.get(s.font, s.ruby_size)
            draw_text_fn(draw, f, p, note.ruby, ruby_color, bc, bw)

    @staticmethod
    def draw_text_border(draw, font, pos, text, color, border_color, border_width):
        if border_width < 1:
            return

        x, y = pos

        for dx in range(0 - border_width, border_width + 1):
            for dy in range(0 - border_width, border_width + 1):
                draw.text((x + dx, y + dy), text, font=font, fill=border_color)

    @staticmethod
    def draw_text(draw, font, pos, text, color, border_color, border_width):
        draw.text(pos, text, font=font, fill=color)


class Fonts:
    CACHE = {}

    @classmethod
    def get(cls, name, size):
        key = "{},{}".format(size, name)

        if key not in cls.CACHE:
            cls.CACHE[key] = ImageFont.truetype(name, size)

        return cls.CACHE[key]


class Parser:
    GLOBAL_SETTINGS = {
        "BACKGROUND",
        "FPS",
        "HEIGHT",
        "LINE_DISTANCE",
        "WIDTH"
    }

    COMMAND_RE = re.compile(r"\{([^}]*)\}")
    SETTING_RE = re.compile(r"^([A-Z0-9_]+)=(.*)$")
    NOTE_RE = re.compile(r"^(!{0,2})(([0-9]+(/[1-9][0-9]*)?,)+)([^|]*)(\|(.*))?$")
    #                       1:hl    2:durations                5:text    7:ruby
    COLOR_RE = re.compile(r"^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$")

    stanzas = None
    lines = None
    notes = None
    width = None
    height = None
    line_distance = None
    fps = None
    background = None
    style = None
    time = None
    line_number = None
    has_notes = None

    def __init__(self, draw, fonts=Fonts):
        self.draw = draw
        self.fonts = fonts

    def parse(self, text):
        self.reset()

        for stanza in text.split("\n\n"):
            self.lines = []
            self.notes = []

            for line in stanza.split("\n"):
                self.line_number += 1
                line = line.strip()

                for command in self.COMMAND_RE.findall(line):
                    setting_match = self.SETTING_RE.match(command)
                    note_match = self.NOTE_RE.match(command)

                    if setting_match:
                        self.parse_setting(setting_match)
                    elif note_match:
                        self.parse_note(note_match)
                    else:
                        raise InvalidCommand(command, "invalid command", self.line_number)

                if not line.endswith("\\"):
                    if len(self.notes) > 0:
                        self.lines.append(
                            Line(self.notes, self.width, 0, self.line_distance)
                        )

                    self.notes = []

            if len(self.notes) > 0:
                self.lines.append(
                    Line(self.notes, self.width, 0, self.line_distance)
                )

            if len(self.lines) > 0:
                self.stanzas.append(Stanza(self.lines, self.height, self.line_distance))

            self.line_number += 1

        return Lyrics(
            self.stanzas,
            self.width,
            self.height,
            self.fps,
            self.background
        )

    def reset(self):
        self.stanzas = []
        self.lines = []
        self.notes = []
        self.width = 1280
        self.height = 720
        self.line_distance = 35
        self.fps = 30
        self.background = Style.GREEN
        self.style = Style()
        self.time = 0
        self.line_number = 0
        self.has_notes = False

    def parse_setting(self, match):
        name, value = match.group(1), match.group(2)

        if name in self.GLOBAL_SETTINGS and self.has_notes:
            raise GlobalSettingsMustBeSpecifiedBeforeFirstNote(
                match.group(0),
                "global settings must be specified before the first note",
                self.line_number
            )

        if name == "FPS":
            self.fps = self.parse_positive_int(value)
        elif name == "BACKGROUND":
            self.background = self.parse_html_color(value)
        elif name == "WIDTH":
            self.width = self.parse_positive_int(value)
        elif name == "HEIGHT":
            self.height = self.parse_positive_int(value)
        elif name == "LINE_DISTANCE":
            self.line_distance = self.parse_non_negative_int(value)
        elif name == "FONT":
            self.style = self.style.set_font(value)
        elif name == "BPM":
            self.style = self.style.set_bpm(self.parse_positive_int(value))
        elif name == "TEXT_SIZE":
            self.style = self.style.set_text_size(self.parse_positive_int(value))
        elif name == "RUBY_SIZE":
            self.style = self.style.set_ruby_size(self.parse_positive_int(value))
        elif name == "RUBY_DISTANCE":
            self.style = self.style.set_ruby_distance(self.parse_non_negative_int(value))
        elif name == "BORDER_WIDTH":
            self.style = self.style.set_border_width(self.parse_non_negative_int(value))
        elif name == "SHADOW":
            self.style = self.style.set_shadow_color(self.parse_html_color(value))
        elif name == "SHADOW_BORDER":
            self.style = self.style.set_shadow_border_color(self.parse_html_color(value))
        elif name == "BORDER":
            self.style = self.style.set_border_color(self.parse_html_color(value))
        elif name == "TEXT":
            self.style = self.style.set_text_color(self.parse_html_color(value))
        elif name == "RUBY":
            self.style = self.style.set_ruby_color(self.parse_html_color(value))
        elif name == "HL1":
            self.style = self.style.set_hl1_color(self.parse_html_color(value))
        elif name == "HL2":
            self.style = self.style.set_hl2_color(self.parse_html_color(value))
        elif name == "BALL":
            self.style = self.style.set_ball_color(self.parse_html_color(value))
        elif name == "BALL_SIZE":
            self.style = self.style.set_ball_size(self.parse_non_negative_int(value))
        else:
            raise UnknownSetting(match.group(0), "unknown setting", self.line_number)

    def parse_note(self, match):
        highlight = match.group(1)
        duration_seconds = self.parse_durations(match.group(2))
        text = match.group(5)
        ruby = match.group(7) or ""

        first_frame = self.seconds_to_frames(self.time)
        self.time += sum(duration_seconds)
        last_frame = self.seconds_to_frames(self.time)

        total_frames = last_frame - first_frame + 1
        durations = [self.seconds_to_frames(d) for d in duration_seconds]
        durations[-1] = total_frames - sum(durations[0:-1])

        if highlight == "":
            highlight = Note.NORMAL
        elif highlight == "!":
            highlight = Note.HL1
        elif highlight == "!!":
            highlight = Note.HL2

        self.has_notes = True

        self.notes.append(
            Note(
                self.draw,
                text,
                ruby,
                self.style,
                highlight,
                durations,
                first_frame,
                last_frame,
                self.fonts
            )
        )

    def seconds_to_frames(self, seconds):
        return int(seconds * float(self.fps) + 0.5)

    def parse_durations(self, raw_durations):
        durations = []

        if raw_durations.endswith(","):
            raw_durations = raw_durations[0:-1]

        for d in raw_durations.split(","):
            whole_notes = 0.0

            if "/" in d:
                numerator, denominator = d.split("/")
                whole_notes = float(numerator) / float(denominator)
            else:
                whole_notes = float(d)

            seconds = (whole_notes * 240.0) / float(self.style.bpm)
            durations.append(seconds)

        return durations

    def parse_html_color(self, color):
        m = self.COLOR_RE.match(color)

        if m is None:
            raise InvalidColor(color, "expected an HTML color (#RRGGBB)", self.line_number)

        rgb = (m.group(1), m.group(2), m.group(3))

        return tuple(int(n, 16) for n in rgb)

    def parse_positive_int(self, n):
        return self.parse_int(n, 1, "positive, non-zero")

    def parse_non_negative_int(self, n):
        return self.parse_int(n, 0, "non-negative")

    def parse_int(self, n, min_value, error_msg):
        try:
            p = int(n)

        except Exception as e:
            raise InvalidInteger(n, "expected a {} integer".format(error_msg), self.line_number, e) from e

        if p < min_value:
            raise InvalidInteger(n, "expected a {} integer".format(error_msg), self.line_number)

        return p


class Lyrics:
    def __init__(self, stanzas, width, height, fps, background):
        self.stanzas = stanzas
        self.width = width
        self.height = height
        self.fps = fps
        self.background = background
        self.last_frame = self.stanzas[-1].last_frame if len(self.stanzas) > 0 else 0

    def dump(self):
        return {
            "stanzas": [s.dump() for s in self.stanzas],
            "width": self.width,
            "height": self.height,
            "background": self.background,
            "fps": self.fps,
            "last_frame": self.last_frame,
        }


class Stanza:
    def __init__(self, lines, frame_height, line_distance):
        self.lines = lines
        self.line_distance = line_distance
        self.height = sum(l.height + line_distance for l in self.lines) - line_distance
        self.first_frame = self.lines[0].first_frame
        self.last_frame = self.lines[-1].last_frame

        cursor_y = int(float(frame_height - self.height + self.lines[0].height) / 2.0) - self.line_distance

        for line in self.lines:
            cursor_y += self.line_distance
            line.set_middle_y(cursor_y)
            cursor_y += line.height

    def dump(self):
        return {
            "height": self.height,
            "line_distance": self.line_distance,
            "lines": [l.dump() for l in self.lines],
            "first_frame": self.first_frame,
            "last_frame": self.last_frame,
        }


class Line:
    middle_y = None
    top = None
    bbox_top = None
    bbox_left = None
    bbox_width = None
    bbox_height = None

    def __init__(self, notes, frame_width, middle_y, line_distance):
        self.notes = notes
        self.height = max(n.height for n in self.notes)
        self.width = sum(n.width for n in self.notes)
        self.left = int(float(frame_width - self.width) / 2.0)
        self.first_frame = self.notes[0].first_frame
        self.last_frame = self.notes[-1].last_frame
        self.set_middle_y(middle_y)
        self.line_distance = line_distance

    def set_middle_y(self, middle_y):
        self.middle_y = middle_y
        self.top = self.middle_y - int(float(self.height) / 2.0 + 1.0)

        cursor_left = self.left

        for note in self.notes:
            note.set_position(self.middle_y, cursor_left)
            cursor_left += note.width

        first_note_border_width = self.notes[0].style.border_width
        last_note_border_width = self.notes[-1].style.border_width

        self.bbox_top = min(n.top - n.style.border_width for n in self.notes)
        self.bbox_left = self.left - first_note_border_width
        self.bbox_height = max(n.height + 2 * n.style.border_width for n in self.notes)
        self.bbox_width = self.width + first_note_border_width + last_note_border_width

    def get_reveal_pos(self, frame):
        if frame < self.first_frame:
            s = self.notes[0].style

            return (
                (
                    s.ball_size,
                    s.ball_color,
                    (self.left, self.top - s.ball_size),
                ),
                (self.bbox_left, self.bbox_top, 0, 0),
            )

        if frame >= self.last_frame:
            s = self.notes[-1].style

            return (
                (
                    s.ball_size,
                    s.ball_color,
                    (self.left + self.width, self.top - s.ball_size),
                ),
                (self.bbox_left, self.bbox_top, self.bbox_width, self.bbox_height),
            )

        border_left = self.notes[0].style.border_width
        revealed_width = 0
        ball_bounce = 0.0

        for note in self.notes:
            if note.last_frame > frame:
                note_revealed_width, ball_bounce = note.get_reveal_pos(frame)
                revealed_width += note_revealed_width
                break

            revealed_width += note.width

        ball_pos = None
        s = note.style

        if ball_bounce is not None:
            ball_pos = (
                self.left + revealed_width,
                self.top - s.ball_size - int(ball_bounce * float(self.line_distance - s.ball_size)),
            )

        return (
            (
                s.ball_size,
                s.ball_color,
                ball_pos,
            ),
            (
                self.bbox_left,
                self.bbox_top,
                border_left + revealed_width,
                self.bbox_height,
            ),
        )

    def dump(self):
        return {
            "middle_y": self.middle_y,
            "width": self.width,
            "height": self.height,
            "left": self.left,
            "notes": [n.dump() for n in self.notes],
            "first_frame": self.first_frame,
            "last_frame": self.last_frame,
            "line_distance": self.line_distance,
        }


class Note:
    NORMAL = "normal"
    HL1 = "hl1"
    HL2 = "hl2"

    def __init__(
            self,
            draw,
            text,
            ruby,
            style,
            highlight,
            durations,
            first_frame,
            last_frame,
            fonts=Fonts
    ):
        self.text = text
        self.ruby = ruby
        self.style = style
        self.highlight = highlight
        self.durations = durations
        self.first_frame = first_frame
        self.last_frame = last_frame

        if self.highlight == self.HL1:
            self.text_color = style.hl1_color
            self.ruby_color = style.hl1_color
        elif self.highlight == self.HL2:
            self.text_color = style.hl2_color
            self.ruby_color = style.hl2_color
        else:
            self.text_color = style.text_color
            self.ruby_color = style.ruby_color

        self.text_width = self.measure_width(draw, fonts, self.style.text_size, text)
        self.ruby_width = self.measure_width(draw, fonts, self.style.ruby_size, ruby)

        self.text_top = 0
        self.text_left = 0
        self.ruby_top = 0
        self.ruby_left = 0
        self.width = max(self.text_width, self.ruby_width)
        self.height = (
            self.style.text_size
            + self.style.ruby_distance
            + self.style.ruby_size
        )

    def set_position(self, middle_y, left):
        ruby_left_offset = int(float(self.ruby_width - self.text_width) / 2.0)

        self.ruby_top = int(float(middle_y) - float(self.height) / 2.0)
        self.ruby_left = left + max(0, 0 - ruby_left_offset)
        self.text_top = self.ruby_top + self.style.ruby_size + self.style.ruby_distance
        self.text_left = left + max(0, ruby_left_offset)
        self.top = self.text_top if not self.ruby else self.ruby_top

    def measure_width(self, draw, fonts, size, text):
        font = fonts.get(self.style.font, size)
        return draw.textsize(text, font)[0]

    def get_reveal_pos(self, frame):
        revealed_parts = 0
        relative_frame = frame - self.first_frame

        for duration in self.durations:
            if duration > relative_frame:
                break

            relative_frame -= duration
            revealed_parts += 1

        parts = len(self.durations)
        partially_revealed = 1.0

        if duration > 1:
            partially_revealed = float(relative_frame) / float(duration - 1)

        revealed_width = int(
            float(self.width) * (float(revealed_parts) + partially_revealed)
            / float(parts)
        )

        ball_bounce = math.sqrt(max(0.0, 0.25 - (partially_revealed - 0.5) ** 2.0))

        return revealed_width, ball_bounce

    def dump(self):
        return {
            "text": self.text,
            "ruby": self.ruby,
            "highlight": self.highlight,
            "text_color": self.text_color,
            "ruby_color": self.ruby_color,
            "text_width": self.text_width,
            "ruby_width": self.ruby_width,
            "width": self.width,
            "height": self.height,
            "style": self.style.dump(),
            "first_frame": self.first_frame,
            "last_frame": self.last_frame,
            "durations": self.durations,
            "text_top": self.text_top,
            "text_left": self.text_left,
            "ruby_top": self.ruby_top,
            "ruby_left": self.ruby_left,
            "top": self.top,
        }


class Style:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREY = (160, 160, 160)
    LIGHT_GREY = (224, 224, 224)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 128)
    LIGHT_RED = (255, 164, 132)
    LIGHT_BLUE = (168, 212, 255)
    YELLOW = (255, 255, 0)

    def __init__(self):
        self.bpm = 120
        self.font = "/usr/share/fonts/truetype/takao-mincho/TakaoMincho.ttf"
        self.text_size = 32
        self.ruby_size = 15
        self.ruby_distance = 2
        self.border_width = 2
        self.shadow_color = self.GREY
        self.shadow_border_color = self.BLACK
        self.text_color = self.WHITE
        self.ruby_color = self.LIGHT_GREY
        self.border_color = self.BLUE
        self.hl1_color = self.LIGHT_RED
        self.hl2_color = self.LIGHT_BLUE
        self.ball_color = self.YELLOW
        self.ball_size = 8

    def dump(self):
        return {
            "bpm": self.bpm,
            "font": self.font,
            "text_size": self.text_size,
            "ruby_size": self.ruby_size,
            "ruby_distance": self.ruby_distance,
            "border_width": self.border_width,
            "shadow_color": self.shadow_color,
            "shadow_border_color": self.shadow_border_color,
            "text_color": self.text_color,
            "ruby_color": self.ruby_color,
            "border_color": self.border_color,
            "hl1_color": self.hl1_color,
            "hl2_color": self.hl2_color,
            "ball_size": self.ball_size,
            "ball_color": self.ball_color,
        }

    def copy(self):
        s = Style()
        s.bpm = self.bpm
        s.font = self.font
        s.text_size = self.text_size
        s.ruby_size = self.ruby_size
        s.ruby_distance = self.ruby_distance
        s.border_width = self.border_width
        s.shadow_color = self.shadow_color
        s.shadow_border_color = self.shadow_border_color
        s.text_color = self.text_color
        s.ruby_color = self.ruby_color
        s.border_color = self.border_color
        s.hl1_color = self.hl1_color
        s.hl2_color = self.hl2_color
        s.ball_size = self.ball_size
        s.ball_color = self.ball_color

        return s

    def set_bpm(self, bpm):
        s = self.copy()
        s.bpm = bpm
        return s

    def set_font(self, font):
        s = self.copy()
        s.font = str(font)
        return s

    def set_text_size(self, text_size):
        s = self.copy()
        s.text_size = text_size
        return s

    def set_ruby_size(self, ruby_size):
        s = self.copy()
        s.ruby_size = ruby_size
        return s

    def set_ruby_distance(self, ruby_distance):
        s = self.copy()
        s.ruby_distance = ruby_distance
        return s

    def set_border_width(self, border_width):
        s = self.copy()
        s.border_width = border_width
        return s

    def set_shadow_color(self, color):
        s = self.copy()
        s.shadow_color = color
        return s

    def set_shadow_border_color(self, color):
        s = self.copy()
        s.shadow_border_color = color
        return s

    def set_text_color(self, color):
        s = self.copy()
        s.text_color = color
        return s

    def set_ruby_color(self, color):
        s = self.copy()
        s.ruby_color = color
        return s

    def set_border_color(self, color):
        s = self.copy()
        s.border_color = color
        return s

    def set_hl1_color(self, color):
        s = self.copy()
        s.hl1_color = color
        return s

    def set_hl2_color(self, color):
        s = self.copy()
        s.hl2_color = color
        return s

    def set_ball_color(self, color):
        s = self.copy()
        s.ball_color = color
        return s

    def set_ball_size(self, size):
        s = self.copy()
        s.ball_size = size
        return s


class ParseError(ValueError):
    def __init__(self, value, problem, line_number, error=None):
        super().__init__(
            "Parse error: {!r}, {} in line {} ({!r})".format(value, problem, line_number, str(error))
        )


class InvalidCommand(ParseError):
    pass


class UnknownSetting(ParseError):
    pass


class InvalidInteger(ParseError):
    pass


class InvalidColor(ParseError):
    pass


class GlobalSettingsMustBeSpecifiedBeforeFirstNote(ParseError):
    pass


if __name__ == "__main__":
    sys.exit(main(sys.argv))
