"""Flatten results/probes.jsonl into one row per probe for charting.

Usage: python analysis/export_tidy.py results/probes.jsonl results/probes_tidy.csv
All memory columns are raw bytes. Divide by 2**30 for GiB (the unit in which the card is "24 GB").
If a probe was run more than once with identical settings, the last record wins.

Which column to chart: process_peak_bytes is what the process held at its highest point (PyTorch's peak reserved
memory plus what the process holds outside PyTorch: CUDA context, kernels). It equals process_bytes_at_end in all
but a handful of runs, where the allocator handed memory back after the peak. peak_allocated_overall_bytes is the
memory PyTorch actually had in use; the gap between the two is allocator slack (median about 0.4 GiB, above 2 GiB
in some full fine-tuning runs). kernels says which optional kernels were installed for the Qwen3.5-family layers:
"fla+causal_conv1d" (both), "fla" (flash-linear-attention only) or "fallback" (plain PyTorch). Models without
linear-attention layers (Qwen3-14B, Nanbeige4.3) are unaffected by it.
"""
import csv, json, sys

KEYS = ["model_id", "weights", "technique", "quant", "dtype", "amp", "grad_ckpt", "kbit_prep", "seq_len", "batch",
        "optimizer", "lora_r", "lora_targets", "steps", "loss", "loss_chunk_tokens", "tag"]
COLS = ["tag", "model_id", "variant", "technique", "quant", "dtype", "amp", "grad_ckpt", "kbit_prep", "loss",
        "loss_chunk_tokens", "batch", "seq_len", "tokens_per_step", "optimizer", "lora_r", "weights_source", "override",
        "status", "fail_phase", "n_layers", "hidden_size", "vocab_size", "n_full_attention_layers",
        "params_stored_bytes", "embedding_bytes", "output_head_bytes", "quantized_4bit_bytes", "tied_embeddings",
        "trainable_params", "weights_and_adapters_bytes", "grad_bytes", "optimizer_state_bytes",
        "forward_peak_over_base_bytes", "backward_peak_over_base_bytes", "optimizer_peak_over_base_bytes",
        "retained_after_forward_bytes", "steady_state_peak_bytes", "first_step_peak_bytes", "peak_phase",
        "peak_allocated_overall_bytes", "peak_reserved_overall_bytes", "process_bytes_at_end", "process_peak_bytes",
        "non_torch_bytes", "gpu_baseline_bytes",
        "gpu_total_bytes", "seconds_per_step", "tokens_per_second", "load_seconds", "wall_seconds",
        "inference_weights_bytes", "inference_prefill_peak_bytes", "inference_cache_bytes", "inference_decode_peak_bytes",
        "loss_first_step", "grad_l2_first_step", "linear_attention_kernel", "causal_conv_kernel", "kernels",
        "harness_version", "config_key"]


def process_peak_mib(r):
    """Highest process memory in MiB: peak reserved by PyTorch + memory held outside PyTorch. None if not recorded."""
    if r.get("process_mib_at_end") is None or r.get("reserved_at_end") is None or r.get("peak_reserved_overall") is None:
        return r.get("process_mib_at_end")
    return max(r["process_mib_at_end"], r["peak_reserved_overall"] / 2 ** 20 + r["process_mib_at_end"] - r["reserved_at_end"] / 2 ** 20)


def main(src, dst):
    last = {}
    for line in open(src):
        r = json.loads(line)
        k = json.dumps([r.get(x) for x in KEYS] + [sorted(r.get("override") or [])])
        last[k] = r
    with open(dst, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in last.values():
            sh, s, inf = r.get("shape") or {}, r.get("summary") or {}, r.get("inference") or {}
            pr = r.get("params_ready") or r.get("params_after_load") or {}
            steps = r.get("steps_detail") or []
            mib = lambda v: None if v is None else v * 2 ** 20
            row = {
                "tag": r.get("tag"), "model_id": r["model_id"], "variant": r.get("variant") or r["technique"],
                "technique": r["technique"], "quant": r["quant"], "dtype": r["dtype"], "amp": r["amp"],
                "grad_ckpt": r["grad_ckpt"], "kbit_prep": r["kbit_prep"], "loss": r.get("loss", "vanilla"),
                "loss_chunk_tokens": r.get("loss_chunk_tokens"), "batch": r["batch"], "seq_len": r["seq_len"],
                "tokens_per_step": r["batch"] * r["seq_len"], "optimizer": r["optimizer"], "lora_r": r["lora_r"],
                "weights_source": "random" if r["weights"] == "random" else "real", "override": " ".join(r.get("override") or []),
                "status": r["status"], "fail_phase": r.get("phase") if r["status"] != "ok" else "",
                "n_layers": sh.get("num_hidden_layers"), "hidden_size": sh.get("hidden_size"), "vocab_size": sh.get("vocab_size"),
                "n_full_attention_layers": sh.get("n_full_attention_layers"),
                "params_stored_bytes": pr.get("total"), "embedding_bytes": pr.get("embedding"),
                "output_head_bytes": pr.get("output_head"), "quantized_4bit_bytes": pr.get("quantized_4bit"),
                "tied_embeddings": pr.get("tied_embeddings"), "trainable_params": pr.get("n_params_trainable"),
                "weights_and_adapters_bytes": s.get("weights_and_adapters_bytes"), "grad_bytes": s.get("grad_bytes"),
                "optimizer_state_bytes": s.get("optimizer_state_bytes"),
                "forward_peak_over_base_bytes": s.get("forward_peak_over_base_bytes"),
                "backward_peak_over_base_bytes": s.get("backward_peak_over_base_bytes"),
                "optimizer_peak_over_base_bytes": s.get("optimizer_peak_over_base_bytes"),
                "retained_after_forward_bytes": s.get("retained_after_forward_bytes"),
                "steady_state_peak_bytes": s.get("steady_state_peak_bytes"), "first_step_peak_bytes": s.get("first_step_peak_bytes"),
                "peak_phase": s.get("peak_phase"), "peak_allocated_overall_bytes": r.get("peak_allocated_overall"),
                "peak_reserved_overall_bytes": r.get("peak_reserved_overall"),
                "process_bytes_at_end": mib(r.get("process_mib_at_end")), "process_peak_bytes": mib(process_peak_mib(r)),
                "non_torch_bytes": (mib(r["process_mib_at_end"]) - r["reserved_at_end"]
                                    if r.get("process_mib_at_end") is not None and r.get("reserved_at_end") is not None else None),
                "gpu_baseline_bytes": mib(r.get("gpu_used_before_mib")),
                "gpu_total_bytes": r.get("gpu_total_bytes"), "seconds_per_step": s.get("seconds_per_step"),
                "tokens_per_second": round(r["batch"] * r["seq_len"] / s["seconds_per_step"], 1) if s.get("seconds_per_step") else None,
                "load_seconds": r.get("load_seconds"), "wall_seconds": r.get("wall_seconds"),
                "inference_weights_bytes": inf.get("base_alloc"), "inference_prefill_peak_bytes": inf.get("peak_prefill"),
                "inference_cache_bytes": inf.get("cache_bytes"), "inference_decode_peak_bytes": inf.get("peak_decode_step"),
                "loss_first_step": steps[0]["loss"] if steps else None, "grad_l2_first_step": steps[0].get("grad_l2") if steps else None,
                "linear_attention_kernel": r.get("linear_attention_kernel"), "causal_conv_kernel": r.get("causal_conv_kernel"),
                "kernels": ("fallback" if r.get("linear_attention_kernel") != "fla" else
                            "fla+causal_conv1d" if r.get("causal_conv_kernel") == "causal_conv1d" else "fla"),
                "harness_version": r.get("harness_version"),
                "config_key": r.get("config_key"),
            }
            w.writerow(row)
    print(f"wrote {len(last)} rows to {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
