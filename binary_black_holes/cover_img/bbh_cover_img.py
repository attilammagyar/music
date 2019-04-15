from __future__ import division

import os.path
import sys
import math
import time
import multiprocessing as mp

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops


# NOTE: instead of a celestial sphere, this script just tiles a flat image
# behind and in front of the virtual camera - this is a hack that I used for
# rendering cover art for a song, the original purpose of this script.


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREY = (128, 128, 128)

ALPHA = 3

X, Y, Z = 0, 1, 2

# 3D coordinates are given in terms of the Schwarzschild radius, ie. 1 = r_S
NULL_3D = (0.0, 0.0, 0.0)

CAMERA_DEPTH = 0.01

PHOTON_SPHERE_RADIUS = 1.5
SHADOW_RADIUS = (3.0 ** 1.5) / 2.0

DONE = "done"
RESULT = "result"

BATCH_SIZE = 150
PROGRESS = 350
SNEAK_PEEK_PERCENT = 5


def render_black_hole(
        bg_file_name,
        disk_file_name,
        disk_color_shift_file_name,
        raw_out_file_name,
        glow_out_file_name,
        out_size=(320, 180),
        black_hole=(0.5, -0.28, 31.0),
        disk_angles=(-1.7, 0.0, 3.5),
        disk_radius=17.25,
        disk_rotation=123.0,
        disk_color_shift=0.8,
        field_of_view=120.0,
        horizon_z=10000.0,
        bg_scale=1.5,
        bg_shift=(0, 0),
        glow_brightness=1.14,
        glow_contrast=1.7,
        glow_blur_radius=12.0,
        glow_alpha=0.32,
        high_quality=False,
        iters=360,
        renderer_threads=3,
        sneak_peek=True
):
    renderer_threads = max(1, int(renderer_threads))

    bg_img = Image.open(bg_file_name)
    disk_img = Image.open(disk_file_name)
    disk_color_shift_img = Image.open(disk_color_shift_file_name)
    raw_out_img = Image.new("RGB", out_size, BLACK)
    glow_out_img = Image.new("RGB", out_size, BLACK)
    draw = ImageDraw.Draw(raw_out_img)

    started = time.time()

    print("Initializing")

    bg_width, bg_height = bg_img.size
    bg_canvas = (
        int(bg_width), int(bg_height), float(horizon_z),
        float(bg_width) / 2.0, float(bg_height) / 2.0
    )

    out_width, out_height = out_size
    half_out_width = float(out_width) / 2.0
    half_out_height = float(out_height) / 2.0

    focal_length = norm((float(out_width), float(out_height))) \
        / math.atan(math.radians(float(field_of_view)) / 2.0)

    bh_norm_sqr = norm_sqr(tuple(float(i) for i in black_hole))
    mbh = scale(-1.0, black_hole)

    disk_rot3 = rotation(tuple(math.radians(float(a)) for a in disk_angles))
    disk_rot3i = tuple(zip(*disk_rot3))
    # 3rd row of the disk's rotation matrix
    disk_rot3_3 = (disk_rot3[0][2], disk_rot3[1][2], disk_rot3[2][2])
    dr = math.radians(float(disk_rotation))
    disk_rot2 = (
        (math.cos(dr), math.sin(dr)), # column 1
        (-math.sin(dr), math.cos(dr)), # column 2
    )

    disk_width, disk_height = disk_img.size
    disk_width, disk_height = disk_width, disk_height
    disk_canvas = (
        int(disk_width), int(disk_height),
        1.0,
        float(disk_width) / 2.0, float(disk_height) / 2.0
    )

    weights = (0.5, 0.25, 0.25, 0.25, 0.25)
    dxdy = ((0.5, 0.5), (0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75))
    pick_color = pick_color_hq

    if not high_quality:
        weights = (1.0,)
        dxdy = ((0.5, 0.5),)
        pick_color = pick_color_lq

    renderers = []
    q = mp.Queue()
    width_per_thread = int(out_width / renderer_threads)

    for i in range(renderer_threads):
        x0 = i * width_per_thread
        w = width_per_thread if i < renderer_threads - 1 else out_width - x0
        name = "Renderer-{} ({}-{})".format(i + 1, x0, x0 + w)
        print("Starting {}".format(name))
        args = (
            name, q,
            x0, x0 + w, out_height, half_out_width, half_out_height, dxdy,
            focal_length,
            iters,
            black_hole, mbh, bh_norm_sqr,
            disk_radius, disk_rot3, disk_rot3_3, disk_rot3i, disk_rot2,
            horizon_z
        )
        r = mp.Process(args=args, target=renderer_thread)
        r.start()
        renderers.append(r)

    done_pixels = 0
    all_pixels = out_width * out_height
    next_sneak_peek = SNEAK_PEEK_PERCENT + 0.5

    while done_pixels < all_pixels:
        result = q.get()

        if result[0] == DONE:
            print("{} finished".format(result[1]))
            continue

        for x, y, rays in result[1]:
            if done_pixels % PROGRESS == 0:
                p = progress(all_pixels, started, done_pixels)

                if sneak_peek and p > next_sneak_peek:
                    next_sneak_peek = p + SNEAK_PEEK_PERCENT
                    print(
                        "Saving sneak peek image to {}".format(
                            raw_out_file_name
                        )
                    )
                    raw_out_img.save(raw_out_file_name)

            colors = collect_colors(
                rays,
                bg_img, bg_canvas, bg_scale, bg_shift,
                disk_img, disk_color_shift_img, disk_color_shift, disk_canvas,
                pick_color
            )
            draw.point((x, y), color_avg(colors, weights))
            done_pixels += 1

    print("Saving {}".format(raw_out_file_name))
    raw_out_img.save(raw_out_file_name)

    print("Rendering glow")
    glow_img = raw_out_img.copy()
    glow_img = ImageEnhance.Brightness(glow_img).enhance(glow_brightness)
    glow_img = ImageEnhance.Contrast(glow_img).enhance(glow_contrast)
    glow_img = glow_img.filter(ImageFilter.GaussianBlur(glow_blur_radius))
    glow_out_img = ImageChops.blend(
        raw_out_img,
        ImageChops.screen(raw_out_img, glow_img),
        glow_alpha
    )

    print("Saving {}".format(glow_out_file_name))
    glow_out_img.save(glow_out_file_name)

    print("Joining threads")
    for r in renderers:
        r.join()

    print("Done in {}".format(format_time(time.time() - started)))


def progress(all_pixels, started, done_pixels):
    p = (float(done_pixels) / float(all_pixels)) * 100.0
    elapsed = time.time() - started
    estimates = ""

    if done_pixels > PROGRESS * 10:
        etr = (float(elapsed) / float(done_pixels)) \
            * float(all_pixels - done_pixels)
        total = format_time(elapsed + etr)
        etr = format_time(etr)
        estimates = "\tETR: {}\t(total: {})".format(etr, total)

    elapsed = format_time(elapsed)
    print("Rendering: {:.3f}%\telapsed: {}{}".format(p, elapsed, estimates))

    return p


def collect_colors(
        rays,
        bg_img, bg_canvas, bg_scale, bg_shift,
        disk_img, disk_color_shift_img, disk_color_shift, disk_canvas,
        pick_color
):
    colors = []

    for lost, hit, disk_hits in rays:
        color = BLACK

        if lost:
            color = BLACK
        else:
            color = pick_color(
                bg_img,
                vsum(
                    to_image_float(
                        (hit[X] / bg_scale, hit[Y] / bg_scale, hit[Z]),
                        bg_canvas
                    ),
                    bg_shift
                ),
                bg_canvas
            )

        if disk_hits:
            disk_colors = []

            for dh, dcsh in disk_hits:
                dh = (
                    dh[X] * disk_canvas[3],
                    dh[Y] * disk_canvas[4],
                    disk_canvas[Z]
                )
                dcsh = (
                    dcsh[X] * disk_canvas[3],
                    dcsh[Y] * disk_canvas[4],
                    disk_canvas[Z]
                )
                dc = pick_color(
                    disk_img,
                    to_image_float(dh, disk_canvas),
                    disk_canvas
                )
                csc = pick_color(
                    disk_color_shift_img,
                    to_image_float(dcsh, disk_canvas),
                    disk_canvas
                )
                sdc = list(blend_colors(csc, dc))
                sdc[ALPHA] = dc[ALPHA]
                disk_colors.append(
                    vsum(
                        scale(1.0 - disk_color_shift, dc),
                        scale(disk_color_shift, tuple(sdc))
                    )
                )

            if len(disk_colors) == 1:
                disk_color = disk_colors[0]
            else:
                disk_color = (0, 0, 0, 0)

                while len(disk_colors) > 0:
                    dc = disk_colors.pop()
                    disk_color = blend_colors(dc, disk_color)

            color = blend_colors(disk_color, color)

        colors.append(color)

    return colors


def renderer_thread(
        name, q,
        x0, w, out_height, half_out_width, half_out_height, dxdy,
        focal_length,
        iters,
        black_hole, mbh, bh_norm_sqr,
        disk_radius, disk_rot3, disk_rot3_3, disk_rot3i, disk_rot2,
        horizon_z
):
    batch = []
    counter = 0

    for x in range(x0, w):
        ray_x = float(x) - half_out_width

        for y in range(out_height):
            rays = []

            for dx, dy in dxdy:
                ray = (
                    ray_x + dx,
                    half_out_height - float(y) + dy,
                    focal_length,
                )

                lost, hit, disk_hits = evolve(
                    iters,
                    ray,
                    black_hole, mbh, bh_norm_sqr,
                    disk_radius, disk_rot3, disk_rot3_3, disk_rot3i, disk_rot2,
                    horizon_z
                )

                rays.append((lost, hit, disk_hits))

            batch.append((x, y, tuple(rays)))
            counter += 1

            if counter == BATCH_SIZE:
                q.put((RESULT, tuple(batch)))
                batch = []
                counter = 0

    if len(batch) > 0:
        q.put((RESULT, tuple(batch)))

    q.put((DONE, name))


def evolve(
        iters,
        ray,
        black_hole, mbh, bh_norm_sqr,
        disk_radius, disk_rot3, disk_rot3_3, disk_rot3i, disk_rot2,
        horizon_z
):
    ray = scale_inv(norm(ray), ray)
    ray_norm_sqr = norm_sqr(ray)
    velocity = ray
    impact = find_impact(ray, ray_norm_sqr, black_hole, bh_norm_sqr)

    # if we rotate and translate the space so that the center of the black hole
    # and the disk is at the origin, and the disk lies horizontally in the X, Z
    # plane, then a lot of the calculations become a lot cheaper - we won't
    # loose accuracy, due to the symmetric nature of Schwarzschild black holes
    p1 = mul(disk_rot3i, mbh)
    p2 = mul(disk_rot3i, vsum(ray, mbh))
    velocity = mul(disk_rot3i, velocity)
    lost = False
    hit = None
    disk_hits = []

    for lost, point, delta in trace(iters, p2, velocity, impact):
        p1 = p2
        p2 = point
        disk_hit = find_disk_hit(
            p1, p2, delta,
            black_hole,
            disk_radius, disk_rot3_3, disk_rot2
        )

        if disk_hit is not None:
            disk_hits.append(disk_hit)

    if not lost:
        # undo the rotation and translation
        hp1 = vsum(mul(disk_rot3, p1), black_hole)
        hdelta = mul(disk_rot3, delta)

        try:
            # lengthen the ray until it reaches the horizon
            l = (horizon_z - hp1[Z]) / hdelta[Z]
        except:
            # consider sideways going rays lost
            lost = True
        else:
            hit = vsum(hp1, scale(l, hdelta))

    return lost, hit, tuple(disk_hits)


def find_impact(ray, ray_norm_sqr, black_hole, bh_norm_sqr):
    # the distance between the origin-->ray line and the black hole's center

    dot_r_bh = dot(ray, black_hole)
    distance_point_on_ray = dot_r_bh / ray_norm_sqr

    return (bh_norm_sqr - dot_r_bh * distance_point_on_ray) ** 0.5


def trace(iters, ray, velocity, impact):
    # trace the path of the ray around the black hole which is at the origin
    ray_norm_sqr = norm_sqr(ray)
    ray_norm = ray_norm_sqr ** 0.5
    delta = velocity

    # when to stop and consider the ray proceeding in a straight line
    stop = max(2.0 * ray_norm + 8.0, 25.0)
    stop_sqr = stop ** 2.0

    step = stop / float(iters)
    h_sqr = impact * SHADOW_RADIUS
    h = -1.5 * h_sqr * step

    for s in range(iters):
        lost = ray_norm_sqr < PHOTON_SPHERE_RADIUS

        yield lost, ray, delta

        if lost or ray_norm_sqr > stop_sqr:
            break

        acceleration = scale(h / (ray_norm_sqr ** 2.5), ray)
        velocity = vsum(velocity, acceleration)
        delta = scale(step, velocity)
        ray = vsum(ray, delta)
        ray_norm_sqr = norm_sqr(ray)


def find_disk_hit(
        l1, l2, delta,
        black_hole,
        disk_radius, disk_rot3_3, disk_rot2
):
    # the disk is flat on the X, Z plane, and it's centered in the origin

    if l1[Y] * l2[Y] > 0.0:
        # both points are on the same side of the disk, the line can't intersect
        return None

    if l1[Z] > disk_radius and l2[Z] > disk_radius:
        return None

    if l1[Z] < -disk_radius and l2[Z] < -disk_radius:
        return None

    # the disk's normal vector is (0, 1, 0), so dot(v, (0, 1, 0)) == v[Y]
    dot_line_disk_normal = delta[Y]
    d = -1.0

    if dot_line_disk_normal == 0.0:
        # the line and the disk are parallel: edge hit or no intersection
        # (ignoring edge hits doesn't seem to make a huge difference)
        return None
    else:
        # the line intersects the disk's plane in a single point
        # the disk's normal vector is (0, 1, 0), so dot(v, (0, 1, 0)) == v[Y]
        d = - l1[Y] / dot_line_disk_normal

    # is the intersection between the two points?
    if 0.0 <= d and d <= 1.0:
        intersection = vsum(scale(d, delta), l1)

        # the intersection's Z coordinate relative to the camera
        intersection_z = dot(disk_rot3_3, intersection)

        # we can't use the focal length here, because it's not measured in r_S,
        # so just use some sufficiently small value
        if intersection_z + black_hole[Z] < CAMERA_DEPTH:
            # hits the disk inside or behind the camera
            return None

        # the disk's center is the origin
        intersection_norm = norm(intersection)

        if 1.0 <= intersection_norm and intersection_norm <= disk_radius:
            # the disk's base in 3D is ((1, 0, 0), (0, 0, 0), (0, 0, 1))
            disk_color_shift_hit = (intersection[X], intersection[Z])
            disk_hit = mul(disk_rot2, disk_color_shift_hit)

            return scale_inv(disk_radius, disk_hit), scale_inv(disk_radius, disk_color_shift_hit)

    return None


def norm_sqr(v):
    return sum(vi * vi for vi in v)


def norm(v):
    return norm_sqr(v) ** 0.5


def dot(a, b):
    return sum(vmul(a, b))


def vmul(a, b):
    return tuple(ai * bi for ai, bi in zip(a, b))


def vsum(a, b):
    return tuple(ai + bi for ai, bi in zip(a, b))


def vminus(a, b):
    return tuple(ai - bi for ai, bi in zip(a, b))


def scale(s, v):
    return tuple(s * vi for vi in v)


def scale_inv(s, v):
    return tuple(vi / s for vi in v)


def mul(mtx, v):
    return tuple(
        sum(mji * vj for mji, vj in zip(mj, v)) for mj in zip(*mtx)
    )


def rotation(angles):
    a, b, c = angles

    sa = math.sin(a)
    sb = math.sin(b)
    sc = math.sin(c)
    ca = math.cos(a)
    cb = math.cos(b)
    cc = math.cos(c)

    return (
        (cb*cc,             cb*sc,              - sb),  # column 1
        (sa*sb*cc - ca*sc,  sa*sb*sc + ca*cc,   sa*cb), # column 2
        (ca*sb*cc + sa*sc,  ca*sb*sc - sa*cc,   ca*cb), # column 3
    )


def rotate(v, r_mtx, center):
    return vsum(mul(r_mtx, vminus(v, center)), center)


def to_canvas(v, canvas):
    s = canvas[Z] / v[Z]

    return (v[X] * s, v[Y] * s)


def to_image_float(v, canvas):
    x, y = to_canvas(v, canvas)

    return (x + canvas[3], canvas[4] - y)


def to_image(v, canvas):
    x, y = to_image_float(v, canvas)

    return (int(math.floor(x)), int(math.floor(y)))


def pick_color_hq(img, xy, canvas):
    # quick and dirty resampling, but smooth enough:
    # the pixel sized unit square at (x, y) might overlap with 4 actual pixels,
    # average those weighted by the overlapping area, but increase the weight
    # for the pixel directly under (x, y) by an empirically chosen value
    x, y = xy

    xm05, xp05 = x - 0.5, x + 0.5
    ym05, yp05 = y - 0.5, y + 0.5

    colors = (
        get_pixel(img, xm05, ym05, canvas),
        get_pixel(img, xp05, ym05, canvas),
        get_pixel(img, xm05, yp05, canvas),
        get_pixel(img, xp05, yp05, canvas),
        get_pixel(img, x, y, canvas),
    )

    xi, yi = math.floor(x), math.floor(y)
    lx1, lx2 = xi - xm05, xp05 - xi
    ly1, ly2 = yi - ym05, yp05 - yi

    areas = (lx1 * ly1, lx2 * ly1, lx1 * ly2, lx2 * ly2, 2.0)

    return color_avg(colors, areas)


def pick_color_lq(img, xy, canvas):
    x, y = xy

    return get_pixel(img, x, y, canvas)


def get_pixel(img, x, y, canvas):
    # tile the image
    x, y = int(x) % canvas[X], int(y) % canvas[Y]

    return img.getpixel((x, y))


def color_avg(colors, weights):
    s = sum(weights)
    if s == 0.0:
        return (0, 0, 0, 0)

    colors = (scale(w, c) for w, c in zip(weights, colors))

    return tuple(int(sum(c) / s) for c in zip(*colors))


def blend_colors(top, bottom):
    top_a = top[ALPHA] if len(top) > 3 else 255
    bottom_a = bottom[ALPHA] if len(bottom) > 3 else 255

    top_a_n = top_a / 255.0
    bottom_a_n = bottom_a / 255.0

    color = color_avg(
        (top[:3], bottom[:3]),
        (top_a_n, bottom_a_n * (1.0 - top_a_n))
    )
    alpha = 255.0

    if top_a != 255 and bottom_a != 255:
        alpha = int(255.0 * (top_a_n + bottom_a_n * (1.0 - top_a_n)))

    return color + (alpha,)


def format_time(seconds):
    seconds = int(seconds + 0.5)

    return "{:02}:{:02}:{:02}".format(
        int(seconds / 3600),
        int((seconds % 3600) / 60),
        int(seconds % 60)
    )


def main(argv):
    render_black_hole(
        "background.png",
        "disk.png",
        "disk_color_shift.png",
        "black_hole.png",
        "black_hole_glow.png",
        (3840, 2160),
        black_hole=(0.5, -0.28, 31.0),
        disk_angles=(-1.7, 0.0, 3.5),
        disk_radius=17.25,
        disk_rotation=123.0,
        disk_color_shift=0.8,
        field_of_view=120.0,
        horizon_z=10000.0,
        bg_scale=1.5,
        bg_shift=(0.0, 0.0),
        glow_brightness=1.14,
        glow_contrast=1.7,
        glow_blur_radius=60.0,
        glow_alpha=0.32,
        high_quality=True,
        iters=450,
        renderer_threads=11,
        sneak_peek=False
    )


main(sys.argv)
