"""Build catalog/models.json from Hugging Face metadata and each model's config.json.

Usage: python catalog/build_catalog.py catalog/model_ids.txt catalog
No token is used. Gated repos (Llama, Gemma 3) fall back to the ungated unsloth mirror
for config.json; the parameter count always comes from the original repo's metadata.
"""
import json, sys, time, urllib.request, urllib.error
from pathlib import Path

UA = {"User-Agent": "catalog-builder"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:  # network hiccup
        return 0, str(e).encode()


def fetch_config(repo):
    for cand in (repo, "unsloth/" + repo.split("/", 1)[1]):
        code, body = get(f"https://huggingface.co/{cand}/resolve/main/config.json")
        if code == 200:
            return cand, json.loads(body)
    return None, None


def first(d, *keys):
    for k in keys:
        if d.get(k) is not None:
            return d[k]
    return None


def normalize(cfg):
    t = cfg.get("text_config") or cfg
    hidden = first(t, "hidden_size", "d_model", "n_embd")
    heads = first(t, "num_attention_heads", "n_head")
    head_dim = first(t, "head_dim") or (hidden // heads if hidden and heads else None)
    return {
        "model_type": cfg.get("model_type"),
        "text_model_type": t.get("model_type"),
        "architecture": (cfg.get("architectures") or [None])[0],
        "n_layers": first(t, "num_hidden_layers", "n_layer"),
        "hidden": hidden,
        "intermediate": first(t, "intermediate_size", "ffn_dim"),
        "n_heads": heads,
        "n_kv_heads": first(t, "num_key_value_heads") or heads,
        "head_dim": head_dim,
        "vocab": first(t, "vocab_size"),
        "tie_word_embeddings": first(t, "tie_word_embeddings") if "tie_word_embeddings" in t else cfg.get("tie_word_embeddings"),
        "hidden_act": first(t, "hidden_act", "hidden_activation"),
        "max_positions": first(t, "max_position_embeddings"),
        "moe_num_experts": first(t, "num_experts", "num_local_experts", "n_routed_experts"),
        "moe_experts_per_token": first(t, "num_experts_per_tok", "experts_per_token", "num_experts_per_token"),
        "moe_intermediate": first(t, "moe_intermediate_size"),
        "n_full_attention_layers": (t.get("layer_types") or []).count("full_attention") or None,
        "n_linear_attention_layers": (t.get("layer_types") or []).count("linear_attention") or None,
        "has_vision": "vision_config" in cfg,
        "has_audio": "audio_config" in cfg,
    }


def main(ids_path, out_dir):
    out_dir = Path(out_dir)
    (out_dir / "configs").mkdir(parents=True, exist_ok=True)
    rows = []
    for line in Path(ids_path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        family, repo = [x.strip() for x in line.split("|")]
        code, body = get(f"https://huggingface.co/api/models/{repo}")
        if code != 200:
            print(f"SKIP {repo}: api {code}")
            continue
        info = json.loads(body)
        st = info.get("safetensors") or {}
        cfg_repo, cfg = fetch_config(repo)
        row = {
            "id": repo,
            "family": family,
            "params": st.get("total"),
            "params_by_dtype": st.get("parameters"),
            "gated": info.get("gated"),
            "license": (info.get("cardData") or {}).get("license"),
            "downloads_30d": info.get("downloads"),
            "likes": info.get("likes"),
            "created": (info.get("createdAt") or "")[:10],
            "pipeline_tag": info.get("pipeline_tag"),
            "config_source": cfg_repo,
        }
        if cfg is None:
            print(f"NOCFG {repo}")
        else:
            (out_dir / "configs" / (repo.replace("/", "__") + ".json")).write_text(json.dumps(cfg, indent=1))
            row.update(normalize(cfg))
        rows.append(row)
        p = row["params"]
        print(f"ok {repo:55s} params={p/1e9 if p else float('nan'):7.2f}B L={row.get('n_layers')} d={row.get('hidden')} ff={row.get('intermediate')} "
              f"vocab={row.get('vocab')} type={row.get('model_type')} cfg={cfg_repo}")
        time.sleep(0.15)
    (out_dir / "models.json").write_text(json.dumps(rows, indent=1))
    print(f"\nwrote {len(rows)} models to {out_dir/'models.json'}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
