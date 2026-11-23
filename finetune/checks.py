"""Checks on what a script did, read from its report and picture (run_sandboxed.py --own-view). Used by the mix
builder (which replay scripts to keep) and by the before/after report, so both judge a script the same way.
"""
import math
import numpy as np
from PIL import Image


def ran(rep):
    return rep.get("process") == "exit 0" and not rep.get("error")


def starting_cube_left(rep):
    """Is the cube of a new file still in the scene? Newer reports mark it exactly; older ones only know that some
    mesh is called "Cube", which is also true of a cube the script added itself."""
    if "starting_objects_left" in rep:
        return "MESH" in rep["starting_objects_left"]
    return bool(rep.get("default_cube_still_there"))


def objects_made(rep):
    """How many objects the script built. The cube of a new Blender file does not count, unless it is all there is
    and was reshaped."""
    n, cube = rep.get("n_renderable_objects", 0), starting_cube_left(rep)
    untouched = all(abs(x - 2.0) < 1e-3 for x in rep.get("bbox_size") or [0, 0, 0])
    return n - 1 if cube and (n > 1 or untouched) else n


def own_view_blank(png):
    """Is the view through the script's own camera blank? That view is the left third of the picture; blank means
    under 1% of it differs from its commonest colour (the camera points away from what was built, or nothing is lit)."""
    px = np.asarray(Image.open(png).convert("RGB")).astype(int)
    own = px[:, :px.shape[1] // 3]
    return bool((np.abs(own - np.median(own.reshape(-1, 3), axis=0)).sum(axis=2) > 24).mean() < 0.01)


def misses_scene(location, direction, half_angle, rep):
    """Does a cone from `location` along `direction` (half-angle in radians) miss the sphere around what was built?
    None if the report has no scene bounds (older reports, or nothing built)."""
    if rep.get("scene_center") is None or not location or not direction:
        return None
    to = np.array(rep["scene_center"]) - np.array(location)
    dist = float(np.linalg.norm(to))
    if dist <= rep["scene_radius"]:
        return False                                       # inside the scene
    off = math.acos(max(-1.0, min(1.0, float(np.dot(to / dist, direction)))))
    return bool(off > half_angle + math.asin(rep["scene_radius"] / dist))


def camera_misses_scene(rep):
    cam = rep.get("camera")
    if not cam or not cam.get("angle"):
        return None
    return misses_scene(cam["location"], cam["direction"], cam["angle"] / 2, rep)


def aimed_lights(rep):
    """(spot and area lights, how many of them point away from what was built). A spot points away if its cone misses
    the scene; an area light if the scene is behind it."""
    out = [misses_scene(l["location"], l.get("direction"), l["spot_size"] / 2 if l["type"] == "SPOT" else math.pi / 2, rep)
           for l in rep.get("lights", []) if l["type"] in ("SPOT", "AREA")]
    out = [x for x in out if x is not None]
    return len(out), sum(out)


def _own_view_scene(png, views):
    """Which pixels of the own-camera view are not background (the commonest colour of the view). `views` is how many
    views the picture holds side by side: 3 from run_sandboxed.py --own-view, 1 with --only-own-view."""
    px = np.asarray(Image.open(png).convert("RGB")).astype(int)
    own = px[:, :(px.shape[1] - 4 * (views - 1)) // views]     # the views are joined with a 4-pixel gap
    colours, counts = np.unique((own // 8).reshape(-1, 3), axis=0, return_counts=True)
    return np.abs(own - (colours[counts.argmax()] * 8 + 4)).sum(axis=2) > 30


def own_view_edge_share(png, views=3):
    """How much of the edge of the own-camera view is covered by the scene, from 0 to 1: the share of the outer
    three pixels all round that are not background. A scene that fits its picture scores near 0; one that is cut off
    by the frame scores well above."""
    scene = _own_view_scene(png, views)
    ring = np.ones(scene.shape, bool)
    ring[3:-3, 3:-3] = False
    return round(float(scene[ring].mean()), 3)


def own_view_fill(png, views=3):
    """How much of its own picture the scene spans, from 0 to 1: the larger of its width and its height, as a share of
    the picture's. Low means the camera is further away than it needs to be."""
    scene = _own_view_scene(png, views)
    ys, xs = np.where(scene)
    if not len(xs):
        return 0.0
    return round(float(max((xs.max() - xs.min() + 1) / scene.shape[1], (ys.max() - ys.min() + 1) / scene.shape[0])), 3)
