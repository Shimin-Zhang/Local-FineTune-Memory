"""Build the Hugging Face dataset of the scene scripts locally: two Parquet files and the dataset card. Nothing is uploaded.

Usage: python -I synth/build_hf_dataset.py [--out results/hf_dataset] [--quality 90]

One row per scene. Scenes in train_b* folders go to the train split (2,000), scenes in test_b* folders to the test split
(100; their main subjects appear in no training request). Only scenes that pass synth/check.py (their batch's
checks.json) are taken. Reads the batch lists in results/synth_v1, the request lists in synth/requests, the writers'
manifests, the first versions in first/, and the clean 640-pixel renders in results/synth_v1/show/ (stored as JPEG).
The `messages` column is built exactly as synth/build_train.py builds the training examples. The card is
synth/hf_card.md with its {placeholders} filled from the data.
"""
import argparse, io, json, os, statistics, sys

from PIL import Image as PILImage
from datasets import Dataset, Features, Image, List, Value

ap = argparse.ArgumentParser()
ap.add_argument("--out", default="results/hf_dataset"); ap.add_argument("--quality", type=int, default=90)
ap.add_argument("--repo-id", default="ShiminZ/blender-lowpoly-dioramas", help="only used in the card's loading example")
a = ap.parse_args()

B = "results/synth_v1"
SYSTEM = ("You control Blender 5.2 through a tool that runs Python. Reply with one Python code block that uses bpy to do what the user asks. "
          "No explanation.")
assert SYSTEM == json.load(open("blender_task/system_prompts.json"))["bare"], "system prompt differs from the one run 3 trained on"

requests = {}
for split in ("train", "test"):
    for line in open(f"synth/requests/{split}.jsonl"):
        r = json.loads(line)
        requests[r["id"]] = r

FEATURES = Features({
    "id": Value("string"), "category": Value("string"), "subject": Value("string"), "setting": Value("string"),
    "instruction": Value("string"), "script": Value("string"),
    "messages": List({"role": Value("string"), "content": Value("string")}),
    "image": Image(),
    "script_tokens": Value("int32"), "script_lines": Value("int32"), "n_objects": Value("int32"),
    "n_materials": Value("int32"), "n_lights": Value("int32"), "render_engine": Value("string"), "blender_version": Value("string"),
    "writer_rating": Value("int32"), "writer_note": Value("string"), "first_run": Value("string"), "revisions": Value("int32"),
    "fixes": List(Value("string")), "framing_repair": Value("string"), "first_script": Value("string"),
})

dirs = [d for f in ("batches_wave1.json", "batches_wave2.json") for d in json.load(open(os.path.join(B, f)))]
splits, skipped, jpeg_bytes = {"train": [], "test": []}, [], 0
for d in dirs:
    name = os.path.basename(d)
    split = "train" if name.startswith("train_") else "test"
    checks = json.load(open(os.path.join(d, "checks.json")))
    manifest = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(d, "manifest.jsonl"))}
    for rq in json.load(open(os.path.join(d, "requests.json"))):
        i = rq["id"]
        c = checks.get(i, {})
        if not c.get("pass"):
            skipped.append(i)
            continue
        req, man = requests[i], manifest[i]
        assert req["request"] == rq["request"], i
        code = open(os.path.join(d, i + ".py")).read()
        rep = json.load(open(os.path.join(d, i + ".report.json")))
        first = os.path.join(d, "first", i + ".py")
        buf = io.BytesIO()
        PILImage.open(os.path.join(B, "show", name, i + ".png")).convert("RGB").save(buf, "JPEG", quality=a.quality, optimize=True)
        jpeg_bytes += buf.tell()
        splits[split].append({
            "id": i, "category": req["category"], "subject": req["head"], "setting": req["setting"],
            "instruction": req["request"], "script": code,
            "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": req["request"]},
                         {"role": "assistant", "content": "```python\n" + code.rstrip() + "\n```"}],
            "image": {"bytes": buf.getvalue(), "path": i + ".jpg"},
            "script_tokens": c["tokens"], "script_lines": c["lines"], "n_objects": c["objects"], "n_materials": c["materials"],
            "n_lights": c["lights"], "render_engine": rep["render_engine"], "blender_version": rep["blender"],
            "writer_rating": man.get("picture"), "writer_note": man.get("note"), "first_run": man.get("first_run"),
            "revisions": man.get("rounds"), "fixes": man.get("fixes") or [], "framing_repair": man.get("framing_repair"),
            "first_script": open(first).read() if os.path.exists(first) else None,
        })

os.makedirs(os.path.join(a.out, "data"), exist_ok=True)
stats = {}
for split, rows in splits.items():
    rows.sort(key=lambda r: r["id"])
    Dataset.from_list(rows, features=FEATURES).to_parquet(os.path.join(a.out, "data", f"{split}-00000-of-00001.parquet"))
    stats[split] = rows
print(f"train {len(splits['train'])}, test {len(splits['test'])}, left out (not passing the checker): {skipped}")
print(f"JPEG renders: {jpeg_bytes / 2**20:.0f} MiB at quality {a.quality}")

allrows = splits["train"] + splits["test"]
med = lambda k, rs=allrows: f"{statistics.median(r[k] for r in rs):,.0f}"
ratings = {k: sum(r["writer_rating"] == k for r in allrows) for k in range(1, 6)}
fill = {
    "repo_id": a.repo_id, "n_train": f"{len(splits['train']):,}", "n_test": f"{len(splits['test']):,}", "n_all": f"{len(allrows):,}",
    "n_categories": len({r["category"] for r in allrows}),
    "med_tokens": med("script_tokens"), "min_tokens": f"{min(r['script_tokens'] for r in allrows):,}",
    "max_tokens": f"{max(r['script_tokens'] for r in allrows):,}", "sum_tokens": f"{sum(r['script_tokens'] for r in allrows) / 1e6:.2f}M",
    "med_lines": med("script_lines"), "med_objects": med("n_objects"),
    "min_objects": min(r["n_objects"] for r in allrows), "max_objects": max(r["n_objects"] for r in allrows),
    "med_materials": med("n_materials"), "med_lights": med("n_lights"),
    "first_ok": sum(r["first_run"] == "ok" for r in allrows), "no_first": sum(r["first_script"] is None for r in allrows),
    **{f"rating_{k}": v for k, v in ratings.items()},
    "revised_0": sum(r["revisions"] == 0 for r in allrows),
    "framing_repaired": sum(bool(r["framing_repair"]) for r in allrows),
}
fill = {k: (f"{v:,}" if isinstance(v, int) else v) for k, v in fill.items()}   # every count with thousands separators
card = open("synth/hf_card.md").read().format(**fill)
open(os.path.join(a.out, "README.md"), "w").write(card)
json.dump(fill, open(os.path.join(a.out, "card_numbers.json"), "w"), indent=1)
print("card written:", os.path.join(a.out, "README.md"))
