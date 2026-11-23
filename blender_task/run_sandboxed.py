"""Run model-written Blender scripts in a sandbox and render each result.

Usage: python blender_task/run_sandboxed.py <dir with *.py scripts> [--timeout 240] [--legacy-colour] [--own-view] [--no-render] [--workers 1]
                                                                    [--size 384] [--samples 48] [--denoise] [--only-own-view]
For every <name>.py in the directory it writes <name>.png (two views side by side; with --own-view a third one first,
rendered with the script's own lights, background and camera) and <name>.report.json next to it. Scripts that already
have a report are skipped unless --redo is given.

The sandbox (bubblewrap): the whole filesystem is read-only except the script directory, there is no network,
and the process cannot see other processes. Blender runs headless from factory settings and renders on the CPU.
"""
import argparse, json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

BLENDER = os.path.realpath(os.path.expanduser("~/.local/bin/blender"))
HARNESS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "harness.py")


def run_one(script, timeout, legacy_colour=False, own_view=False, no_render=False, extra=(), only_own=False):
    work = os.path.dirname(os.path.abspath(script))
    base = os.path.abspath(script)[:-3]
    png, report = base + ".png", base + ".report.json"
    for f in (png, report):
        if os.path.exists(f):
            os.remove(f)
    cmd = ["bwrap", "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc", "--tmpfs", "/tmp", "--bind", work, work,
           "--unshare-net", "--unshare-pid", "--unshare-ipc", "--die-with-parent", "--new-session",
           "--dir", "/tmp/home", "--setenv", "HOME", "/tmp/home", "--chdir", work,
           BLENDER, "--background", "--factory-startup", "--python", HARNESS, "--", os.path.abspath(script), base, report]
    cmd += [flag for on, flag in ((legacy_colour, "legacy-colour"), (own_view, "own-view"), (no_render, "no-render"), (only_own, "only-own-view")) if on] + list(extra)
    t = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        status, tail = f"exit {p.returncode}", (p.stdout + p.stderr)[-600:]
    except subprocess.TimeoutExpired:
        status, tail = "timeout", ""
    views = [f"{base}.v{k}.png" for k in ((2,) if only_own else (2, 0, 1) if own_view else (0, 1))]
    if all(os.path.exists(v) for v in views):  # join the views into one picture, then drop the parts
        ims = [Image.open(v).convert("RGB") for v in views]
        sheet = Image.new("RGB", (ims[0].width * len(ims) + 4 * (len(ims) - 1), ims[0].height), (250, 250, 248))
        for j, im in enumerate(ims):
            sheet.paste(im, (j * (ims[0].width + 4), 0))
        sheet.save(png)
    for v in views:
        if os.path.exists(v):
            os.remove(v)
    rep = json.load(open(report)) if os.path.exists(report) else {}
    rep.update(process=status, seconds=round(time.time() - t, 1), image=os.path.exists(png))
    if status != "exit 0" or (not os.path.exists(png) and not no_render):
        rep["log_tail"] = tail
    json.dump(rep, open(report, "w"), indent=1)
    return rep


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--timeout", type=int, default=240)
    ap.add_argument("--legacy-colour", action="store_true", help="copy diffuse_color onto the shader, as Blender 4 and earlier showed it")
    ap.add_argument("--own-view", action="store_true"); ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--workers", type=int, default=1); ap.add_argument("--redo", action="store_true")
    ap.add_argument("--size", type=int, default=384, help="pixels per view"); ap.add_argument("--samples", type=int, default=48)
    ap.add_argument("--denoise", action="store_true", help="with --size and --samples: a cleaner picture, for showing")
    ap.add_argument("--only-own-view", action="store_true", help="with --own-view: render that view alone (the picture is then one view wide)")
    a = ap.parse_args()
    names = sorted(f for f in os.listdir(a.dir) if f.endswith(".py") and (a.redo or not os.path.exists(os.path.join(a.dir, f[:-3] + ".report.json"))))

    def go(name):
        r = run_one(os.path.join(a.dir, name), a.timeout, a.legacy_colour, a.own_view, a.no_render,
                    [f"size={a.size}", f"samples={a.samples}"] + (["denoise"] if a.denoise else []), a.only_own_view and a.own_view)
        print(f"{name:28s} {r.get('process'):9s} {r.get('seconds'):6.1f}s image={r.get('image')} objects={r.get('n_renderable_objects')} "
              f"viewport_only_materials={r.get('materials_viewport_only')} error={r.get('error')}", flush=True)

    with ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(go, names))
