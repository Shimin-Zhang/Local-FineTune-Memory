"""One memory probe = one process = one JSON line.

Builds a model (random weights from a real config, or real weights from a local folder),
sets up one technique (inference, full fine-tune, LoRA; optionally on a 4-bit base = QLoRA),
runs a few steps at a fixed batch x sequence shape, and records where GPU memory went.

Memory does not depend on the values of the weights, so random weights from the real config
give the same numbers as the real checkpoint (checked by the `validate_random` runs).

Run with `python -I measure/probe.py ...` (isolated mode; this file has no local imports).
Every run appends exactly one record to --out, including on out-of-memory.
"""
import argparse, gc, hashlib, json, os, subprocess, sys, time, traceback

T0 = time.time()


def nvidia_smi_used_mib():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=20).stdout.strip().splitlines()[0]
        return int(out)
    except Exception:
        return None


def nvidia_smi_process_mib(pid):
    try:
        out = subprocess.run(["nvidia-smi", "--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=20).stdout
        for line in out.strip().splitlines():
            p, m = [x.strip() for x in line.split(",")]
            if int(p) == pid:
                return int(m)
    except Exception:
        pass
    return None


p = argparse.ArgumentParser()
p.add_argument("--model-id", required=True)
p.add_argument("--config", required=True, help="path to the model's config.json")
p.add_argument("--weights", default="random", help="'random' or a local folder with real weights")
p.add_argument("--technique", required=True, choices=["inference", "full", "lora"])
p.add_argument("--quant", default="none", choices=["none", "nf4"], help="nf4 = bitsandbytes 4-bit base (LoRA on it = QLoRA)")
p.add_argument("--dtype", default="bf16", choices=["fp32", "bf16"], help="storage dtype of non-quantized base weights")
p.add_argument("--amp", default="none", choices=["none", "bf16"], help="autocast dtype during forward")
p.add_argument("--grad-ckpt", type=int, default=0)
p.add_argument("--kbit-prep", type=int, default=0, help="call peft.prepare_model_for_kbit_training (QLoRA recipes often do)")
p.add_argument("--seq-len", type=int, default=2048)
p.add_argument("--batch", type=int, default=2)
p.add_argument("--optimizer", default="adamw", choices=["adamw", "adamw_fused", "sgd", "sgd_momentum", "adamw8bit"])
p.add_argument("--lora-r", type=int, default=16)
p.add_argument("--lora-targets", default="all-linear")
p.add_argument("--steps", type=int, default=3)
p.add_argument("--loss", default="vanilla", choices=["vanilla", "chunked"],
               help="vanilla = model(labels=...) as in stock Hugging Face; chunked = same loss computed a slice at a time")
p.add_argument("--loss-chunk-tokens", type=int, default=128, help="tokens (across the batch) per slice for --loss chunked")
p.add_argument("--override", action="append", default=[], help="config override key=int, e.g. vocab_size=32000")
p.add_argument("--scratch", default=".scratch", help="where random checkpoints for 4-bit loading are cached")
p.add_argument("--device", default="cuda", choices=["cuda", "cpu"], help="cpu is for code-path smoke tests only")
p.add_argument("--tag", default="")
p.add_argument("--variant", default="", help="label for the technique variant, stored for charts")
p.add_argument("--out", required=True)
args = p.parse_args()

rec = {k.replace("-", "_"): v for k, v in vars(args).items() if k != "out"}
key_fields = ["model_id", "weights", "technique", "quant", "dtype", "amp", "grad_ckpt", "kbit_prep", "seq_len", "batch",
              "optimizer", "lora_r", "lora_targets", "steps", "loss", "loss_chunk_tokens", "override", "device", "tag"]
rec["config_key"] = hashlib.sha1(json.dumps({k: rec[k] for k in key_fields}, sort_keys=True).encode()).hexdigest()[:12]
rec["harness_version"] = 2  # 2: random weights load via from_pretrained; chunked loss option; fixed seed
rec["status"] = "started"
rec["phase"] = "import"
rec["gpu_used_before_mib"] = nvidia_smi_used_mib() if args.device == "cuda" else None
rec["started_unix"] = int(T0)


def finish(status, **extra):
    rec["status"] = status
    rec.update(extra)
    rec["wall_seconds"] = round(time.time() - T0, 1)
    if args.device == "cuda":
        try:
            rec["process_mib_at_end"] = nvidia_smi_process_mib(os.getpid())
            rec["gpu_used_at_end_mib"] = nvidia_smi_used_mib()
            note_peaks()
            rec["peak_allocated_overall"] = OVERALL["allocated"]
            rec["peak_reserved_overall"] = OVERALL["reserved"]
            rec["allocated_at_end"] = torch.cuda.memory_allocated()
            rec["reserved_at_end"] = torch.cuda.memory_reserved()
            # GPU memory this process holds outside PyTorch's allocator: normally the ~0.46 GiB CUDA context.
            # It is ~2 GiB in a run that compiled Triton kernels for the first time (see run_matrix.py).
            if rec.get("process_mib_at_end") is not None:
                rec["non_torch_overhead_mib"] = round(rec["process_mib_at_end"] - rec["reserved_at_end"] / 2 ** 20, 1)
        except Exception:
            pass
    with open(args.out, "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps({k: rec.get(k) for k in ["config_key", "model_id", "technique", "quant", "dtype", "amp", "grad_ckpt",
                                              "seq_len", "batch", "status", "phase", "peak_allocated_overall",
                                              "peak_reserved_overall", "process_mib_at_end", "non_torch_overhead_mib", "wall_seconds"]}))
    sys.stdout.flush()
    os._exit(0)


try:
    import torch
    import transformers, peft, bitsandbytes, accelerate
    from transformers import AutoConfig, AutoModelForCausalLM, BitsAndBytesConfig
except Exception as e:  # pragma: no cover
    rec["error"] = traceback.format_exc()[-2000:]
    with open(args.out, "a") as f:
        rec["status"] = "error"
        f.write(json.dumps(rec) + "\n")
    raise

torch.manual_seed(0)  # same random weights and inputs in every probe, so losses and gradients are comparable
CUDA = args.device == "cuda"
DEV = torch.device(args.device)
DTYPE = {"fp32": torch.float32, "bf16": torch.bfloat16}[args.dtype]
import importlib.util as _u
rec["versions"] = {"torch": torch.__version__, "transformers": transformers.__version__, "peft": peft.__version__,
                   "bitsandbytes": bitsandbytes.__version__, "accelerate": accelerate.__version__}
rec["linear_attention_kernel"] = "fla" if _u.find_spec("fla") else "torch_fallback"
rec["causal_conv_kernel"] = "causal_conv1d" if _u.find_spec("causal_conv1d") else "torch_fallback"
if CUDA:
    rec["gpu_name"] = torch.cuda.get_device_name(0)
    rec["gpu_total_bytes"] = torch.cuda.mem_get_info()[1]


def alloc():
    return torch.cuda.memory_allocated() if CUDA else 0


def peak():
    return torch.cuda.max_memory_allocated() if CUDA else 0


OVERALL = {"allocated": 0, "reserved": 0}


def note_peaks():
    if CUDA:
        OVERALL["allocated"] = max(OVERALL["allocated"], torch.cuda.max_memory_allocated())
        OVERALL["reserved"] = max(OVERALL["reserved"], torch.cuda.max_memory_reserved())


def reset_peak():
    if CUDA:
        note_peaks()
        torch.cuda.reset_peak_memory_stats()


def sync():
    if CUDA:
        torch.cuda.synchronize()


def text_config():
    cfg = AutoConfig.from_pretrained(args.config)
    tc = cfg.text_config if hasattr(cfg, "text_config") else cfg
    for ov in args.override:
        k, v = ov.split("=")
        setattr(tc, k, int(v))
    return tc


def param_stats(model):
    """Bytes of parameters actually stored, deduplicated, grouped the way the charts need."""
    seen, out = set(), {"total": 0, "trainable": 0, "frozen": 0, "by_dtype": {}, "embedding": 0, "output_head": 0,
                        "quantized_4bit": 0, "n_params_total": 0, "n_params_trainable": 0}
    emb = model.get_input_embeddings().weight
    head_mod = model.get_output_embeddings()
    head = head_mod.weight if head_mod is not None else None
    out["tied_embeddings"] = bool(head is not None and head is emb)
    for name, prm in model.named_parameters():
        if id(prm) in seen:
            continue
        seen.add(id(prm))
        b = prm.numel() * prm.element_size()
        out["total"] += b
        out["trainable" if prm.requires_grad else "frozen"] += b
        out["by_dtype"][str(prm.dtype).replace("torch.", "")] = out["by_dtype"].get(str(prm.dtype).replace("torch.", ""), 0) + b
        is4 = prm.__class__.__name__ == "Params4bit"
        if is4:
            out["quantized_4bit"] += b
        if prm is emb:
            out["embedding"] += b
        elif head is not None and prm is head:
            out["output_head"] += b
        if not is4:
            out["n_params_total"] += prm.numel()
        if prm.requires_grad:
            out["n_params_trainable"] += prm.numel()
    out["buffers"] = sum(bf.numel() * bf.element_size() for bf in model.buffers())
    return out


def random_checkpoint_dir(tc):
    """A bf16 random-weight checkpoint on disk, needed because 4-bit quantization happens in from_pretrained."""
    tagv = "_".join(args.override) if args.override else "base"
    d = os.path.join(args.scratch, "random", args.model_id.replace("/", "__") + "__" + tagv)
    if not os.path.exists(os.path.join(d, "config.json")):
        t = time.time()
        m = AutoModelForCausalLM.from_config(tc, dtype=torch.bfloat16)
        m.save_pretrained(d)
        del m
        gc.collect()
        rec["random_checkpoint_build_seconds"] = round(time.time() - t, 1)
    return d


try:
    # ------------------------------------------------------------------ load
    rec["phase"] = "load"
    tc = text_config()
    rec["shape"] = {k: getattr(tc, k, None) for k in ["num_hidden_layers", "hidden_size", "intermediate_size", "vocab_size",
                                                      "num_attention_heads", "num_key_value_heads", "head_dim"]}
    lt = getattr(tc, "layer_types", None)
    rec["shape"]["n_full_attention_layers"] = lt.count("full_attention") if lt else tc.num_hidden_layers
    reset_peak()
    t = time.time()
    if args.quant == "nf4":
        src = args.weights if args.weights != "random" else random_checkpoint_dir(tc)
        qc = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True,
                                bnb_4bit_compute_dtype=torch.bfloat16)
        model = AutoModelForCausalLM.from_pretrained(src, quantization_config=qc, dtype=torch.bfloat16, device_map={"": 0})
    else:
        # Random weights go through the same from_pretrained path as real ones (a random checkpoint on disk),
        # so load-time allocation matches real usage. Building directly on the GPU left a constant 24 MiB extra.
        src = args.weights if args.weights != "random" else random_checkpoint_dir(tc)
        model = AutoModelForCausalLM.from_pretrained(src, dtype=DTYPE, device_map={"": 0} if CUDA else None)
    sync()
    gc.collect()
    rec["load_seconds"] = round(time.time() - t, 1)
    rec["model_class"] = type(model).__name__
    rec["attn_implementation"] = getattr(model.config, "_attn_implementation", None)
    rec["alloc_after_load"] = alloc()
    rec["peak_during_load"] = peak()
    rec["params_after_load"] = param_stats(model)
    rec["devices"] = sorted({str(q.device) for q in model.parameters()})

    V = tc.vocab_size
    B, S = args.batch, args.seq_len
    g = torch.Generator().manual_seed(0)
    ids = torch.randint(0, V, (B, S), generator=g).to(DEV)
    mask = torch.ones_like(ids)
    rec["tokens_per_step"] = B * S
    amp_on = args.amp == "bf16"

    def autocast():
        return torch.autocast(args.device, dtype=torch.bfloat16, enabled=amp_on)

    # ------------------------------------------------------------- inference
    if args.technique == "inference":
        rec["phase"] = "inference_prefill"
        model.eval()
        base = alloc()
        reset_peak()
        t = time.time()
        with torch.no_grad(), autocast():
            try:
                out = model(input_ids=ids, attention_mask=mask, use_cache=True, logits_to_keep=1)
                rec["logits_to_keep"] = 1
            except TypeError:
                out = model(input_ids=ids, attention_mask=mask, use_cache=True)
                rec["logits_to_keep"] = None
        sync()
        rec["prefill_seconds"] = round(time.time() - t, 3)
        rec["inference"] = {"base_alloc": base, "peak_prefill": peak()}
        past = out.past_key_values
        del out
        gc.collect()
        rec["inference"]["cache_bytes"] = alloc() - base
        rec["inference"]["cache_bytes_per_token"] = (alloc() - base) / (B * S)
        rec["phase"] = "inference_decode"
        nxt = torch.randint(0, V, (B, 1), generator=g).to(DEV)
        reset_peak()
        with torch.no_grad(), autocast():
            out = model(input_ids=nxt, attention_mask=torch.ones(B, S + 1, dtype=mask.dtype, device=DEV),
                        past_key_values=past, use_cache=True)
        sync()
        rec["inference"]["peak_decode_step"] = peak()
        rec["inference"]["logits_finite"] = bool(torch.isfinite(out.logits.float()).all())
        finish("ok")

    # -------------------------------------------------------------- training
    rec["phase"] = "prepare"
    model.train()
    if args.technique == "lora":
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        if args.kbit_prep:
            model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=bool(args.grad_ckpt))
        else:
            for prm in model.parameters():
                prm.requires_grad = False
            if args.grad_ckpt:
                model.gradient_checkpointing_enable()
        rec["alloc_after_prepare"] = alloc()
        targets = args.lora_targets if args.lora_targets == "all-linear" else args.lora_targets.split(",")
        model = get_peft_model(model, LoraConfig(r=args.lora_r, lora_alpha=2 * args.lora_r, lora_dropout=0.0,
                                                 target_modules=targets, task_type="CAUSAL_LM"))
    else:
        if args.grad_ckpt:
            model.gradient_checkpointing_enable()
    rec["gradient_checkpointing"] = bool(getattr(model, "is_gradient_checkpointing", False))
    rec["params_ready"] = param_stats(model)
    trainable = [q for q in model.parameters() if q.requires_grad]
    rec["trainable_dtypes"] = sorted({str(q.dtype).replace("torch.", "") for q in trainable})
    if args.optimizer == "adamw":
        opt = torch.optim.AdamW(trainable, lr=1e-5)
    elif args.optimizer == "adamw_fused":
        opt = torch.optim.AdamW(trainable, lr=1e-5, fused=True)
    elif args.optimizer == "sgd":
        opt = torch.optim.SGD(trainable, lr=1e-5)
    elif args.optimizer == "sgd_momentum":
        opt = torch.optim.SGD(trainable, lr=1e-5, momentum=0.9)
    else:
        opt = bitsandbytes.optim.AdamW8bit(trainable, lr=1e-5)
    gc.collect()
    rec["alloc_before_training"] = alloc()
    if args.loss == "chunked":
        from peft import PeftModel
        causal = model.get_base_model() if isinstance(model, PeftModel) else model
        body = getattr(causal, causal.base_model_prefix)
        head = causal.get_output_embeddings()
        rec["chunked_loss"] = {"body_class": type(body).__name__, "head_class": type(head).__name__,
                               "positions_per_slice": max(1, args.loss_chunk_tokens // B)}

    steps = []
    reset_peak()
    for i in range(args.steps):
        st = {"step": i}
        rec["phase"] = f"step{i}_forward"
        opt.zero_grad(set_to_none=True)
        gc.collect()
        st["base_alloc"] = alloc()
        reset_peak()
        sync(); t = time.time()
        if args.loss == "vanilla":
            with autocast():
                out = model(input_ids=ids, attention_mask=mask, labels=ids)
                loss = out.loss
            sync()
            st["forward_seconds"] = round(time.time() - t, 3)
            st["after_forward_alloc"] = alloc()
            st["peak_forward"] = peak()
            st["logits_dtype"] = str(out.logits.dtype).replace("torch.", "")
            st["loss"] = float(loss.detach().float())
            rec["phase"] = f"step{i}_backward"
            reset_peak()
            t = time.time()
            loss.backward()
            sync()
            st["backward_seconds"] = round(time.time() - t, 3)
            st["peak_backward"] = peak()
            del out, loss
        else:
            # Same loss as above (mean cross-entropy over the B*(S-1) shifted positions), but the logits are
            # produced and consumed one slice of positions at a time, so the full tokens x vocab tensor never exists.
            with autocast():
                hidden = body(input_ids=ids, attention_mask=mask).last_hidden_state
            sync()
            st["forward_seconds"] = round(time.time() - t, 3)
            st["after_forward_alloc"] = alloc()
            st["peak_forward"] = peak()
            rec["phase"] = f"step{i}_backward"
            reset_peak()
            t = time.time()
            hd = hidden.detach().requires_grad_(True)
            n_tok, total, per = B * (S - 1), 0.0, max(1, args.loss_chunk_tokens // B)
            for a0 in range(0, S - 1, per):
                a1 = min(a0 + per, S - 1)
                with autocast():
                    lg = head(hd[:, a0:a1])
                st["logits_dtype"] = str(lg.dtype).replace("torch.", "")
                lc = torch.nn.functional.cross_entropy(lg.float().reshape(-1, V), ids[:, a0 + 1:a1 + 1].reshape(-1),
                                                       reduction="sum") / n_tok
                lc.backward()
                total += float(lc.detach())
                del lg, lc
            hidden.backward(hd.grad)
            sync()
            st["backward_seconds"] = round(time.time() - t, 3)
            st["peak_backward"] = peak()
            st["loss"] = total
            del hidden, hd
        gc.collect()
        st["after_backward_alloc"] = alloc()
        st["grad_bytes"] = sum(q.grad.numel() * q.grad.element_size() for q in trainable if q.grad is not None)
        st["trainable_without_grad"] = sum(1 for q in trainable if q.grad is None)
        st["grad_l2"] = float(sum(float(torch.linalg.vector_norm(q.grad.float())) ** 2 for q in trainable if q.grad is not None) ** 0.5)
        rec["phase"] = f"step{i}_optimizer"
        reset_peak()
        t = time.time()
        opt.step()
        sync()
        st["optimizer_seconds"] = round(time.time() - t, 3)
        st["peak_optimizer_step"] = peak()
        st["after_optimizer_alloc"] = alloc()
        st["optimizer_state_bytes"] = sum(v.numel() * v.element_size() for s in opt.state.values() for v in s.values()
                                          if torch.is_tensor(v))
        st["peak_step"] = max(st["peak_forward"], st["peak_backward"], st["peak_optimizer_step"])
        steps.append(st)
        rec["steps_detail"] = steps
    last = steps[-1]
    rec["summary"] = {
        "weights_and_adapters_bytes": rec["alloc_before_training"],
        "grad_bytes": last["grad_bytes"],
        "optimizer_state_bytes": last["optimizer_state_bytes"],
        "retained_after_forward_bytes": last["after_forward_alloc"] - last["base_alloc"],
        "forward_peak_over_base_bytes": last["peak_forward"] - last["base_alloc"],
        "backward_peak_over_base_bytes": last["peak_backward"] - last["base_alloc"],
        "optimizer_peak_over_base_bytes": last["peak_optimizer_step"] - last["base_alloc"],
        "steady_state_peak_bytes": max(s["peak_step"] for s in steps[1:]) if len(steps) > 1 else last["peak_step"],
        "first_step_peak_bytes": steps[0]["peak_step"],
        "peak_phase": max(("forward", "backward", "optimizer"), key=lambda ph: last[{"forward": "peak_forward", "backward": "peak_backward", "optimizer": "peak_optimizer_step"}[ph]]),
        "seconds_per_step": round(last["forward_seconds"] + last["backward_seconds"] + last["optimizer_seconds"], 3),
        "loss_finite": all(s["loss"] == s["loss"] and abs(s["loss"]) != float("inf") for s in steps),
        "all_trainable_have_grad": all(s["trainable_without_grad"] == 0 for s in steps),
    }
    finish("ok")
except torch.OutOfMemoryError as e:
    finish("oom", error=str(e)[:600])
except SystemExit:
    raise
except Exception as e:
    # Out-of-memory raised outside PyTorch's allocator (for example inside a Triton kernel) is still out-of-memory.
    if "out of memory" in str(e).lower():
        finish("oom", error=traceback.format_exc()[-1500:], oom_source="outside the PyTorch allocator")
    finish("error", error=traceback.format_exc()[-3000:])
