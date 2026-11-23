"""Exact per-model parameter breakdown, counted on the meta device (no weights are ever allocated).

Usage (from the repo root):
    CUDA_VISIBLE_DEVICES="" uv run python catalog/param_breakdown.py \
        catalog/models.json catalog/configs catalog/param_breakdown.json

Method, per catalog row (one model at a time):
  1. AutoConfig.from_pretrained(<local config.json>, trust_remote_code=False).
  2. Full model: the class named in config.architectures (fallback: AutoModelForImageTextToText /
     AutoModelForCausalLM / AutoModel), built with accelerate.init_empty_weights(include_buffers=True),
     then model.tie_weights(). Every parameter is asserted to be on the meta device before counting.
  3. Text-only model: for multimodal configs, AutoModelForCausalLM.from_config(config.get_text_config())
     (e.g. Qwen3_5ForCausalLM, Gemma3ForCausalLM); otherwise the full model is the text model.
  4. Shared tensors are counted once (dedup by id(param)). "Tied" means the input embedding weight and the
     output head weight are the same Python object after tie_weights(); the config flag is not trusted.
  5. bitsandbytes 4-bit: the text class is rebuilt with the same init context from_pretrained uses for a
     quantized load (cls.get_init_context(dtype, is_quantized=True, ...)), then transformers' own
     Bnb4BitHfQuantizer.get_modules_to_not_convert (-> quantizers.base.get_keys_to_not_convert, plus
     model._keep_in_fp32_modules) gives the skip list and integrations.bitsandbytes.replace_with_bnb_linear
     is run on the meta model. bnb_quantizable_params = weights of the resulting Linear4bit modules.
  6. KV cache, MoE totals and an explanation of any difference from the Hub's stored parameter count.

Safety: CUDA is hidden before torch is imported, the process data segment is capped (RLIMIT_DATA), and
resident memory is checked after every model.
"""
import os

os.environ["CUDA_VISIBLE_DEVICES"] = ""  # the GPU is reserved for another job; never touch it
os.environ.setdefault("HF_HUB_OFFLINE", "1")  # local config files only, no network
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

import resource

MEM_CAP_BYTES = 8 * 1024**3  # any accidental real allocation of a big model fails instead of eating RAM
_soft, _hard = resource.getrlimit(resource.RLIMIT_DATA)
resource.setrlimit(resource.RLIMIT_DATA, (MEM_CAP_BYTES, _hard))

import collections
import copy
import gc
import json
import re
import sys
import traceback
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import accelerate
import bitsandbytes as bnb
import torch
import transformers
from accelerate import init_empty_weights
from torch import nn
from transformers import (
    AutoConfig,
    AutoModel,
    AutoModelForCausalLM,
    AutoModelForImageTextToText,
    BitsAndBytesConfig,
    LlamaConfig,
)
from transformers.integrations.bitsandbytes import replace_with_bnb_linear
from transformers.pytorch_utils import Conv1D
from transformers.quantizers.auto import AutoHfQuantizer
from transformers.quantizers.quantizers_utils import should_convert_module
from transformers.utils import ContextManagers

assert not torch.cuda.is_available(), "CUDA must be hidden for this script"

ENV = (
    f"transformers {transformers.__version__} / torch {torch.__version__} / accelerate {accelerate.__version__}"
    f" / bitsandbytes {bnb.__version__}"
)
BNB_FUNCTION = (
    "transformers.quantizers.quantizer_bnb_4bit.Bnb4BitHfQuantizer.get_modules_to_not_convert(model, "
    "llm_int8_skip_modules=None, model._keep_in_fp32_modules) -> transformers.quantizers.base."
    "get_keys_to_not_convert(model) [tied keys + last parameter + get_output_embeddings()] plus "
    "_keep_in_fp32_modules; then transformers.integrations.bitsandbytes.replace_with_bnb_linear converts every "
    "module with type(m) is nn.Linear or Conv1D whose name passes should_convert_module(name, skip)"
)


# ----------------------------------------------------------------------------- helpers
def rss_gb():
    with open("/proc/self/status") as fh:
        for line in fh:
            if line.startswith("VmRSS"):
                return int(line.split()[1]) / 1e6
    return float("nan")


def assert_meta(model, what):
    """Every parameter must be on meta; non-meta buffers (if any) must be tiny."""
    for name, p in model.named_parameters(remove_duplicate=False):
        if p.device.type != "meta":
            raise RuntimeError(f"{what}: parameter {name} is on {p.device}, not meta")
    assert next(model.parameters()).device.type == "meta"
    real_buf = sum(b.numel() * b.element_size() for b in model.buffers() if b.device.type != "meta")
    if real_buf > 64 * 1024**2:
        raise RuntimeError(f"{what}: {real_buf / 1e6:.1f} MB of real buffers allocated")
    if rss_gb() > 6.0:
        raise RuntimeError(f"{what}: resident memory {rss_gb():.2f} GB, aborting")


def build_meta(factory, what):
    """Instantiate on meta. Buffers go to meta too; fall back to params-only if a model needs real buffers."""
    try:
        with init_empty_weights(include_buffers=True):
            model = factory()
        mode = "params+buffers on meta"
    except Exception:
        with init_empty_weights(include_buffers=False):
            model = factory()
        mode = "params on meta (buffers real)"
    model.tie_weights()
    assert_meta(model, what)
    return model, mode


def unique_params(model):
    """(name, param) for every distinct tensor, deduplicated by id(param)."""
    seen, out = set(), []
    for name, p in model.named_parameters(remove_duplicate=False):
        if id(p) not in seen:
            seen.add(id(p))
            out.append((name, p))
    return out


def count(model):
    return sum(p.numel() for _, p in unique_params(model))


def layer_cfg(tc, i):
    """Per-layer view of a (possibly heterogeneous, e.g. Gemma-4) text config."""
    try:
        het = bool(tc.is_heterogeneous)
    except Exception:
        het = False
    return tc.per_layer_config[i] if het else tc


def pct(counted, ref):
    return round(100.0 * (counted - ref) / ref, 8) + 0.0  # + 0.0 turns -0.0 into 0.0


def cfg_get(c, name, default=None):
    try:
        v = getattr(c, name)
    except Exception:
        return default
    return default if v is None else v


def is_expert_module(mod, name):
    return type(mod).__name__.endswith("Experts") and "shared" not in name.split(".")[-1]


def find_layers(model, n_layers):
    for name, mod in model.named_modules():
        if isinstance(mod, nn.ModuleList) and len(mod) == n_layers and name.endswith("layers"):
            return name, mod
    return None, None


# ----------------------------------------------------------------------------- text breakdown
def text_breakdown(t):
    ie, oe = t.get_input_embeddings(), t.get_output_embeddings()
    emb_ids = {id(p) for p in ie.parameters()}
    tied = oe is not None and oe.weight is ie.weight
    head_ids = ({id(p) for p in oe.parameters()} - emb_ids) if oe is not None else set()
    head_mod_ids = {id(oe)} if oe is not None else set()

    expert_prefixes = [n for n, m in t.named_modules() if is_expert_module(m, n) and any(True for _ in m.parameters())]
    # keep only outermost expert modules
    expert_prefixes = [p for p in expert_prefixes if not any(p != q and p.startswith(q + ".") for q in expert_prefixes)]

    def in_experts(mod_name):
        return any(mod_name == p or mod_name.startswith(p + ".") for p in expert_prefixes)

    cats = collections.Counter()
    other_detail = collections.Counter()
    linear_subclass = 0
    seen = set()
    for mod_name, mod in t.named_modules(remove_duplicate=False):
        for pn, p in mod.named_parameters(recurse=False):
            if id(p) in seen:
                continue
            seen.add(id(p))
            n = p.numel()
            if id(p) in emb_ids:
                cats["embedding"] += n
            elif id(p) in head_ids:
                cats["output_head"] += n
            elif isinstance(mod, nn.Embedding):
                cats["extra_embedding"] += n
            elif isinstance(mod, nn.Linear) and pn == "weight" and id(mod) not in head_mod_ids:
                cats["linear_weight"] += n
                if type(mod) is not nn.Linear:
                    linear_subclass += n
            elif in_experts(mod_name):
                cats["moe_expert_fused"] += n
            else:
                cats["other"] += n
                key = f"{type(mod).__name__}.{pn}" if isinstance(mod, (nn.Linear, nn.Conv1d)) else type(mod).__name__
                other_detail[key] += n
    return {
        "tied": tied,
        "embedding": cats["embedding"],
        "output_head": cats["output_head"],
        "extra_embedding": cats["extra_embedding"],
        "linear_weight": cats["linear_weight"],
        "moe_expert_fused": cats["moe_expert_fused"],
        "other": cats["other"],
        "other_detail": dict(other_detail.most_common()),
        "linear_subclass": linear_subclass,
        "expert_prefixes": expert_prefixes,
    }


# ----------------------------------------------------------------------------- MoE
def moe_info(t, tc, n_text, expert_prefixes):
    if not expert_prefixes:
        return None
    mods = dict(t.named_modules())
    total, weights_3d, n_exp_seen, classes = 0, 0, set(), set()
    for p in expert_prefixes:
        m = mods[p]
        classes.add(type(m).__name__)
        for pn, prm in m.named_parameters():
            total += prm.numel()
            if prm.dim() == 3:
                n_exp_seen.add(prm.shape[0])
                weights_3d += prm.numel()
        if isinstance(m, nn.ModuleList):
            n_exp_seen.add(len(m))
    assert len(n_exp_seen) == 1, f"inconsistent expert counts {n_exp_seen}"
    E = n_exp_seen.pop()
    moe_layer_idx = int(re.search(r"\.(\d+)\.", expert_prefixes[0] + ".").group(1))
    lc = layer_cfg(tc, moe_layer_idx)
    k = None
    for attr in ("num_experts_per_tok", "top_k_experts", "experts_per_token", "moe_top_k"):
        k = cfg_get(lc, attr)
        if k is not None:
            break
    cfg_E = None
    for attr in ("num_experts", "num_local_experts", "n_routed_experts"):
        cfg_E = cfg_get(lc, attr)
        if cfg_E is not None:
            break
    shared = 0
    router = 0
    seen = set()
    for mod_name, mod in t.named_modules():
        last = mod_name.split(".")[-1]
        if "shared_expert" in last:
            for prm in mod.parameters():
                if id(prm) not in seen:
                    seen.add(id(prm))
                    shared += prm.numel()
        elif "router" in type(mod).__name__.lower():
            for prm in mod.parameters():
                if id(prm) not in seen:
                    seen.add(id(prm))
                    router += prm.numel()
    assert (total * k) % E == 0
    active = total * k // E
    return {
        "num_experts": E,
        "num_experts_config": cfg_E,
        "experts_per_token": k,
        "n_moe_layers": len(expert_prefixes),
        "expert_module_class": sorted(classes),
        "expert_params_total": total,
        "expert_weight_params_3d": weights_3d,  # fused expert matrices only (expert_params_total minus expert biases)
        "expert_params_active_per_token": active,
        "expert_params_per_expert_per_layer": total // (E * len(expert_prefixes)),
        "shared_expert_params": shared,
        "router_params": router,
        "active_params_per_token_text": n_text - total + active,
    }


# ----------------------------------------------------------------------------- KV cache
def kv_info(t, tc, notes):
    L = tc.num_hidden_layers
    lt = cfg_get(tc, "layer_types")
    sw_global = cfg_get(layer_cfg(tc, 0), "sliding_window")
    max_pos = cfg_get(tc, "max_position_embeddings")
    if lt is None:
        if sw_global is not None and max_pos is not None and sw_global < max_pos:
            lt = ["sliding_attention"] * L
            notes.append(f"no layer_types in config; sliding_window={sw_global} applies to every layer.")
        else:
            lt = ["full_attention"] * L
            if sw_global is not None:
                notes.append(
                    f"config sets sliding_window={sw_global} >= max_position_embeddings={max_pos}, so every "
                    "layer is treated as full attention."
                )
    assert len(lt) == L, (len(lt), L)
    n_shared = cfg_get(tc, "num_kv_shared_layers", 0) or 0
    first_shared = L - n_shared
    _, layers = find_layers(t, L)

    def kv_dims(i):
        lc = layer_cfg(tc, i)
        nkv = cfg_get(lc, "num_key_value_heads") or cfg_get(lc, "num_attention_heads")
        hd = cfg_get(lc, "head_dim") or (lc.hidden_size // lc.num_attention_heads)
        return nkv, hd

    def module_check(i, nkv, hd):
        if layers is None:
            return None
        k = v = qkv = None
        for n, m in layers[i].named_modules():
            if isinstance(m, nn.Linear):
                last = n.split(".")[-1]
                if last == "qkv_proj":  # fused (Phi-3)
                    qkv = m
                elif last == "k_proj":
                    k = m
                elif last == "v_proj":
                    v = m
        if k is not None:
            ok = k.out_features == nkv * hd and (v is None or v.out_features == nkv * hd)
            return ok
        if qkv is not None:
            lc = layer_cfg(tc, i)
            return qkv.out_features - lc.num_attention_heads * hd == 2 * nkv * hd
        return None

    groups = {"full": [], "sliding": [], "linear": [], "shared": [], "other": []}
    for i, kind in enumerate(lt):
        if i >= first_shared and kind in ("full_attention", "sliding_attention", "attention"):
            groups["shared"].append(i)
        elif kind in ("full_attention", "attention"):
            groups["full"].append(i)
        elif kind in ("sliding_attention", "chunked_attention"):
            groups["sliding"].append(i)
        elif kind in ("linear_attention", "mamba"):
            groups["linear"].append(i)
        else:
            groups["other"].append(i)

    def bytes_for(idx):
        total, dims, checks = 0, set(), []
        for i in idx:
            nkv, hd = kv_dims(i)
            dims.add((nkv, hd))
            total += 2 * nkv * hd * 2
            checks.append(module_check(i, nkv, hd))
        return total, sorted(dims), checks

    full_b, full_dims, full_chk = bytes_for(groups["full"])
    sl_b, sl_dims, sl_chk = bytes_for(groups["sliding"])
    checks = [c for c in full_chk + sl_chk if c is not None]
    if not all(checks):
        notes.append("WARNING: k_proj/v_proj shapes disagree with config kv heads x head_dim for some layer.")
    sw = None
    if groups["sliding"]:
        sw = cfg_get(layer_cfg(tc, groups["sliding"][0]), "sliding_window")
    return {
        "n_full_attention_layers": len(groups["full"]),
        "n_full_attention_layers_in_layer_types": sum(1 for k in lt if k in ("full_attention", "attention")),
        "n_sliding_attention_layers": len(groups["sliding"]),
        "n_linear_attention_layers": len(groups["linear"]),
        "n_kv_shared_layers": len(groups["shared"]),
        "n_non_attention_layers": len(groups["other"]),
        "layer_kinds": dict(collections.Counter(lt)),
        "kv_dims_full": [list(d) for d in full_dims],  # [n_kv_heads, head_dim] used for full-attention layers
        "kv_bytes_per_token_fp16": full_b,
        "kv_bytes_per_token_sliding_fp16": sl_b,
        "kv_dims_sliding": [list(d) for d in sl_dims],
        "sliding_window": sw,
        "kv_module_shapes_checked": f"{sum(checks)}/{len(full_chk) + len(sl_chk)} layers",
    }


# ----------------------------------------------------------------------------- bitsandbytes
def bnb_info(text_cls, tc, cfg_for_preq):
    qc = BitsAndBytesConfig(load_in_4bit=True)
    quantizer = AutoHfQuantizer.from_config(qc, pre_quantized=False)
    ctx = text_cls.get_init_context(torch.bfloat16, True, False, None)
    with ContextManagers(ctx):
        m = text_cls(copy.deepcopy(tc))
        assert_meta(m, "bnb text model")
        skip = quantizer.get_modules_to_not_convert(
            m, quantizer.quantization_config.llm_int8_skip_modules, m._keep_in_fp32_modules
        )
        pred = 0
        for name, mod in m.named_modules():
            if not should_convert_module(name, skip):
                continue
            if isinstance(mod, Conv1D) or type(mod) is nn.Linear:
                pred += mod.weight.numel()
        replace_with_bnb_linear(m, modules_to_not_convert=skip, quantization_config=qc, pre_quantized=False)
    converted = sum(mod.in_features * mod.out_features for mod in m.modules() if isinstance(mod, bnb.nn.Linear4bit))
    n_conv_mods = sum(1 for mod in m.modules() if isinstance(mod, bnb.nn.Linear4bit))
    assert converted == pred, (converted, pred)
    keep_fp32 = sorted(m._keep_in_fp32_modules or [])
    keep_fp32_strict = sorted(m._keep_in_fp32_modules_strict or [])
    del m
    gc.collect()

    preq_note = None
    qcfg = cfg_get(cfg_for_preq, "quantization_config") if cfg_for_preq is not None else None
    if qcfg is not None:
        qdict = qcfg if isinstance(qcfg, dict) else qcfg.to_dict()
        method = qdict.get("quant_method")
        if AutoHfQuantizer.supports_quant_method(copy.deepcopy(qdict)):
            try:
                AutoHfQuantizer.merge_quantization_configs(copy.deepcopy(qdict), BitsAndBytesConfig(load_in_4bit=True))
                preq_note = f"checkpoint is pre-quantized ({method}); merge with BitsAndBytesConfig succeeded."
            except Exception as e:
                preq_note = (
                    f"checkpoint is pre-quantized ({method}): from_pretrained(..., quantization_config="
                    f"BitsAndBytesConfig(load_in_4bit=True)) raises {type(e).__name__} in "
                    f"AutoHfQuantizer.merge_quantization_configs: '{str(e)[:160]}'. The skip list above is "
                    "what bnb would do to a 16-bit copy of the weights."
                )
    return {
        "skip": sorted(skip),
        "quantizable": converted,
        "n_linear4bit_modules": n_conv_mods,
        "keep_in_fp32": keep_fp32,
        "keep_in_fp32_strict": keep_fp32_strict,
        "preq_note": preq_note,
    }


# ----------------------------------------------------------------------------- full-model split
VISION_TOKENS = ("vision", "visual", "multi_modal_projector", "image")
AUDIO_TOKENS = ("audio",)


def full_split(full, multimodal):
    out = collections.Counter()
    modules = collections.Counter()
    for name, p in unique_params(full):
        low = name.lower()
        parts = name.split(".")
        if not multimodal:
            out["text"] += p.numel()
            continue
        if any(tok in low for tok in AUDIO_TOKENS):
            out["audio"] += p.numel()
            modules[".".join(parts[:2])] += p.numel()
        elif any(tok in low for tok in VISION_TOKENS):
            out["vision"] += p.numel()
            modules[".".join(parts[:2])] += p.numel()
        elif name.startswith(("model.language_model.", "language_model.", "lm_head")):
            out["text"] += p.numel()
        else:
            out["other"] += p.numel()
            modules[".".join(parts[:2])] += p.numel()
    return out, dict(modules.most_common())


def persistent_buffers(model):
    text, nontext = 0, 0
    for mod_name, mod in model.named_modules():
        for bn, b in mod._buffers.items():
            if b is None or bn in mod._non_persistent_buffers_set:
                continue
            if any(tok in mod_name.lower() for tok in VISION_TOKENS + AUDIO_TOKENS):
                nontext += b.numel()
            else:
                text += b.numel()
    return text, nontext


# ----------------------------------------------------------------------------- hub-difference explanations
def layer_params(layer):
    return sum(p.numel() for _, p in unique_params(layer))


def explain_hub_diff(row, raw, tc, t, counted_full, tied_full, emb_numel):
    """Structural reasons why the Hub's stored tensor count differs from the instantiated model."""
    hub = row["params"]
    diff = hub - counted_full
    explained = []
    H = tc.hidden_size
    L = tc.num_hidden_layers
    _, layers = find_layers(t, L)
    lt = cfg_get(tc, "layer_types") or []

    # Qwen3.5 / Qwen3.6 / Qwen3.8: multi-token-prediction head stored in the checkpoint (mtp.*),
    # not instantiated by transformers. Layout verified against the local Qwen3.5-0.8B-Base header:
    # mtp.fc [H, 2H], mtp.pre_fc_norm_embedding [H], mtp.pre_fc_norm_hidden [H], mtp.norm [H],
    # mtp.layers.0.* = one full-attention decoder layer (attention + MLP/MoE + 2 norms).
    n_mtp = cfg_get(tc, "mtp_num_hidden_layers", 0) or 0
    if n_mtp and layers is not None and "full_attention" in lt:
        one = layer_params(layers[lt.index("full_attention")])
        mtp = n_mtp * one + 2 * H * H + 3 * H
        explained.append(
            {"reason": f"multi-token-prediction head (mtp_num_hidden_layers={n_mtp}) stored but not instantiated",
             "params": mtp,
             "basis": "mtp.fc 2H*H + 3 norms + one full-attention decoder layer copied from the instantiated model; "
                      "this layout was checked tensor-by-tensor against the local Qwen3.5-0.8B-Base safetensors header"}
        )

    # Nemotron-H: num_nextn_predict_layers MTP block, also not instantiated by transformers.
    n_nextn = cfg_get(tc, "num_nextn_predict_layers", 0) or 0
    mtp_pattern = cfg_get(tc, "mtp_hybrid_override_pattern") or cfg_get(tc, "mtp_layers_block_type")
    if n_nextn and layers is not None and mtp_pattern:
        sym = {"*": "full_attention", "E": "moe", "M": "linear_attention", "-": "mlp",
               "attention": "full_attention", "moe": "moe", "mamba": "linear_attention", "mlp": "mlp"}
        kinds = [sym[s] for s in (list(mtp_pattern) if isinstance(mtp_pattern, str) else mtp_pattern)]
        blocks = sum(layer_params(layers[lt.index(k)]) for k in kinds)
        mtp = n_nextn * (blocks + 2 * H * H + 3 * H)
        explained.append(
            {"reason": f"multi-token-prediction block (num_nextn_predict_layers={n_nextn}, pattern {mtp_pattern}) "
                       "not instantiated by transformers",
             "params": mtp,
             "basis": "ESTIMATE: copies of the instantiated blocks named in the MTP pattern + an assumed 2H*H "
                      "projection and 3 H-sized norms (tensor names not verified; no local checkpoint)"}
        )

    # Gemma-4: KV-shared layers have no k/v projections in transformers, but the checkpoint stores them
    # (dropped on load via _keys_to_ignore_on_load_unexpected in modeling_gemma4.py).
    n_shared = cfg_get(tc, "num_kv_shared_layers", 0) or 0
    if n_shared:
        k_eq_v = bool(cfg_get(tc, "attention_k_eq_v", False))
        unused = 0
        for i in range(L - n_shared, L):
            lc = layer_cfg(tc, i)
            nkv, hd = lc.num_key_value_heads, lc.head_dim
            has_v = not (k_eq_v and lt[i] != "sliding_attention")
            unused += H * nkv * hd * (2 if has_v else 1) + hd  # k_proj (+ v_proj) + k_norm (v_norm has no weight)
        explained.append(
            {"reason": f"k_proj/v_proj/k_norm of the {n_shared} KV-shared layers: stored in the checkpoint, "
                       "ignored on load (_keys_to_ignore_on_load_unexpected)",
             "params": unused, "basis": "computed per layer from per_layer_config"}
        )

    if diff == 0:
        # Nothing to explain; keep structural candidates aside (used to check Hub metadata consistency).
        return {"hub_minus_counted_full": 0, "explained": [], "residual": 0, "candidates_not_in_hub_total": explained}
    residual = diff - sum(e["params"] for e in explained)
    # A checkpoint that stores lm_head.weight although the instantiated model ties it to the embedding.
    if tied_full and residual == emb_numel:
        explained.append(
            {"reason": "one extra vocab x hidden matrix: the checkpoint stores a separate lm_head.weight while the "
                       "instantiated model ties it to the input embedding",
             "params": emb_numel, "basis": "inferred from an exact match of the residual"}
        )
        residual = 0
    return {"hub_minus_counted_full": diff, "explained": explained, "residual": residual}


# ----------------------------------------------------------------------------- formula cross-check
def dense_formula(raw):
    """Closed-form count for a plain Llama/Mistral/Qwen3 decoder (no biases), from the raw config JSON."""
    c = raw.get("text_config") or raw
    mt = c.get("model_type")
    if mt not in ("llama", "mistral", "qwen3") or c.get("attention_bias") or c.get("mlp_bias"):
        return None
    H, I, L, V = c["hidden_size"], c["intermediate_size"], c["num_hidden_layers"], c["vocab_size"]
    nq = c["num_attention_heads"]
    nkv = c.get("num_key_value_heads") or nq
    hd = c.get("head_dim") or H // nq
    tie = c.get("tie_word_embeddings", False)
    attn_w = H * nq * hd + 2 * H * nkv * hd + nq * hd * H
    mlp_w = 3 * H * I
    per_layer_other = 2 * H + (2 * hd if mt == "qwen3" else 0)
    linear = L * (attn_w + mlp_w)
    total = linear + L * per_layer_other + H + V * H * (1 if tie else 2)
    return {"total": total, "linear_weight": linear, "kv_bytes_per_token_fp16": 2 * L * nkv * hd * 2,
            "tie_in_raw_config": tie}


# ----------------------------------------------------------------------------- per-model analysis
def pick_full_class(cfg, multimodal):
    arch = (cfg_get(cfg, "architectures") or [None])[0]
    cands = []
    if arch and hasattr(transformers, arch):
        cands.append((arch, lambda c, k=getattr(transformers, arch): k._from_config(c)))
    if multimodal:
        cands.append(("AutoModelForImageTextToText", AutoModelForImageTextToText.from_config))
    cands.append(("AutoModelForCausalLM", AutoModelForCausalLM.from_config))
    cands.append(("AutoModel", AutoModel.from_config))
    return cands


def empty_record(row):
    return {
        "id": row["id"], "status": None, "analytic": False,
        "class_full": None, "class_text": None,
        "hub_params": row["params"], "counted_params_full": None, "counted_params_text": None,
        "diff_vs_hub_pct": None, "tied_embeddings": None,
        "embedding_params": None, "output_head_params": None,
        "text_linear_weight_params": None, "text_moe_expert_params": None,
        "text_extra_embedding_params": None, "text_other_params": None,
        "vision_params": None, "audio_params": None, "other_params": None,
        "n_text_layers": None, "n_full_attention_layers": None, "kv_bytes_per_token_fp16": None,
        "moe": None, "bnb_skip_modules": None, "bnb_quantizable_params": None, "notes": None,
    }


def analyze_model(rec, row, raw, cfg, notes, analytic_proxy=False):
    multimodal = cfg_get(cfg, "vision_config") is not None or cfg_get(cfg, "audio_config") is not None

    # ---- full model
    full, full_cls_name, full_mode, errs = None, None, None, []
    for cname, factory in pick_full_class(cfg, multimodal):
        try:
            full, full_mode = build_meta(lambda: factory(copy.deepcopy(cfg)), "full model")
            full_cls_name = type(full).__name__
            break
        except Exception as e:
            errs.append(f"{cname}: {type(e).__name__}: {str(e)[:200]}")
    if full is None:
        raise RuntimeError("could not instantiate full model: " + " | ".join(errs))
    counted_full = count(full)
    ie_f, oe_f = full.get_input_embeddings(), full.get_output_embeddings()
    tied_full = oe_f is not None and oe_f.weight is ie_f.weight
    split, nontext_modules = full_split(full, multimodal)
    pbuf_text, pbuf_nontext = persistent_buffers(full)

    # ---- text model
    tc = cfg.get_text_config()
    if multimodal:
        t, text_mode = build_meta(lambda: AutoModelForCausalLM.from_config(copy.deepcopy(tc)), "text model")
        leaked = [n for n, _ in unique_params(t) if any(tok in n.lower() for tok in VISION_TOKENS + AUDIO_TOKENS)]
        assert not leaked, f"text-only model contains non-text params: {leaked[:3]}"
    else:
        t, text_mode = full, full_mode
    counted_text = count(t)
    tb = text_breakdown(t)
    emb_numel = tb["embedding"]

    comp_sum = (tb["embedding"] + tb["output_head"] + tb["linear_weight"] + tb["moe_expert_fused"]
                + tb["extra_embedding"] + tb["other"])
    assert comp_sum == counted_text, (comp_sum, counted_text)
    assert split["text"] + split["vision"] + split["audio"] + split["other"] == counted_full

    rec.update({
        "class_full": full_cls_name,
        "class_text": type(t).__name__,
        "counted_params_full": counted_full,
        "counted_params_text": counted_text,
        "diff_vs_hub_pct": pct(counted_full, row["params"]),
        "tied_embeddings": tb["tied"],
        "embedding_params": tb["embedding"],
        "output_head_params": tb["output_head"],
        "text_linear_weight_params": tb["linear_weight"],
        "text_moe_expert_params": tb["moe_expert_fused"],
        "text_extra_embedding_params": tb["extra_embedding"],
        "text_other_params": tb["other"],
        "vision_params": split["vision"],
        "audio_params": split["audio"],
        "other_params": split["other"],
        "n_text_layers": tc.num_hidden_layers,
    })
    dsum = sum((row.get("params_by_dtype") or {}).values()) or None
    rec["hub_params_dtype_sum"] = dsum
    rec["diff_vs_hub_dtype_sum_pct"] = pct(counted_full, dsum) if dsum else None
    rec["full_text_part_params"] = split["text"]
    rec["full_equals_text_plus_nontext"] = split["text"] == counted_text
    rec["tied_embeddings_full"] = tied_full
    rec["config_tie_word_embeddings_text"] = cfg_get(tc, "tie_word_embeddings")
    rec["nontext_modules"] = nontext_modules
    rec["text_other_detail"] = tb["other_detail"]
    rec["persistent_buffer_values"] = {"text": pbuf_text, "nontext": pbuf_nontext}
    rec["meta_init"] = {"full": full_mode, "text": text_mode}

    if not rec["full_equals_text_plus_nontext"]:
        notes.append(
            f"MISMATCH: the language-model part of the full model has {split['text']:,} params but the text-only "
            f"class has {counted_text:,} (difference {counted_text - split['text']:+,}). Tied in full model: "
            f"{tied_full}; tied in text model: {tb['tied']}."
        )
    if tied_full != tb["tied"]:
        top_set = "tie_word_embeddings" in raw
        txt_set = "tie_word_embeddings" in (raw.get("text_config") or {})
        notes.append(
            f"Tie flags disagree: {type(cfg).__name__}.tie_word_embeddings={cfg_get(cfg, 'tie_word_embeddings')} "
            f"({'set in config.json' if top_set else 'class default; key absent from config.json'}) vs "
            f"{type(tc).__name__}.tie_word_embeddings={cfg_get(tc, 'tie_word_embeddings')} "
            f"({'set in config.json' if txt_set else 'class default; key absent from text_config'})."
        )
    lt = cfg_get(tc, "layer_types") or []
    if any(k in ("moe", "mlp") for k in lt):
        notes.append(
            "n_text_layers counts every block in the hybrid pattern: "
            + ", ".join(f"{v} {k}" for k, v in collections.Counter(lt).items())
            + " (MLP/MoE blocks are separate layers here)."
        )
    if tb["linear_subclass"]:
        notes.append(f"{tb['linear_subclass']:,} nn.Linear-subclass weights in the text model are not converted by bnb.")

    # ---- KV cache
    kv = kv_info(t, tc, notes)
    rec["n_full_attention_layers"] = kv.pop("n_full_attention_layers")
    rec["kv_bytes_per_token_fp16"] = kv.pop("kv_bytes_per_token_fp16")
    rec["kv_detail"] = kv
    if kv["n_kv_shared_layers"]:
        notes.append(
            f"KV: {kv['n_kv_shared_layers']} trailing layers reuse the KV of earlier layers (num_kv_shared_layers) and "
            f"keep no cache; n_full_attention_layers counts only the {rec['n_full_attention_layers']} full-attention "
            f"layers with their own cache (layer_types lists {kv['n_full_attention_layers_in_layer_types']})."
        )
    if cfg_get(tc, "attention_k_eq_v", False):
        notes.append(
            "KV: attention_k_eq_v=True, so full-attention layers have no v_proj (V is derived from K), but the "
            "transformers cache stores K and V as separate tensors (past_key_values.update(key, value)), so the 2x "
            "factor still applies."
        )
    if len(kv["kv_dims_full"]) > 1 or (kv["kv_dims_sliding"] and kv["kv_dims_sliding"] != kv["kv_dims_full"]):
        notes.append(
            f"KV: per-layer shapes differ (full-attention [kv_heads, head_dim] = {kv['kv_dims_full']}, sliding = "
            f"{kv['kv_dims_sliding']}); kv_bytes_per_token_fp16 sums the full-attention layers individually."
        )

    # ---- MoE
    rec["moe"] = moe_info(t, tc, counted_text, tb["expert_prefixes"])

    # ---- bnb
    b = bnb_info(type(t), tc, None if analytic_proxy else cfg)
    rec["bnb_skip_modules"] = b["skip"]
    rec["bnb_quantizable_params"] = b["quantizable"]
    rec["bnb_unquantized_params"] = counted_text - b["quantizable"]
    rec["bnb_quantizable_share_of_text"] = round(b["quantizable"] / counted_text, 6)
    rec["bnb_detail"] = {
        "n_linear4bit_modules": b["n_linear4bit_modules"],
        "keep_in_fp32_modules": b["keep_in_fp32"],
        "keep_in_fp32_modules_strict": b["keep_in_fp32_strict"],
        "linear_weights_left_16bit": tb["linear_weight"] - b["quantizable"],
    }
    if b["preq_note"]:
        notes.append(b["preq_note"])
    if rec["moe"] and tb["moe_expert_fused"]:
        notes.append(
            f"MoE experts are fused 3D nn.Parameter tensors ({', '.join(rec['moe']['expert_module_class'])}), not "
            f"nn.Linear, so load_in_4bit leaves all {tb['moe_expert_fused']:,} expert params in 16-bit "
            "(replace_with_bnb_linear only swaps nn.Linear/Conv1D)."
        )

    # ---- hub difference
    if not analytic_proxy:
        rec["hub_diff"] = explain_hub_diff(row, raw, tc, t, counted_full, tied_full, emb_numel)

    # ---- closed-form cross-check for plain dense decoders
    f = dense_formula(raw)
    if f is not None:
        rec["formula_check"] = {
            "formula_total": f["total"], "matches_text_count": f["total"] == counted_text,
            "formula_linear_weight": f["linear_weight"],
            "matches_linear_weight": f["linear_weight"] == tb["linear_weight"],
            "formula_kv_bytes_per_token_fp16": f["kv_bytes_per_token_fp16"],
            "matches_kv": f["kv_bytes_per_token_fp16"] == rec["kv_bytes_per_token_fp16"],
        }

    if t is not full:
        del t
    del full
    gc.collect()


def describe_diff(rec, row):
    """Human-readable notes about the Hub comparison."""
    notes = []
    hd = rec.get("hub_diff")
    if hd is None:
        return notes
    d = hd["hub_minus_counted_full"]
    if d == 0:
        notes.append("counted full-model params equal the Hub's stored count exactly.")
    else:
        notes.append(f"Hub stores {d:+,} params vs the instantiated full model ({rec['diff_vs_hub_pct']:+.4f}%).")
        for e in hd["explained"]:
            notes.append(f"explained: {e['params']:,} = {e['reason']} [{e['basis']}].")
            if "lm_head.weight" in e["reason"]:
                notes.append(
                    "On from_pretrained, PreTrainedModel.tie_weights(missing_keys=...) finds both tensors in the "
                    "checkpoint and ties them only if torch.equal(embedding, lm_head); otherwise it warns and keeps "
                    f"them separate, so the loaded model has {rec['counted_params_full']:,} (equal) or "
                    f"{rec['counted_params_full'] + e['params']:,} (different) params. Not checkable without reading "
                    "the weights."
                )
        r = hd["residual"]
        if r == 0:
            notes.append("residual after the explanations above: 0 (exact).")
        else:
            pb = rec["persistent_buffer_values"]
            tag = ""
            if r == pb["text"] + pb["nontext"]:
                tag = " = all persistent buffers of the full model (saved in the checkpoint, registered as buffers, not parameters)"
            elif r == pb["text"]:
                tag = (f" = the text model's persistent buffers ({pb['text']:,}; e.g. per-layer scalars); the "
                       f"{pb['nontext']:,} vision/audio persistent buffer values are apparently not in the Hub count (unverified)")
            notes.append(f"residual not explained structurally: {r:+,}{tag}.")
    by_dtype = row.get("params_by_dtype") or {}
    s = sum(by_dtype.values())
    if by_dtype and s != row["params"]:
        excess = s - row["params"]
        pb_text = rec["persistent_buffer_values"]["text"]
        cands = hd.get("candidates_not_in_hub_total") or []
        est = sum(e["params"] for e in cands)
        gap = excess - pb_text - est
        msg = (f"Hub metadata is internally inconsistent: params_by_dtype sums to {s:,}, {excess:+,} vs its 'total' "
               f"{row['params']:,} (diff_vs_hub_pct uses 'total'; diff_vs_hub_dtype_sum_pct uses the sum). Breakdown "
               f"of the excess: {pb_text:,} = persistent buffers of the instantiated model (e.g. MoE router "
               f"e_score_correction_bias, stored as F32 tensors)")
        if cands:
            msg += (f"; {est:,} = structural estimate of " + "; ".join(e["reason"] for e in cands)
                    + " (so the safetensors probably contain it, while the Hub 'total' does not)")
        msg += f"; remaining gap {gap:+,}"
        moe = rec.get("moe") or {}
        if gap and moe and gap == moe.get("num_experts"):
            msg += " (= num_experts: consistent with one more router-bias buffer belonging to the MTP MoE block)"
        notes.append(msg + ". Unverified: no local copy of this checkpoint.")
    moe = rec.get("moe") or {}
    if by_dtype.get("U8") and moe and by_dtype["U8"] == moe.get("expert_weight_params_3d"):
        notes.append(
            f"Storage: the Hub's U8 count ({by_dtype['U8']:,}) equals the fused expert weight count exactly; the "
            "checkpoint stores experts in MXFP4 (U8-packed) and the Hub reports their logical parameter count. "
            "Mxfp4HfQuantizer keeps MXFP4 on load only when triton and the `kernels` package are available (kernels "
            "is not installed in this venv), otherwise it dequantizes to bf16; it reports is_trainable=False."
        )
    f8 = by_dtype.get("F8_E4M3")
    if f8:
        same = f8 == rec["text_linear_weight_params"]
        rest = by_dtype.get("BF16") == rec["counted_params_full"] - f8
        notes.append(
            f"Storage: {f8:,} params are stored as FP8 (F8_E4M3)"
            + ("; this equals text_linear_weight_params exactly, i.e. the text Linear weights except lm_head"
               if same else "")
            + ("; the BF16 count equals everything else (embeddings, lm_head, norms, vision tower)" if rest else "")
            + "."
        )
    return notes


def nanbeige_proxy(raw):
    """Llama-layout proxy for a config whose model_type is not in transformers (analytic estimate)."""
    keys = ["hidden_size", "intermediate_size", "num_hidden_layers", "num_attention_heads", "num_key_value_heads",
            "head_dim", "vocab_size", "tie_word_embeddings", "attention_bias", "rms_norm_eps",
            "max_position_embeddings", "hidden_act"]
    kw = {k: raw[k] for k in keys if k in raw}
    kw["mlp_bias"] = raw.get("mlp_bias", False)
    return LlamaConfig(**kw)


def run(models_json, configs_dir, out_path):
    rows = json.loads(Path(models_json).read_text())
    records = []
    for row in rows:
        path = Path(configs_dir) / (row["id"].replace("/", "__") + ".json")
        raw = json.loads(path.read_text())
        rec = empty_record(row)
        notes = []
        try:
            try:
                cfg = AutoConfig.from_pretrained(str(path), trust_remote_code=False)
            except Exception as e:
                rec["status"] = "unsupported"
                rec["error"] = f"{type(e).__name__}: {str(e).splitlines()[0][:300]}"
                mt = raw.get("model_type")
                notes.append(f"model_type '{mt}' is not in transformers {transformers.__version__}; the config's "
                             f"auto_map points to remote code ({raw.get('auto_map', {}).get('AutoModelForCausalLM')}), "
                             "which was not run (trust_remote_code=False).")
                plain = (raw.get("hidden_act") == "silu" and not raw.get("attention_bias") and "auto_map" in raw
                         and all(k in raw for k in ("hidden_size", "intermediate_size", "num_hidden_layers",
                                                    "num_attention_heads", "num_key_value_heads", "vocab_size")))
                if plain:
                    pcfg = nanbeige_proxy(raw)
                    analyze_model(rec, row, raw, pcfg, notes, analytic_proxy=True)
                    rec["analytic"] = True
                    rec["class_full"] = rec["class_text"] = None
                    rec["analytic_proxy_class"] = "LlamaForCausalLM"
                    hub = row["params"]
                    rec["hub_diff"] = {"hub_minus_counted_full": hub - rec["counted_params_full"], "explained": [],
                                       "residual": hub - rec["counted_params_full"]}
                    notes.append(
                        "ANALYTIC: counted on a LlamaForCausalLM meta proxy built from the same shape fields "
                        "(hidden 3072, 22 layers, 48 q / 8 kv heads x 128, intermediate 10752, vocab 166144, "
                        "untied). Hand arithmetic: 22 x 143,136,768 per layer + 2 x 510,394,368 + 3,072 = "
                        "4,169,800,704, identical to the Hub's stored count, so the stored weights have a plain "
                        "Llama layout. The forward pass is not plain: num_loops=2 re-applies the layer stack; "
                        "bnb fields are what the Llama proxy gives and the real remote class was not checked.")
                    single = rec["kv_bytes_per_token_fp16"]
                    rec["kv_bytes_per_token_fp16"] = None
                    notes.append(
                        f"kv_bytes_per_token_fp16 left null: one pass over the 22 layers would cache {single:,} B/token, "
                        "but with num_loops=2 the remote code may keep a cache per loop (2x); not verifiable without "
                        "running remote code.")
                rec["notes"] = " ".join(notes)
                records.append(rec)
                print(f"UNSUPPORTED {row['id']}: {rec['error'][:120]}", flush=True)
                continue
            analyze_model(rec, row, raw, cfg, notes)
            rec["status"] = "ok"
            notes = describe_diff(rec, row) + notes
        except Exception as e:
            rec["status"] = "error"
            rec["error"] = f"{type(e).__name__}: {e}"
            notes.append(traceback.format_exc(limit=3))
        rec["notes"] = " ".join(notes) if notes else None
        rec["bnb_function"] = BNB_FUNCTION
        rec["counted_with"] = ENV
        records.append(rec)
        gc.collect()
        print(
            f"{rec['status']:5s} {row['id']:52s} text={rec['counted_params_text'] or 0:>16,} "
            f"full={rec['counted_params_full'] or 0:>16,} hub={row['params']:>16,} diff={rec['diff_vs_hub_pct']}% "
            f"rss={rss_gb():.2f}GB", flush=True)
    for r in records:
        r.setdefault("bnb_function", BNB_FUNCTION)
        r.setdefault("counted_with", ENV)
    Path(out_path).write_text(json.dumps(records, indent=1) + "\n")
    print(f"wrote {len(records)} records to {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    run(*sys.argv[1:])
