"""Turn the written scenes into the trainer's files: one {"id", "kind", "system", "user", "assistant"} line per scene.

Usage: python synth/build_train.py [--out results/finetune_v3] [--tokenizer .models/Qwen3.8-27B]
Reads the batch lists results/synth_v1/batches_wave1.json and batches_wave2.json. Scenes in train_b* folders go to
train.jsonl, scenes in test_b* folders to val.jsonl (held out: never trained on, used for the validation loss and as
the requests of the before/after test). Only scenes that pass synth/check.py (their batch's checks.json) are taken.
Prints the token counts as the trainer will see them (prompt + reply + end marker).
"""
import argparse, json, os, statistics
from transformers import AutoTokenizer

ap = argparse.ArgumentParser()
ap.add_argument("--out", default="results/finetune_v3"); ap.add_argument("--tokenizer", default=".models/Qwen3.8-27B")
a = ap.parse_args()
SYSTEM = ("You control Blender 5.2 through a tool that runs Python. Reply with one Python code block that uses bpy to do what the user asks. "
          "No explanation.")                              # the bare prompt of blender_task/system_prompts.json, so the 50 everyday requests stay comparable
dirs = [d for f in ("batches_wave1.json", "batches_wave2.json") for d in json.load(open(os.path.join("results/synth_v1", f)))]
sets, skipped = {"train": [], "val": []}, []
for d in dirs:
    which = "train" if os.path.basename(d).startswith("train_") else "val"
    checks = json.load(open(os.path.join(d, "checks.json")))
    for r in json.load(open(os.path.join(d, "requests.json"))):
        if not checks.get(r["id"], {}).get("pass"):
            skipped.append(r["id"])
            continue
        code = open(os.path.join(d, r["id"] + ".py")).read()
        sets[which].append({"id": r["id"], "kind": "scene", "category": r["category"], "system": SYSTEM, "user": r["request"],
                            "assistant": "```python\n" + code.rstrip() + "\n```"})
os.makedirs(a.out, exist_ok=True)
tok = AutoTokenizer.from_pretrained(a.tokenizer)
for which, rows in sets.items():
    rows.sort(key=lambda r: r["id"])
    with open(os.path.join(a.out, which + ".jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    n = [len(tok(f"<|im_start|>system\n{r['system']}<|im_end|>\n<|im_start|>user\n{r['user']}<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
                 + r["assistant"] + "<|im_end|>", add_special_tokens=False).input_ids) for r in rows]
    print(f"{which}: {len(rows)} scenes, {sum(n):,} tokens, median {statistics.median(n):.0f}, longest {max(n)}, over 3,700: {sum(x > 3700 for x in n)}")
print("left out (not passing the checker):", skipped)
