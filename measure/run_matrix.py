"""Run a named set of memory probes one after another, each in its own process.

Usage: python measure/run_matrix.py <matrix> [--out results/probes.jsonl] [--timeout 2400] [--dry]

Probes already present in the output (same arguments and tag) are skipped, so a run can be resumed.
One probe at a time: the GPU must not be shared while measuring.
"""
import argparse, json, os, subprocess, sys, time

CFG = "catalog/configs/{}.json"
MODELS = {  # short name -> (hub id, config file stem, text-only parameter count in billions, approximate)
    "q35_08": ("Qwen/Qwen3.5-0.8B-Base", "Qwen__Qwen3.5-0.8B-Base"),
    "q35_2": ("Qwen/Qwen3.5-2B-Base", "Qwen__Qwen3.5-2B-Base"),
    "q35_4": ("Qwen/Qwen3.5-4B-Base", "Qwen__Qwen3.5-4B-Base"),
    "q35_9": ("Qwen/Qwen3.5-9B-Base", "Qwen__Qwen3.5-9B-Base"),
    "q3_14": ("Qwen/Qwen3-14B-Base", "Qwen__Qwen3-14B-Base"),
    "q38_27": ("Qwen/Qwen3.8-27B", "Qwen__Qwen3.8-27B"),
    "nb_33": ("Nanbeige/Nanbeige4.3-33B-Base", "Nanbeige__Nanbeige4.3-33B-Base"),
}
LADDER = ["q35_08", "q35_2", "q35_4", "q35_9", "q3_14", "q38_27", "nb_33"]

# technique variants: name -> probe arguments
VARIANTS = {
    "full_fp32": dict(technique="full", quant="none", dtype="fp32", amp="none"),
    "full_fp32_amp": dict(technique="full", quant="none", dtype="fp32", amp="bf16"),
    "full_bf16": dict(technique="full", quant="none", dtype="bf16", amp="bf16"),
    "lora_bf16": dict(technique="lora", quant="none", dtype="bf16", amp="bf16"),
    "qlora": dict(technique="lora", quant="nf4", dtype="bf16", amp="bf16", kbit_prep=0),
    "qlora_kbitprep": dict(technique="lora", quant="nf4", dtype="bf16", amp="bf16", kbit_prep=1),
}
STD = dict(batch=2, seq_len=2048)  # 4,096 tokens per step


def probe(model, variant=None, **kw):
    mid, stem = MODELS[model]
    d = dict(model_id=mid, config=CFG.format(stem), weights="random", technique="full", quant="none", dtype="bf16",
             amp="none", grad_ckpt=0, kbit_prep=0, seq_len=2048, batch=2, optimizer="adamw", lora_r=16,
             lora_targets="all-linear", steps=3, loss="vanilla", loss_chunk_tokens=128, override=[], device="cuda")
    if variant:
        d.update(VARIANTS[variant])
        d["variant"] = variant
    d.update(kw)
    return d


def matrix(name):
    out = []
    if name == "pilot":  # smallest model, every technique, small then standard shape
        for v in VARIANTS:
            for ck in (0, 1):
                out.append(probe("q35_08", v, grad_ckpt=ck, batch=1, seq_len=512))
        for v in VARIANTS:
            for ck in (0, 1):
                out.append(probe("q35_08", v, grad_ckpt=ck, **STD))
        out.append(probe("q35_08", technique="inference", dtype="bf16", batch=1, seq_len=2048))
        out.append(probe("q35_08", technique="inference", quant="nf4", batch=1, seq_len=2048))
    elif name == "loss_check":  # chunked loss must give the same loss and gradients as the stock one
        for v in ("lora_bf16", "full_bf16", "qlora"):
            for ck in (0, 1):
                for ls in ("vanilla", "chunked"):
                    out.append(probe("q35_08", v, grad_ckpt=ck, batch=2, seq_len=256, loss=ls))
    elif name == "validate_random":  # real weights vs random weights, same settings
        real = ".models/Qwen3.5-0.8B-Base"
        for w in (real, "random"):  # both sides run here so they share shapes, seeds and code version
            for v in ("full_bf16", "lora_bf16", "qlora"):
                for ck, bsz, sl, ls in ((0, 1, 512, "vanilla"), (1, 1, 512, "vanilla"), (1, 2, 2048, "vanilla"), (1, 2, 2048, "chunked")):
                    out.append(probe("q35_08", v, weights=w, grad_ckpt=ck, batch=bsz, seq_len=sl, loss=ls))
            out.append(probe("q35_08", technique="inference", dtype="bf16", batch=1, seq_len=2048, weights=w))
            out.append(probe("q35_08", technique="inference", quant="nf4", batch=1, seq_len=2048, weights=w))
    elif name == "ladder":  # every model x every technique at the standard shape
        for m in LADDER:
            for v in VARIANTS:
                for ck in (0, 1):
                    for ls in ("vanilla", "chunked"):
                        out.append(probe(m, v, grad_ckpt=ck, loss=ls, loss_chunk_tokens=64 if ls == "chunked" else 128, **STD))
    elif name == "ladder_small_shape":  # same, at 1 x 1024, to see what a smaller step buys
        for m in LADDER:
            for v in ("lora_bf16", "qlora"):
                for ck in (0, 1):
                    for ls in ("vanilla", "chunked"):
                        out.append(probe(m, v, grad_ckpt=ck, batch=1, seq_len=1024, loss=ls,
                                         loss_chunk_tokens=64 if ls == "chunked" else 128))
    elif name == "tokens":  # memory against tokens per step
        for m, v in (("q35_2", "lora_bf16"), ("q35_9", "qlora")):
            for ck in (0, 1):
                for ls in ("vanilla", "chunked"):
                    for s in (512, 1024, 2048, 4096, 8192, 16384, 32768):
                        out.append(probe(m, v, grad_ckpt=ck, batch=1, seq_len=s, loss=ls,
                                         loss_chunk_tokens=64 if ls == "chunked" else 128))
        for b, s in ((8, 512), (4, 1024), (1, 4096)):  # same 4,096 tokens, different split
            out.append(probe("q35_2", "lora_bf16", batch=b, seq_len=s))
    elif name == "anchor_tokens":  # how many tokens per step fit when fine-tuning the model you run
        for ck in (1, 0):
            for ls in ("chunked", "vanilla"):
                for sl in (256, 512, 1024, 1536, 2048, 3072, 4096):
                    out.append(probe("q38_27", "qlora", grad_ckpt=ck, batch=1, seq_len=sl, loss=ls,
                                     loss_chunk_tokens=64 if ls == "chunked" else 128))
    elif name == "anchor_edge":  # the 27B fails at 2,048 tokens by a small margin: which small levers get it over?
        base = dict(grad_ckpt=1, batch=1, seq_len=2048, loss="chunked", loss_chunk_tokens=64)
        for r in (8, 4):
            out.append(probe("q38_27", "qlora", lora_r=r, **base))
        for o in ("sgd", "adamw8bit", "adamw_fused"):
            out.append(probe("q38_27", "qlora", optimizer=o, **base))
        out.append(probe("q38_27", "qlora", lora_r=4, optimizer="sgd", **base))
    elif name == "fla_kernel":  # same settings as earlier probes, re-run with flash-linear-attention installed
        fit = dict(grad_ckpt=1, loss="chunked", loss_chunk_tokens=64)
        out.append(probe("q35_08", "full_bf16", **fit, **STD))
        out.append(probe("q35_2", "lora_bf16", **fit, **STD))
        out.append(probe("q35_2", "lora_bf16", grad_ckpt=0, loss="chunked", loss_chunk_tokens=64, batch=1, seq_len=2048))
        out.append(probe("q35_9", "qlora", **fit, **STD))
        out.append(probe("q35_9", "qlora", batch=1, seq_len=8192, **fit))
        for sl in (1024, 1536, 2048, 3072):
            out.append(probe("q38_27", "qlora", batch=1, seq_len=sl, **fit))
        out.append(probe("q35_9", technique="inference", quant="nf4", dtype="bf16", batch=1, seq_len=8192))
        out.append(probe("q38_27", technique="inference", quant="nf4", dtype="bf16", batch=1, seq_len=8192))
    elif name == "fla_kernel_warm":  # the same probes again once the compiled kernels are cached
        out = matrix("fla_kernel")
    elif name == "vocab":  # isolate the logits term by shrinking the vocabulary
        for ov in (["vocab_size=32000"], ["vocab_size=128000"], []):  # [] = the real 248,320
            for ck in (0, 1):
                out.append(probe("q35_2", "lora_bf16", grad_ckpt=ck, override=ov, batch=1, seq_len=512))
            out.append(probe("q35_2", "lora_bf16", grad_ckpt=1, override=ov, **STD))
    elif name == "optimizers":  # optimizer choice under full fine-tuning and under LoRA
        fit = dict(grad_ckpt=1, loss="chunked", loss_chunk_tokens=64, **STD)  # a configuration that fits, so the optimizer is what varies
        for o in ("adamw", "adamw_fused", "sgd", "sgd_momentum", "adamw8bit"):
            out.append(probe("q35_08", "full_bf16", optimizer=o, **fit))
            out.append(probe("q35_08", "lora_bf16", optimizer=o, **fit))
            out.append(probe("q35_2", "full_bf16", optimizer=o, **fit))
    elif name == "lora_rank":
        fit = dict(grad_ckpt=1, loss="chunked", loss_chunk_tokens=64, **STD)
        for r in (4, 8, 16, 64, 256):
            out.append(probe("q35_2", "lora_bf16", lora_r=r, **fit))
            out.append(probe("q35_9", "qlora", lora_r=r, **fit))
    elif name == "inference":  # PyTorch inference: weights and KV cache per token
        for m in LADDER:
            for q in ("none", "nf4"):
                for s in (2048, 8192, 32768):
                    out.append(probe(m, technique="inference", quant=q, dtype="bf16", batch=1, seq_len=s))
    else:
        raise SystemExit(f"unknown matrix {name}")
    for d in out:
        d["tag"] = name
    return out


KEY = ["model_id", "weights", "technique", "quant", "dtype", "amp", "grad_ckpt", "kbit_prep", "seq_len", "batch",
       "optimizer", "lora_r", "lora_targets", "steps", "tag"]
DEFAULTS = {"loss": "vanilla", "loss_chunk_tokens": 128}  # fields added after the pilot; older records imply these


def key(d):
    return json.dumps([d.get(k) for k in KEY] + [d.get(k, v) for k, v in DEFAULTS.items()] + [sorted(d.get("override") or [])])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("matrix")
    ap.add_argument("--out", default="results/probes.jsonl")
    ap.add_argument("--timeout", type=int, default=2400)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--only-models", default="", help="comma-separated short names (see MODELS) to restrict a matrix")
    ap.add_argument("--tag-suffix", default="", help="appended to the tag, e.g. _k for runs with the fast kernels installed")
    a = ap.parse_args()
    todo = matrix(a.matrix)
    for d in todo:
        d["tag"] += a.tag_suffix
    if a.only_models:
        keep = {MODELS[m][0] for m in a.only_models.split(",")}
        todo = [d for d in todo if d["model_id"] in keep]
    done = set()
    if os.path.exists(a.out):
        for line in open(a.out):
            try:
                j = json.loads(line)
                if j.get("status") in ("ok", "oom"):  # errors, crashes and timeouts are retried
                    done.add(key(j))
            except Exception:
                pass
    print(f"matrix {a.matrix}: {len(todo)} probes, {sum(key(d) in done for d in todo)} already done", flush=True)
    for i, d in enumerate(todo):
        if key(d) in done:
            continue
        argv = [sys.executable, "-I", "measure/probe.py", "--out", a.out]
        for k, v in d.items():
            if k == "override":
                for ov in v:
                    argv += ["--override", ov]
                continue
            argv += ["--" + k.replace("_", "-"), str(v)]
        label = f"[{i + 1}/{len(todo)}] {d['model_id'].split('/')[-1]} {d.get('variant', d['technique'] + ('+nf4' if d['quant'] == 'nf4' else ''))} ckpt={d['grad_ckpt']} {d['batch']}x{d['seq_len']} loss={d['loss']} {' '.join(d['override'])}"
        if a.dry:
            print(label)
            continue
        # A run that compiles Triton kernels for the first time holds ~1.6 GiB extra GPU memory outside PyTorch,
        # which is not representative and can cause a false out-of-memory near the limit. Such a run is repeated
        # (the compiled kernels are cached by then); the later record wins when the data is exported.
        for attempt in range(3):
            t = time.time()
            n_before = sum(1 for _ in open(a.out)) if os.path.exists(a.out) else 0
            try:
                r = subprocess.run(argv, capture_output=True, text=True, timeout=a.timeout)
                tail = (r.stdout.strip().splitlines() or [""])[-1]
                status = "exit %d" % r.returncode
            except subprocess.TimeoutExpired:
                tail, status = "", "timeout"
            n_after = sum(1 for _ in open(a.out)) if os.path.exists(a.out) else 0
            cold = False
            if n_after == n_before:  # the probe died without writing its record
                rec = dict(d, status="crashed" if status != "timeout" else "timeout", phase="unknown",
                           wall_seconds=round(time.time() - t, 1), error=(r.stderr[-1500:] if status != "timeout" else "timeout"))
                with open(a.out, "a") as f:
                    f.write(json.dumps(rec) + "\n")
                print(label, "->", rec["status"], flush=True)
            else:
                try:
                    j = json.loads(tail)
                    pk = j.get("peak_allocated_overall")
                    ov = j.get("non_torch_overhead_mib")
                    cold = ov is not None and ov > 550  # normal is 462-472 MiB; partial compiles were seen at 624 and 968
                    print(label, "->", j["status"], f"(phase {j['phase']})" if j["status"] != "ok" else "",
                          f"peak {pk / 2 ** 30:.2f} GiB" if pk else "", f"{j['wall_seconds']}s",
                          "[cold kernel compile, repeating]" if cold and attempt < 2 else "", flush=True)
                except Exception:
                    print(label, "->", status, flush=True)
            if not cold:
                break
            time.sleep(2)
        time.sleep(2)  # let the driver release memory before the next probe


if __name__ == "__main__":
    main()
