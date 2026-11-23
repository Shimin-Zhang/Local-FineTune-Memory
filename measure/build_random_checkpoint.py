"""Build a random-weight bf16 checkpoint from a real config, for the 4-bit probes.

bitsandbytes quantizes inside from_pretrained, so the 4-bit probes need a checkpoint on disk.
Memory use does not depend on weight values, so random weights stand in for the real ones.
The output folder name matches what measure/probe.py looks for.

Usage (CPU only): CUDA_VISIBLE_DEVICES="" python -I measure/build_random_checkpoint.py <model_id> <config.json> [scratch_dir]
"""
import json, os, sys, time
import torch
from transformers import AutoConfig, AutoModelForCausalLM

model_id, config_path = sys.argv[1], sys.argv[2]
scratch = sys.argv[3] if len(sys.argv) > 3 else ".scratch"
out = os.path.join(scratch, "random", model_id.replace("/", "__") + "__base")
if os.path.exists(os.path.join(out, "config.json")):
    print("exists", out)
    sys.exit(0)
cfg = AutoConfig.from_pretrained(config_path)
tc = cfg.text_config if hasattr(cfg, "text_config") else cfg
t = time.time()
model = AutoModelForCausalLM.from_config(tc, dtype=torch.bfloat16)
t_init = time.time() - t
n = sum(p.numel() for p in model.parameters())
t = time.time()
model.save_pretrained(out)
t_save = time.time() - t
size = sum(os.path.getsize(os.path.join(out, f)) for f in os.listdir(out))
print(json.dumps({"model_id": model_id, "out": out, "params": n, "init_seconds": round(t_init, 1),
                  "save_seconds": round(t_save, 1), "disk_bytes": size, "class": type(model).__name__}))
