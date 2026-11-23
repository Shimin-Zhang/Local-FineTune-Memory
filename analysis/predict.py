"""Predict fine-tuning memory for catalog models from coefficients measured on the RTX 4090.

Usage: python analysis/predict.py validate [--fallback]   # compare predictions with measured probes
       python analysis/predict.py budget <GiB> [tokens_per_step] [--fallback]
       python analysis/predict.py fit                      # print the fitted activation coefficients

By default the activation coefficients come from the runs with both fast kernels installed (flash-linear-attention
and causal-conv1d; probe tags ending in _k). --fallback uses the runs on the plain-PyTorch path instead, which is
what a default install of transformers gives for Qwen3.5-family models. Models without linear-attention layers
measure the same either way.

Everything here assumes gradient checkpointing and a chunked loss (the configuration that fits the most).
Coefficients and where they come from:
  - 16-bit weights: 2 bytes per parameter; 32-bit: 4 (exact).
  - 4-bit weights: 0.517 bytes per quantized parameter + 2 bytes for everything bitsandbytes leaves alone
    (measured on 0.8B-27B, within 2%).
  - LoRA rank 16 on all linear layers: 16 bytes per trainable parameter (fp32 weight, gradient, two AdamW moments).
    Trainable count is measured for the ladder models and estimated as 82 * layers * (hidden + intermediate) otherwise.
  - Full fine-tuning with stock AdamW: the peak is the larger of the optimizer step (5 parameter-sized copies)
    and the backward pass (4 copies + activations).
  - Activations: for the measured models, a straight line fitted at import time to (process memory minus the terms
    above) against tokens per step, from results/probes.jsonl. Otherwise 4 bytes * layers * hidden per token
    + 0.5 GiB. This term is rough (it is the smallest term for large models) and is the main source of error.
    The fitted line also absorbs allocator slack that grows with the step size.
  - CUDA context 0.47 GiB + allocator slack 0.4 GiB.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from export_tidy import process_peak_mib  # highest process memory of a run, MiB

G = 2 ** 30
BREAK = {r["id"]: r for r in json.load(open("catalog/param_breakdown.json"))}
CAT = {r["id"]: r for r in json.load(open("catalog/models.json"))}
KERNEL = "--fallback" not in sys.argv  # which set of measurements the activation term is fitted to
ARGS = [a for a in sys.argv[1:] if a != "--fallback"]
TRAINABLE = {"Qwen/Qwen3.5-0.8B-Base": 10.8e6, "Qwen/Qwen3.5-2B-Base": 16.8e6, "Qwen/Qwen3.5-4B-Base": 32.5e6,
             "Qwen/Qwen3.5-9B-Base": 43.3e6, "Qwen/Qwen3-14B-Base": 64.2e6, "Qwen/Qwen3.8-27B": 116.7e6}
FIXED = (0.47 + 0.40) * G


def shape(mid):
    b, c = BREAK[mid], CAT[mid]
    return b["counted_params_text"], b["bnb_quantizable_params"], c["n_layers"], c["hidden"], c.get("intermediate") or 3 * c["hidden"]


def probes(kernel):
    """Last record per distinct probe from the main probe sets, for one kernel configuration."""
    keys = ["model_id", "weights", "technique", "quant", "dtype", "amp", "grad_ckpt", "kbit_prep", "seq_len", "batch",
            "optimizer", "lora_r", "lora_targets", "steps", "loss", "loss_chunk_tokens", "tag"]
    last = {}
    for line in open("results/probes.jsonl"):
        r = json.loads(line)
        tag = str(r.get("tag"))
        if tag.startswith(("pilot", "fla_kernel")) or tag.endswith("_k") != kernel:
            continue
        last[json.dumps([r.get(k) for k in keys] + [sorted(r.get("override") or [])])] = r
    return list(last.values())


def standard(r):
    """Checkpointing + chunked loss, AdamW, rank 16, random weights from the unmodified config."""
    return (r["technique"] != "inference" and r["grad_ckpt"] == 1 and r.get("loss") == "chunked" and r["optimizer"] == "adamw"
            and r["lora_r"] == 16 and not r.get("override") and r["weights"] == "random" and r["model_id"] in BREAK)


def fit_activations(kernel):
    """Per measured model: least-squares line through (tokens, process bytes - everything predict() counts except
    activations), over the LoRA and QLoRA runs. Returns {model_id: (bytes per token, intercept bytes, n points)}."""
    pts = {}
    for r in probes(kernel):
        if standard(r) and r["status"] == "ok" and r.get("variant") in ("lora_bf16", "qlora"):
            T = r["batch"] * r["seq_len"]
            pts.setdefault(r["model_id"], set()).add((T, process_peak_mib(r) * 2 ** 20 - predict(r["model_id"], r["variant"], T, act=0.0)))
    out = {}
    for mid, v in pts.items():
        xs, ys = [p[0] for p in v], [p[1] for p in v]
        if len(set(xs)) < 2:
            continue
        n, mx, my = len(xs), sum(xs) / len(xs), sum(ys) / len(ys)
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
        out[mid] = (slope, my - slope * mx, n)
    return out


_ACT = {}


def activations(mid, tokens):
    if KERNEL not in _ACT:
        _ACT[KERNEL] = fit_activations(KERNEL)
    if mid in _ACT[KERNEL]:
        s, i, _ = _ACT[KERNEL][mid]
        return max(0.0, i + s * tokens)
    _, _, L, d, _ = shape(mid)
    return 0.5 * G + 4 * L * d * tokens


def adapters(mid):
    if mid in TRAINABLE:
        return 16 * TRAINABLE[mid]
    _, _, L, d, ff = shape(mid)
    return 16 * 82 * L * (d + ff)


def predict(mid, technique, tokens=4096, act=None):
    """Predicted GPU memory (bytes) the process holds at its peak."""
    P, Q, L, d, ff = shape(mid)
    act = activations(mid, tokens) if act is None else act
    if technique == "full_fp32":
        return max(5 * 4 * P, 4 * 4 * P + act) + FIXED
    if technique == "full_bf16":
        return max(5 * 2 * P, 4 * 2 * P + act) + FIXED
    if technique == "full_bf16_fused":  # fused AdamW has no step-time temporary
        return 4 * 2 * P + act + FIXED
    if technique == "lora_bf16":
        return 2 * P + adapters(mid) + act + FIXED
    if technique == "qlora":
        return 0.517 * Q + 2 * (P - Q) + adapters(mid) + act + FIXED
    raise ValueError(technique)


def generic_activations(mid, tokens):
    _, _, L, d, _ = shape(mid)
    return 0.5 * G + 4 * L * d * tokens


def validate():
    """Two comparisons with the measured runs. "fitted" uses the per-model activation line, which was fitted to
    these same LoRA/QLoRA runs, so it is an in-sample check. "generic" uses only the formula applied to models
    that were never measured, which is the honest estimate of the error on the rest of the catalog."""
    keep = [r for r in probes(KERNEL) if standard(r) and r.get("variant") in ("full_fp32", "full_bf16", "lora_bf16", "qlora")]
    keep.sort(key=lambda r: (shape(r["model_id"])[0], r["variant"], r["batch"] * r["seq_len"], r["batch"]))
    seen, errs, gerrs, agree, gagree, n = set(), [], [], 0, 0, 0
    print(f"Activation term fitted to the {'fast-kernel' if KERNEL else 'fallback (plain PyTorch)'} runs.\n")
    print(f"{'model':16s} {'technique':10s} {'tokens':>6s} {'measured':>9s} {'fitted':>8s} {'error':>7s} {'generic':>8s} {'error':>7s}  outcome")
    for r in keep:
        T = r["batch"] * r["seq_len"]
        k = (r["model_id"], r["variant"], T, r["batch"])
        if k in seen:
            continue
        seen.add(k)
        pred = predict(r["model_id"], r["variant"], T) / G
        gen = predict(r["model_id"], r["variant"], T, act=generic_activations(r["model_id"], T)) / G
        free = (r["gpu_total_bytes"] / G) - (r["gpu_used_before_mib"] / 1024) if r.get("gpu_total_bytes") else 21.8
        n += 1
        name = r["model_id"].split("/")[-1].replace("-Base", "")[:16]
        if r["status"] == "ok":
            meas = process_peak_mib(r) / 1024
            errs.append((pred - meas) / meas)
            gerrs.append((gen - meas) / meas)
            agree += pred <= free
            gagree += gen <= free
            print(f"{name:16s} {r['variant']:10s} {T:6d} {meas:9.2f} {pred:8.2f} {100 * (pred - meas) / meas:+6.1f}% {gen:8.2f} {100 * (gen - meas) / meas:+6.1f}%  fit{'' if pred <= free else ', fitted says NO FIT'}{'' if gen <= free else ', generic says NO FIT'}")
        else:
            agree += pred > free
            gagree += gen > free
            print(f"{name:16s} {r['variant']:10s} {T:6d} {'oom':>9s} {pred:8.2f} {'':>7s} {gen:8.2f} {'':>7s}  no fit (free {free:.1f}){'' if pred > free else ', fitted says FIT'}{'' if gen > free else ', generic says FIT'}")
    for label, e, ag in (("fitted ", errs, agree), ("generic", gerrs, gagree)):
        a = sorted(abs(x) for x in e)
        print(f"\n{label}: {len(e)} completed runs, median absolute error {100 * a[len(a) // 2]:.1f}%, worst {100 * a[-1]:.1f}%, "
              f"mean signed {100 * sum(e) / len(e):+.1f}%; fit / no-fit outcome right for {ag} of {n} runs", end="")
    print()


def fit():
    for kernel in (True, False):
        print(f"{'fast kernels' if kernel else 'fallback (plain PyTorch)'}: activation memory, checkpointing + chunked loss")
        print(f"   {'model':16s} {'MiB per token':>14s} {'intercept GiB':>14s} {'points':>7s} {'generic formula MiB per token':>30s}")
        for mid, (s, i, npts) in sorted(fit_activations(kernel).items(), key=lambda x: shape(x[0])[0]):
            _, _, L, d, _ = shape(mid)
            print(f"   {mid.split('/')[-1].replace('-Base', ''):16s} {s / 2 ** 20:14.3f} {i / G:+14.2f} {npts:7d} {4 * L * d / 2 ** 20:30.3f}")
        print()


def budget(gib, tokens):
    print(f"Budget {gib} GiB, {tokens} tokens per step, checkpointing + chunked loss, "
          f"{'fast kernels' if KERNEL else 'fallback path'} for Qwen3.5-family models. Predicted GiB per model.\n")
    names = {"full_fp32": "Full, 32-bit", "full_bf16": "Full, 16-bit", "full_bf16_fused": "Full, 16-bit, fused AdamW",
             "lora_bf16": "LoRA, 16-bit base", "qlora": "QLoRA (bitsandbytes)"}
    ok = [m for m in BREAK if BREAK[m]["status"] == "ok" and CAT[m].get("n_layers") and CAT[m].get("hidden")]
    for t, label in names.items():
        preds = sorted(((predict(m, t, tokens) / G, m) for m in ok), key=lambda x: x[0])
        fits = [(g, m) for g, m in preds if g <= gib]
        nofit = [(g, m) for g, m in preds if g > gib]
        best = sorted(fits, key=lambda x: -BREAK[x[1]]["counted_params_text"])[:4]
        nxt = sorted(nofit, key=lambda x: BREAK[x[1]]["counted_params_text"])[:2]
        print(f"{label}")
        for g, m in best:
            b = BREAK[m]
            print(f"   fits    {m:48s} {b['counted_params_text'] / 1e9:6.1f}B  {g:6.1f} GiB{'  (MoE: experts stay 16-bit)' if b.get('moe') and t == 'qlora' else ''}")
        for g, m in nxt:
            b = BREAK[m]
            print(f"   too big {m:48s} {b['counted_params_text'] / 1e9:6.1f}B  {g:6.1f} GiB{'  (MoE: experts stay 16-bit)' if b.get('moe') and t == 'qlora' else ''}")
        print()


if __name__ == "__main__":
    if ARGS[0] == "validate":
        validate()
    elif ARGS[0] == "fit":
        fit()
    else:
        budget(float(ARGS[1]), int(ARGS[2]) if len(ARGS) > 2 else 4096)
