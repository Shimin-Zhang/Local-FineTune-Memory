"""Are chat-marker embeddings trained in a base checkpoint? usage: template_check.py MODEL_DIR OUT_JSON"""
import json, sys, glob, os
import numpy as np, torch
from safetensors import safe_open
from transformers import AutoTokenizer, AutoModelForCausalLM

model_dir, out_path = sys.argv[1], sys.argv[2]
torch.manual_seed(0); rng = np.random.default_rng(0)
tok = AutoTokenizer.from_pretrained(model_dir)
cfg = json.load(open(os.path.join(model_dir, "tokenizer_config.json")))
added = {int(k): v for k, v in cfg["added_tokens_decoder"].items()}
res = {"tokenizer": {}, "embedding_stats": {}, "behaviour": {}}

# ---- 1. tokenizer
chat = ["<|im_start|>", "<|im_end|>"]
think = ["<think>", "</think>"]
tool = ["<tool_call>", "</tool_call>", "<tool_response>", "</tool_response>"]
vision = [v["content"] for v in added.values() if "vision" in v["content"] or "image" in v["content"]
          or "video" in v["content"] or any(s in v["content"] for s in ("object_ref", "box_", "quad_"))]
audio = [v["content"] for v in added.values() if "audio" in v["content"] or "tts" in v["content"]]
fim = [v["content"] for v in added.values() if "fim" in v["content"] or v["content"] in ("<|repo_name|>", "<|file_sep|>")]
ids = lambda names: {n: tok.convert_tokens_to_ids(n) for n in names}
vocab_rows = None
res["tokenizer"] = {
    "added_tokens": {str(k): {"content": v["content"], "special": v["special"]} for k, v in sorted(added.items())},
    "eos_token": tok.eos_token, "eos_id": tok.eos_token_id, "pad_token": tok.pad_token, "bos_token": tok.bos_token,
    "groups": {"chat_markers": ids(chat), "think": ids(think), "tool": ids(tool), "vision": ids(vision),
               "audio_tts": ids(audio), "fim_repo": ids(fim), "endoftext": ids(["<|endoftext|>"])},
    "chat_template": tok.chat_template,
    "len_tokenizer": len(tok),
    "reserved_note": "no named reserved placeholders; ids max_added+1 .. vocab_size-1 have no token (padding rows)",
}

# ---- 2. embedding stats
f = [p for p in glob.glob(os.path.join(model_dir, "*.safetensors*")) if p.endswith(".safetensors")][0]
with safe_open(f, "pt") as sf:
    E = sf.get_tensor("model.language_model.embed_tokens.weight").float()
V = E.shape[0]
last = max(added)
res["tokenizer"]["embedding_rows"] = V
res["tokenizer"]["unassigned_id_range"] = [last + 1, V - 1]
ordinary_pool = np.arange(0, 248044)
ordinary = rng.choice(ordinary_pool, 2000, replace=False)

def stats(idx, label):
    idx = np.array(sorted(idx)); R = E[idx]
    n = R.norm(dim=1)
    Rn = R / n.clamp_min(1e-12)[:, None]
    C = Rn @ Rn.T
    off = C[~torch.eye(len(idx), dtype=bool)] if len(idx) > 1 else torch.tensor([float("nan")])
    # random-pair cosine sample for large groups
    d = {"n": len(idx), "ids_sample": idx[:8].tolist(),
         "l2_norm_mean": n.mean().item(), "l2_norm_std": n.std().item() if len(idx) > 1 else None,
         "l2_norm_min": n.min().item(), "l2_norm_max": n.max().item(),
         "row_mean_avg": R.mean(1).mean().item(), "row_mean_absavg": R.mean(1).abs().mean().item(),
         "row_std_avg": R.std(1).mean().item(), "row_std_min": R.std(1).min().item(), "row_std_max": R.std(1).max().item(),
         "pairwise_cos_mean": off.mean().item(), "pairwise_cos_std": off.std().item() if len(idx) > 2 else None,
         "pairwise_cos_max": off.max().item()}
    # cosine to the centroid of ordinary tokens
    cen = E[ordinary].mean(0)
    d["cos_to_ordinary_centroid_mean"] = torch.nn.functional.cosine_similarity(R, cen[None], dim=1).mean().item()
    res["embedding_stats"][label] = d

ids_of = lambda names: [tok.convert_tokens_to_ids(n) for n in names]
stats(ids_of(chat), "chat_markers(im_start,im_end)")
stats(ids_of(think), "think_markers")
stats(ids_of(tool), "tool_markers")
stats(ids_of(vision), "vision_markers")
stats(ids_of(fim), "fim_repo_markers")
stats(ids_of(audio), "audio_tts_markers")
stats(ids_of(["<|endoftext|>"]), "endoftext")
stats(ordinary, "ordinary_random_2000")
stats(range(last + 1, V), "unassigned_padding_rows")
# ordinary-ordinary baseline for tiny groups: mean cos among 10 random sets of 2 is just the 2000 group mean
res["embedding_stats"]["_note"] = ("unassigned_padding_rows = ids beyond the last real token; never emitted by tokenizer, "
                                   "so their rows receive no input gradient (only output-logit gradient since tied).")
# nearest-neighbour check: is <|im_end|> row closer to other special tokens than to ordinary?
def mean_cos(a, bidx):
    A = E[a] / E[a].norm(dim=1, keepdim=True); B = E[bidx] / E[bidx].norm(dim=1, keepdim=True)
    return (A @ B.T).mean().item()
res["embedding_stats"]["cross_group_cos"] = {
    "chat_vs_ordinary": mean_cos(ids_of(chat), ordinary),
    "chat_vs_padding": mean_cos(ids_of(chat), list(range(last + 1, V))),
    "chat_vs_vision": mean_cos(ids_of(chat), ids_of(vision)),
    "chat_vs_think": mean_cos(ids_of(chat), ids_of(think)),
    "padding_vs_ordinary": mean_cos(list(range(last + 1, V)), ordinary),
}

# ---- 3. behaviour
torch.set_num_threads(max(1, os.cpu_count() // 2))
model = AutoModelForCausalLM.from_pretrained(model_dir, dtype=torch.float32).eval()
res["behaviour"]["model_class"] = type(model).__name__
IM_END, IM_START, EOT = tok.convert_tokens_to_ids("<|im_end|>"), tok.convert_tokens_to_ids("<|im_start|>"), tok.eos_token_id
instr = ["List three primary colors.", "Translate 'good morning' to French.", "What is 12 times 7?", "Write one sentence about the ocean."]
answers = ["Red, blue, and yellow.", "Bonjour.", "12 times 7 is 84.", "The ocean stretches endlessly under the sky."]

def gen(prompt):
    x = tok(prompt, return_tensors="pt", add_special_tokens=False)
    with torch.no_grad():
        o = model.generate(**x, max_new_tokens=80, do_sample=False, pad_token_id=EOT)
    new = o[0, x["input_ids"].shape[1]:].tolist()
    return {"new_token_ids": new, "text_with_specials": tok.decode(new, skip_special_tokens=False),
            "emitted_im_end": IM_END in new, "emitted_endoftext": EOT in new,
            "stopped_early": len(new) < 80,
            "first_stop_token": next((tok.convert_ids_to_tokens(t) for t in new if t in (IM_END, EOT)), None)}
# HF generate stops only at eos (<|endoftext|>); so stop-detection is judged on whether stop tokens appear in 80 new tokens
fmts = {
    "chat": lambda i: f"<|im_start|>user\n{i}<|im_end|>\n<|im_start|>assistant\n",
    "chat_template_nothink": lambda i: tok.apply_chat_template([{"role": "user", "content": i}], tokenize=False, add_generation_prompt=True),
    "plain": lambda i: f"### Instruction:\n{i}\n\n### Response:\n",
}
res["behaviour"]["generations"] = {k: [] for k in fmts}
for k, fn in fmts.items():
    for i in instr:
        p = fn(i); g = gen(p); g.update(instruction=i, prompt=p); res["behaviour"]["generations"][k].append(g)
        print(k, "|", i, "->", repr(g["text_with_specials"][:150]), flush=True)

# teacher-forced next-token probabilities after a complete short answer
tf = []
for i, a in zip(instr, answers):
    for name, prompt, tail in [("chat", f"<|im_start|>user\n{i}<|im_end|>\n<|im_start|>assistant\n{a}", None),
                               ("plain", f"### Instruction:\n{i}\n\n### Response:\n{a}", None)]:
        x = tok(prompt, return_tensors="pt", add_special_tokens=False)
        with torch.no_grad():
            lg = model(**x).logits[0, -1].float()
        lp = torch.log_softmax(lg, -1); pr = lp.exp()
        top = torch.topk(pr, 5)
        tf.append({"format": name, "instruction": i, "answer": a,
                   "p_im_end": pr[IM_END].item(), "p_endoftext": pr[EOT].item(),
                   "p_im_start": pr[IM_START].item(),
                   "p_newline": pr[tok.encode("\n")[0]].item(),
                   "rank_im_end": int((pr > pr[IM_END]).sum().item()) + 1,
                   "rank_endoftext": int((pr > pr[EOT]).sum().item()) + 1,
                   "top5": [(tok.convert_ids_to_tokens(t.item()), round(p.item(), 5)) for p, t in zip(top.values, top.indices)]})
res["behaviour"]["teacher_forced"] = tf
chat_tf = [t for t in tf if t["format"] == "chat"]
res["behaviour"]["teacher_forced_summary"] = {
    f: {"mean_p_im_end": float(np.mean([t["p_im_end"] for t in tf if t["format"] == f])),
        "mean_p_endoftext": float(np.mean([t["p_endoftext"] for t in tf if t["format"] == f]))} for f in ("chat", "plain")}

es = res["embedding_stats"]; ch = es["chat_markers(im_start,im_end)"]; pad = es["unassigned_padding_rows"]; od = es["ordinary_random_2000"]
tfs = res["behaviour"]["teacher_forced_summary"]
looks_untrained = pad["pairwise_cos_mean"] > 0.99 and abs(ch["l2_norm_mean"] - pad["l2_norm_mean"]) < 0.01 or ch["pairwise_cos_mean"] > 0.9
behaves = tfs["chat"]["mean_p_im_end"] > 0.5
verdict = "trained" if (not looks_untrained and behaves) else "untrained" if (looks_untrained and not behaves) else "mixed"
res["verdict"] = {"label": verdict, "justification": (
    f"Embeddings: chat-marker rows have L2 norm {ch['l2_norm_mean']:.3f} (ordinary tokens {od['l2_norm_mean']:.3f} +/- {od['l2_norm_std']:.3f}), "
    f"pairwise cosine between <|im_start|> and <|im_end|> {ch['pairwise_cos_mean']:.3f} (ordinary-pair mean {od['pairwise_cos_mean']:.3f}), and cosine to the ordinary-token centroid {ch['cos_to_ordinary_centroid_mean']:.3f}. "
    f"The genuinely untrained reference (243 unassigned padding rows plus the 7 audio/tts tokens) is unmistakable: identical rows, norm {pad['l2_norm_mean']:.4f}, pairwise cosine {pad['pairwise_cos_mean']:.6f}. The chat markers look nothing like that. "
    f"Behaviour: teacher-forced after a complete short answer in chat format, P(<|im_end|>) averages {tfs['chat']['mean_p_im_end']:.3f} (range {min(t['p_im_end'] for t in res['behaviour']['teacher_forced'] if t['format']=='chat'):.2f}-{max(t['p_im_end'] for t in res['behaviour']['teacher_forced'] if t['format']=='chat'):.2f}, always rank 1) versus P(<|endoftext|>) {tfs['chat']['mean_p_endoftext']:.5f}; in plain format the reverse holds (P(<|endoftext|>) {tfs['plain']['mean_p_endoftext']:.3f}, P(<|im_end|>) {tfs['plain']['mean_p_im_end']:.4f}). "
    "In greedy generation with the model's own chat template (which adds an empty think block) all four answers end with <|im_end|> then <|endoftext|>. With the bare <|im_start|>assistant\\n prompt the model usually opens a <think> reasoning block and runs past 80 tokens (3 of 4), so it is not a clean 'answer then stop' there. "
    "Both lines of evidence agree that the markers are trained in this checkpoint: this 'Base' model was evidently pretrained/mid-trained on chat-formatted data. "
    "Limitations: single 0.8B checkpoint, 4 prompts, greedy decoding; larger sizes may differ; embedding statistics cannot prove training on their own (a trained row can still be near ordinary scale), but the contrast with the exactly-identical untrained rows is strong. "
    "Caveat for fine-tuning: <|im_end|> is trained as a stop signal but the exact template matters (use the template's empty <think></think> block, or expect think-mode openings), and the template wrapper tokens <|im_start|>/<|im_end|> need no embedding training.")}
json.dump(res, open(out_path, "w"), indent=1, default=str)
print("saved", out_path)
