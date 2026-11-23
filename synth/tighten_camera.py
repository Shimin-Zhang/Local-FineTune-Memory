"""After the framing repair of wave 1 (cameras moved back so no scene is cut off), move the cameras that went further
back than needed closer again, by rewriting the one camera line the repair changed.

Usage: python synth/tighten_camera.py plan <backup dir>     # rewrite the scripts that need it, keep the repaired versions
       python synth/tighten_camera.py settle <backup dir>   # after re-running and re-checking: put back any that got worse
Between the two: run_sandboxed.py --own-view and synth/check.py on every folder that `plan` printed.

How far a scene reaches from the middle of its own picture is measured on the picture (finetune/checks.py); the
camera's offset from its aim point is scaled so that reach becomes 86% of the half-width. The line is found from git:
the repair changed exactly one line per script, and the numbers that changed on it are the offset.
"""
import json, os, re, shutil, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "finetune"))
from checks import _own_view_scene

ROOT, TARGET, NUM = "results/synth_v1", 0.86, r"-?\d+\.\d+|-?\.\d+|-?\d+"
mode, backup = sys.argv[1], sys.argv[2]
rows = [r for r in json.load(open(f"{ROOT}/edge_share_wave1.json")) if r["edge_share"] >= 0.15]


def reach(png):
    """Furthest the scene gets from the middle of the picture, as a share of the half-width (1 = touches the edge)."""
    scene = _own_view_scene(png, 3)
    ys, xs = np.where(scene)
    h, w = scene.shape
    return max(abs(xs.min() - w / 2), abs(xs.max() + 1 - w / 2)) / (w / 2), max(abs(ys.min() - h / 2), abs(ys.max() + 1 - h / 2)) / (h / 2)


def fmt(x, like):
    """Write x the way `like` was written: no decimals if it had none, else one."""
    if "." not in like:
        return str(int(round(x)))
    s = f"{x:.1f}"
    return s[:-2] if s.endswith(".0") else s.replace("0.", ".", 1) if like.lstrip("-").startswith(".") else s


if mode == "plan":
    os.makedirs(backup, exist_ok=True)
    plan, folders = {}, set()
    for r in rows:
        path = f"{ROOT}/{r['batch']}/{r['id']}.py"
        m = max(reach(path[:-3] + ".png"))
        if m >= 0.80:
            continue
        diff = subprocess.run(["git", "diff", "-U0", "--", path], capture_output=True, text=True).stdout.splitlines()
        old = [l[1:] for l in diff if l.startswith("-") and not l.startswith("---")]
        new = [l[1:] for l in diff if l.startswith("+") and not l.startswith("+++")]
        if len(old) != 1 or len(new) != 1 or re.sub(NUM, "#", old[0]) != re.sub(NUM, "#", new[0]):
            print("skip (cannot read the change):", r["id"]); continue
        a, b = re.findall(NUM, old[0]), re.findall(NUM, new[0])
        changed = [i for i in range(len(a)) if a[i] != b[i]]
        ratios = [float(b[i]) / float(a[i]) for i in changed if float(a[i])]
        if len(changed) < 2 or not ratios or max(ratios) / min(ratios) > 1.15 or min(ratios) < 1:
            print("skip (not a plain move back):", r["id"], ratios); continue
        s = max(m / TARGET, 1 / min(ratios))                # never closer than the camera was before the repair
        parts, k = re.split(NUM, new[0]), 0
        line = parts[0]
        for i, n in enumerate(b):
            line += (fmt(float(n) * s, n) if i in changed else n) + parts[i + 1]
        code = open(path).read()
        assert code.count(new[0]) == 1, r["id"]
        shutil.copy(path, f"{backup}/{r['id']}.py")
        open(path, "w").write(code.replace(new[0], line))
        for ext in (".report.json", ".png"):
            os.remove(path[:-3] + ext)
        plan[r["id"]] = {"batch": r["batch"], "reach_before": round(float(m), 3), "scale": round(float(s), 3), "moved_back_by": round(float(np.mean(ratios)), 2)}
        folders.add(f"{ROOT}/{r['batch']}")
    json.dump(plan, open(f"{backup}/plan.json", "w"), indent=1)
    print(len(plan), "scripts rewritten;", len(rows) - len(plan), "left as repaired")
    print(" ".join(sorted(folders)))
else:
    plan, back = json.load(open(f"{backup}/plan.json")), []
    for i, p in plan.items():
        path = f"{ROOT}/{p['batch']}/{i}.py"
        c = json.load(open(f"{ROOT}/{p['batch']}/checks.json"))[i]
        p.update(passes=c["pass"], edge_share=c["edge_share"], fill=c["fill"])
        if not c["pass"] or c["edge_share"] is None or c["edge_share"] >= 0.03:
            shutil.copy(f"{backup}/{i}.py", path)
            for ext in (".report.json", ".png"):
                if os.path.exists(path[:-3] + ext):
                    os.remove(path[:-3] + ext)
            p["put_back"] = True
            back.append(i)
            continue
        lines = [json.loads(l) for l in open(f"{ROOT}/{p['batch']}/manifest.jsonl") if l.strip()]
        for l in lines:
            if l["id"] == i and "then moved closer" not in l.get("framing_repair", ""):
                l["framing_repair"] = l.get("framing_repair", "") + f"; then moved closer by script (offset x{p['scale']:.2f}) because the scene had become small"
        open(f"{ROOT}/{p['batch']}/manifest.jsonl", "w").write("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in lines))
    json.dump(plan, open(f"{backup}/plan.json", "w"), indent=1)
    print(len(plan) - len(back), "kept closer;", len(back), "put back as repaired:", " ".join(back))
