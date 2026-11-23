"""Check a folder of written scripts against the rules in synth/guide.md, after run_sandboxed.py --own-view has run them.

Usage: python synth/check.py <dir> [--max-tokens 3300] [--tokenizer .models/Qwen3.8-27B]
Prints one line per script and writes <dir>/checks.json. A script passes when every hard rule holds; warnings do not fail it.
"""
import argparse, glob, json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "finetune"))
from checks import ran, objects_made, own_view_blank, camera_misses_scene, aimed_lights, starting_cube_left, own_view_edge_share, own_view_fill
from PIL import Image
from transformers import AutoTokenizer

ap = argparse.ArgumentParser()
ap.add_argument("dir"); ap.add_argument("--max-tokens", type=int, default=3300); ap.add_argument("--tokenizer", default=".models/Qwen3.8-27B")
ap.add_argument("--max-edge", type=float, default=0.15, help="fail when more than this share of the own view's edge is covered by the scene")
a = ap.parse_args()
tok = AutoTokenizer.from_pretrained(a.tokenizer)
FORBIDDEN = r"\bopen\(|bpy\.ops\.wm\.|bpy\.ops\.render\.|bpy\.ops\.preferences|\bimport (os|sys|subprocess|socket|urllib|requests|shutil|pathlib)\b|bpy\.data\.images\.load|filepath"
out = {}
for f in sorted(glob.glob(os.path.join(a.dir, "*.py"))):
    name, base, code = os.path.basename(f)[:-3], f[:-3], open(f).read()
    rep = json.load(open(base + ".report.json")) if os.path.exists(base + ".report.json") else None
    tokens = len(tok("```python\n" + code.rstrip() + "\n```", add_special_tokens=False).input_ids)
    fails, warns, edge, fill = [], [], None, None
    if rep is None:
        fails.append("not run yet")
    else:
        if not ran(rep):
            fails.append("error: " + (rep.get("error") or rep.get("process") or "?")[:140] + (f"  [line: {rep['error_line']}]" if rep.get("error_line") else ""))
        else:
            if not objects_made(rep):
                fails.append("built no object")
            if starting_cube_left(rep):
                fails.append("Blender's starting cube is still in the scene")
            if rep.get("materials_viewport_only"):
                fails.append("a colour was set where the render ignores it (diffuse_color)")
            if rep.get("objects_without_material"):
                fails.append(f"{rep['objects_without_material']} object(s) have no material")
            if not rep.get("script_set_camera"):
                fails.append("no camera of its own")
            elif camera_misses_scene(rep) or (os.path.exists(base + ".png") and own_view_blank(base + ".png")):
                fails.append("its own camera does not show the scene (points away, or the view is blank or unlit)")
            n, astray = aimed_lights(rep)
            if astray:
                fails.append(f"{astray} spot or area light(s) point away from the scene")
            if not os.path.exists(base + ".png"):
                fails.append("no picture was rendered")
            else:                                          # does the scene fit its own picture?
                w, h = Image.open(base + ".png").size
                edge = own_view_edge_share(base + ".png", 3 if w > 2 * h else 1)
                if edge >= a.max_edge:
                    fails.append(f"cut off by the picture's edge: the scene covers {edge:.0%} of the edge of its own view (limit {a.max_edge:.0%}); "
                                 "move the camera back, or pull in whatever reaches past the base")
                elif edge >= 0.05:
                    warns.append(f"the scene touches the edge of its own view ({edge:.0%} of it)")
                fill = own_view_fill(base + ".png", 3 if w > 2 * h else 1)
                if fill < 0.75:
                    warns.append(f"the scene is small in its own view (it spans {fill:.0%} of the picture); move the camera closer")
            if not rep.get("lights"):
                warns.append("no light object (fine only if the scene is lit by glowing materials or the background)")
            if any(t == "TEX_IMAGE" for m in rep.get("materials", []) for t in m.get("node_types", [])):
                fails.append("uses an image texture")
    if tokens > a.max_tokens:
        fails.append(f"too long: {tokens} tokens (limit {a.max_tokens})")
    bad = sorted(set(m.group(0) for m in re.finditer(FORBIDDEN, code)))
    if bad:
        fails.append("forbidden in a script: " + ", ".join(bad))
    out[name] = {"pass": not fails, "tokens": tokens, "lines": len(code.strip().splitlines()), "objects": objects_made(rep) if rep else None,
                 "materials": len(rep.get("materials", [])) if rep else None, "lights": len(rep.get("lights", [])) if rep else None, "edge_share": edge, "fill": fill,
                 "fails": fails, "warnings": warns}
    print(f"{name:12s} {'PASS' if not fails else 'FAIL'}  {tokens:5d} tokens  objects={out[name]['objects']}  " + "; ".join(fails + ["(warning) " + w for w in warns]))
json.dump(out, open(os.path.join(a.dir, "checks.json"), "w"), indent=1)
print(f"{sum(v['pass'] for v in out.values())} of {len(out)} pass")
