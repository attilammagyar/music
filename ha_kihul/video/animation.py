#!/usr/bin/python3

import sys
import os
import os.path
import re
import math
import argparse
import json
import time

from fractions import Fraction

from PIL import Image, ImageDraw, ImageMath


def vscale(scalar, vector):
    return (scalar * vector[0], scalar * vector[1])


def vsum(a, b):
    return (a[0] + b[0], a[1] + b[1])


def vdiff(a, b):
    return (a[0] - b[0], a[1] - b[1])


def rotate(point, origin, degrees):
    rad = (degrees * math.pi) / 180
    sin = math.sin(rad)
    cos = math.cos(rad)
    x, y = vdiff(point, origin);

    return vsum(origin, (x * cos - y * sin, x * sin + y * cos))


def ease(t):
    return t * t * (3 - 2 * t)


def sort_events_desc(evts):
    return sorted(evts, key=lambda evt: evt["time"], reverse=True)


class Animation:
    def __init__(self):
        self.sprites = []
        self.sprites_by_z = []
        self.events = {}
        self.now = 0
        self.previous_frame = None
        self.queued_events = None

    def key_to_event_id(self, key):
        return f"event_{key}"

    def get_event(self, key):
        return self.events.get(self.key_to_event_id(key), None)

    def load_sprite(self, parent_sprite, sprite):
        if len(sprite["position"]) != 2:
            return;

        img = Image.open(sprite["name"])

        # d = ImageDraw.Draw(img)
        # d.rectangle(((0, 0), img.size), outline=(255, 255, 0), width=5)

        sid = len(self.sprites)
        children = []

        self.sprites.append({
            "image": img,
            "center": vscale(0.5, img.size),
            "replace": None,
            "anchor": tuple(sprite["anchor"]),
            "position": tuple(sprite["position"]),
            "offset": (0, 0),
            "z": sprite["z"],
            "size": img.size,
            "scale": 1.0,
            "opacity": 1.0,
            "parent": parent_sprite,
            "rotate": 0,
            "children": children
        })

        for evt in sprite["events"]:
            evt_id = self.key_to_event_id(evt["key"]);

            if evt_id not in self.events:
                self.events[evt_id] = {
                    "state": "inactive",
                    "effects": [],
                }

            effect_def = evt["effect"];

            if effect_def["type"] == "replace":
                replace = Image.open(effect_def["img"])
            else:
                replace = None

            self.events[evt_id]["effects"].append({
                "def": effect_def,
                "sprite": sid,
                "param": 0,
                "replace": replace
            })

        for child in sprite["children"]:
            children.append(self.load_sprite(sid, child))

        return sid

    def load_scene(self, scene):
        self.load_sprite(None, scene["main"])

    def compute_center_rotation_scale_opacity_on_screen(self, sprite):
        rotation = sprite["rotate"];
        position = sprite["position"]
        scale = sprite["scale"]
        opacity = sprite["opacity"]
        center = vsum(
            position,
            vscale(scale, vdiff(sprite["center"], sprite["anchor"]))
        )
        center = rotate(center, position, rotation)
        center = vsum(center, vscale(sprite["scale"], sprite["offset"]))
        parent_sprite = sprite["parent"]

        if parent_sprite is not None:
            parent_sprite = self.sprites[parent_sprite]
            parent_center, parent_rotation, parent_scale, parent_opacity = self.compute_center_rotation_scale_opacity_on_screen(parent_sprite)
            center = vscale(parent_scale, center)
            center = vsum(parent_center, vdiff(center, vscale(parent_scale, parent_sprite["center"])))
            center = rotate(center, parent_center, parent_rotation)

            scale *= parent_scale
            opacity *= parent_opacity
            rotation += parent_rotation

        return (center, rotation, scale, opacity)

    def render(self, out_img):
        for sid in self.sprites_by_z:
            sprite = self.sprites[sid]
            img = sprite["image"]

            if sprite["replace"] is not None:
                img = sprite["replace"]

            center, rotation, scale, opacity = self.compute_center_rotation_scale_opacity_on_screen(sprite)

            if opacity < 0.0001:
                continue

            resample = Image.BICUBIC
            # resample = Image.NEAREST
            size = vscale(scale, img.size)
            img = img.resize((int(size[0]), int(size[1])), resample)
            img = img.rotate(-rotation, resample, True)

            if opacity < 1.0:
                opacity = max(0.0, opacity)
                alpha = img.getchannel("A")
                alpha = ImageMath.eval("convert(float(a) * {} + 0.5, 'L')".format(opacity), a=alpha)
                img.putalpha(alpha)

            dest_top_left = vdiff(center, vscale(1.0 / 2.0, img.size))
            dest_top_left = [int(dest_top_left[0]), int(dest_top_left[1])]
            src_top_left = [0, 0]

            if dest_top_left[0] < 0:
                src_top_left[0] = - dest_top_left[0]
                dest_top_left[0] = 0

            if dest_top_left[1] < 0:
                src_top_left[1] = - dest_top_left[1]
                dest_top_left[1] = 0

            out_img.alpha_composite(img, tuple(dest_top_left), tuple(src_top_left))

            # d = ImageDraw.Draw(out_img)
            # d.rectangle((top_left, vsum(top_left, (10, 10))), (255, 0, 128))

    def animate(self):
        done = True

        if self.previous_frame is None:
            self.previous_frame = self.now

        delta = self.now - self.previous_frame

        while len(self.queued_events) > 0 and self.queued_events[-1]["time"] <= self.now:
            evt = self.queued_events.pop()

            if evt["type"] == "down":
                self.start_event(evt["key"])
            else:
                self.rewind_event(evt["key"])

        for sprite in self.sprites:
            sprite["scale"] = 1.0
            sprite["opacity"] = 1.0
            sprite["rotate"] = 0.0
            sprite["offset"] = (0.0, 0.0)

        for evt in self.events.values():
            state = evt["state"]

            if state == "inactive":
                continue;

            effects = evt["effects"]
            rewind_done = True

            for effect in effects:
                effect_def = effect["def"]

                if "duration" in effect_def:
                    param = effect["param"]

                    if state == "started":
                        duration = effect_def["duration"]

                        if duration < 0.0001:
                            param = 1.0
                        else:
                            param = min(1.0, param + delta / duration)

                        if param < 1.0:
                            done = False
                    else:
                        if "rewind" in effect_def:
                            duration = effect_def["rewind"]
                        else:
                            duration = effect_def["duration"]

                        if duration < 0.0001:
                            param = 0.0
                        else:
                            param = max(0.0, param - delta / duration)

                        if param > 0.0:
                            done = False
                            rewind_done = False

                    effect["param"] = param

                sprite = self.sprites[effect["sprite"]]

                if effect_def["type"] == "scale":
                    eased_param = ease(param)
                    sprite["scale"] *= eased_param * effect_def["scale"] + 1.0 - eased_param;

                elif effect_def["type"] == "opacity":
                    eased_param = ease(param)
                    sprite["opacity"] *= eased_param * effect_def["opacity"] + 1.0 - eased_param;

                elif effect_def["type"] == "rotate":
                    sprite["rotate"] += ease(param) * effect_def["angle"]

                elif effect_def["type"] == "translate":
                    sprite["offset"] = vsum(
                        sprite["offset"],
                        vscale(ease(param), effect_def["offset"])
                    )

                elif effect_def["type"] == "replace":

                    if state == "started":
                        sprite["replace"] = effect["replace"]

                    elif sprite["replace"] is effect["replace"]:
                        sprite["replace"] = None

            if state == "rewinding" and rewind_done:
                evt["state"] = "inactive"

        self.previous_frame = self.now

    def rewind_event(self, key):
        evt = self.get_event(key)

        if evt is None or evt["state"] != "started":
            return

        evt["state"] = "rewinding"

    def start_event(self, key):
        evt = self.get_event(key);

        if evt is None or evt["state"] == "started":
            return

        evt["state"] = "started"

    def queue_events(self, event_layers):
        q = []

        for layer in event_layers.values():
            for evt in layer:
                q.append(evt)

        return sort_events_desc(q)

    def main(self, argv):
        if len(argv) < 4:
            print(f"Usage: {argv[0]} scene.js events.js FPS [end]", file=sys.stderr)
            return 1

        with open(argv[1], "r") as f:
            scene = json.loads("{" + f.read().split("{", 1)[1].rsplit("}", 1)[0] + "}")

        with open(argv[2], "r") as f:
            event_layers = json.loads(f.read())

        fps = max(1.0, min(60.0, float(argv[3])))

        end = None

        if len(argv) > 4:
            end = float(argv[4])

        self.load_scene(scene)
        self.queued_events = self.queue_events(event_layers)

        self.sprites_by_z = sorted(
            range(0, len(self.sprites)),
            key=lambda s: self.sprites[s]["z"]
        )

        if len(self.queued_events) < 1:
            return 0

        last_evt = self.queued_events[0]
        evt = self.get_event(last_evt["key"])

        if end is None:
            end = (
                last_evt["time"]
                + max(
                    effect["def"]["duration"] + effect["def"].get("rewind", effect["def"]["duration"])
                    for effect in evt["effects"] if "duration" in effect["def"]
                )
            ) + 2.0

        img = Image.new("RGBA", tuple(scene["size"]), (255, 255, 255))
        canvas = ImageDraw.Draw(img)
        stdout = os.fdopen(sys.stdout.fileno(), 'wb')
        self.now = 0
        prev_percent = ""
        start = time.time()

        while self.now < end:
            percent = self.format_number((100.0 * self.now) / end)

            if percent != prev_percent:
                eta = self.compute_eta(start, self.now, end)
                print(
                    f"Rendering... {percent}%    {self.format_number(self.now)}s/{self.format_number(end)}s    ETA: {eta}    ",
                    file=sys.stderr
                )
                prev_percent = percent

            canvas.rectangle(((0, 0), tuple(scene["size"])), (0, 255, 0))
            self.animate()
            self.render(img)
            img.save(stdout, "BMP")
            self.now += 1.0 / fps

        return 0

    def format_number(self, n):
        return str(int(n * 100.0 + 0.5) / 100.0)

    def compute_eta(self, start, ready, end):
        if ready < 0.01:
            return "???"

        now = time.time()
        elapsed = now - start
        backlog = end - ready

        return self.format_time((backlog * elapsed) / ready)

    def format_time(self, t):
        t = int(t + 0.5)

        return ":".join([
            str(int(t / 3600)),
            self.format_time_component(int((t % 3600) / 60)),
            self.format_time_component(t % 60),
        ])

    def format_time_component(self, c):
        if c > 9:
            return str(c)

        return "0" + str(c)


sys.exit(Animation().main(sys.argv));
