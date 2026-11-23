"""QLoRA fine-tune of a chat model on (request, reply) pairs, inside a fixed budget of tokens per step.

Usage: python -I finetune/train_qlora.py --model <dir with the checkpoint> --train train.jsonl --val val.jsonl --out <dir>
           [--epochs 3] [--tokens-per-step 2048] [--max-example-tokens N] [--lr 1e-4] [--rank 16] [--max-steps N] [--val-every 100] [--save-every N]

Each line of the data files is {"id", "kind", "system", "user", "assistant"}. With "may_truncate": true, a reply too
long for the budget is cut to fit and trained without its end marker (the loss on the part that fits is still valid;
the model is not taught to stop early). Other examples that do not fit are left out and counted. The budget for one
example is --tokens-per-step unless --max-example-tokens sets a larger one: such an example is a step on its own and
costs more memory than any other step (about 1.7 to 2 GiB per thousand tokens on the 27B).

The memory recipe is the one measured in measure/probe.py for this card: frozen base in 4-bit (bitsandbytes NF4),
LoRA on every linear layer, 16-bit autocast, gradient checkpointing, and the loss computed a slice of positions at a
time so the full tokens-by-vocabulary table never exists. A step is one batch of examples of similar length, padded
on the right, with batch size times padded length at most --tokens-per-step. The loss is taken on the reply only.

Writes to --out: log.jsonl (one line per step and per validation pass), run.json, and the adapter after every epoch
(epoch1/, epoch2/, ...; with --save-every also step<N>/). Run in isolated mode (-I); this file has no local imports.
"""
import argparse, gc, json, math, os, random, sys, time

p = argparse.ArgumentParser()
p.add_argument("--model", required=True); p.add_argument("--train", required=True); p.add_argument("--val", required=True)
p.add_argument("--out", required=True)
p.add_argument("--epochs", type=int, default=3); p.add_argument("--tokens-per-step", type=int, default=2048)
p.add_argument("--max-batch", type=int, default=24)
p.add_argument("--max-example-tokens", type=int, default=0, help="let one long example exceed --tokens-per-step, as a step on its own")
p.add_argument("--lr", type=float, default=1e-4); p.add_argument("--warmup-steps", type=int, default=30)
p.add_argument("--rank", type=int, default=16); p.add_argument("--dropout", type=float, default=0.05)
p.add_argument("--targets", default="all-linear")
p.add_argument("--clip", type=float, default=1.0); p.add_argument("--loss-chunk", type=int, default=128)
p.add_argument("--max-steps", type=int, default=0, help="stop early (for a smoke test)")
p.add_argument("--val-every", type=int, default=100); p.add_argument("--seed", type=int, default=0)
p.add_argument("--save-every", type=int, default=0, help="also save the adapter every N steps (step<N>/), so a crash late in a long run leaves something")
args = p.parse_args()
os.makedirs(args.out, exist_ok=True)
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")  # batches change shape every step

import torch
import transformers, peft, bitsandbytes
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, PeftModel, get_peft_model

torch.manual_seed(args.seed)
T0 = time.time()
LOG = open(os.path.join(args.out, "log.jsonl"), "a")


def log(**rec):
    rec["minutes"] = round((time.time() - T0) / 60, 2)
    LOG.write(json.dumps(rec) + "\n"); LOG.flush()
    print(json.dumps(rec), flush=True)


# ---------------------------------------------------------------------------------------------------------- data
tok = AutoTokenizer.from_pretrained(args.model)
PAD = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
END = "<|im_end|>"


def prompt_text(ex):
    return f"<|im_start|>system\n{ex['system']}<|im_end|>\n<|im_start|>user\n{ex['user']}<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"


def encode(ex, budget):
    """(token ids, number of prompt tokens, was cut) or None if it does not fit."""
    pr = tok(prompt_text(ex), add_special_tokens=False).input_ids
    tg = tok(ex["assistant"] + END, add_special_tokens=False).input_ids
    cut = False
    if len(pr) + len(tg) > budget:
        if not ex.get("may_truncate") or budget - len(pr) < 256:
            return None
        tg, cut = tg[:budget - len(pr)], True
    return pr + tg, len(pr), cut


def load(path, budget):
    out, left_out, cut = [], 0, 0
    for line in open(path):
        ex = json.loads(line)
        enc = encode(ex, budget)
        if enc is None:
            left_out += 1
            continue
        cut += enc[2]
        out.append({"id": ex["id"], "kind": ex["kind"], "ids": enc[0], "n_prompt": enc[1]})
    return out, left_out, cut


LONGEST = max(args.tokens_per_step, args.max_example_tokens)
train, train_left_out, train_cut = load(args.train, LONGEST)
val, val_left_out, val_cut = load(args.val, LONGEST)
# the prompt must be exactly what the tokenizer's own chat template produces with thinking off
first = json.loads(open(args.train).readline())
ref = tok.apply_chat_template([{"role": "system", "content": first["system"]}, {"role": "user", "content": first["user"]}],
                              tokenize=False, add_generation_prompt=True, enable_thinking=False)
assert ref == prompt_text(first), "prompt format differs from the chat template:\n" + repr(ref[-200:]) + "\n" + repr(prompt_text(first)[-200:])


def batches(examples, rng=None):
    """Lists of examples of similar length with batch size x longest <= the token budget."""
    key = (lambda e: (len(e["ids"]) // 48, rng.random())) if rng else (lambda e: (len(e["ids"]), 0))
    out, cur = [], []
    for e in sorted(examples, key=key):
        longest = max([len(x["ids"]) for x in cur] + [len(e["ids"])])
        if cur and ((len(cur) + 1) * longest > args.tokens_per_step or len(cur) >= args.max_batch):
            out.append(cur); cur = []
        cur.append(e)
    if cur:
        out.append(cur)
    if rng:
        rng.shuffle(out)
    return out


def tensors(batch):
    L = max(len(e["ids"]) for e in batch)
    ids = torch.full((len(batch), L), PAD, dtype=torch.long)
    mask = torch.zeros((len(batch), L), dtype=torch.long)
    labels = torch.full((len(batch), L), -100, dtype=torch.long)
    for i, e in enumerate(batch):
        n = len(e["ids"])
        ids[i, :n] = torch.tensor(e["ids"]); mask[i, :n] = 1
        labels[i, e["n_prompt"]:n] = torch.tensor(e["ids"][e["n_prompt"]:])
    return ids.cuda(), mask.cuda(), labels.cuda()


steps_per_epoch = len(batches(train, random.Random(0)))
total_steps = args.max_steps or steps_per_epoch * args.epochs
kinds = sorted({e["kind"] for e in train})
log(event="data", train_examples=len(train), train_left_out=train_left_out, train_cut_to_fit=train_cut, val_examples=len(val),
    val_left_out=val_left_out, train_tokens=sum(len(e["ids"]) for e in train), train_reply_tokens=sum(len(e["ids"]) - e["n_prompt"] for e in train),
    by_kind={k: sum(e["kind"] == k for e in train) for k in kinds}, steps_per_epoch=steps_per_epoch, total_steps=total_steps,
    longest_example=max(len(e["ids"]) for e in train), examples_over_step_budget=sum(len(e["ids"]) > args.tokens_per_step for e in train))

# --------------------------------------------------------------------------------------------------------- model
qc = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16)
t = time.time()
model = AutoModelForCausalLM.from_pretrained(args.model, quantization_config=qc, dtype=torch.bfloat16, device_map={"": 0})
for prm in model.parameters():
    prm.requires_grad = False
model.gradient_checkpointing_enable()
targets = args.targets if args.targets == "all-linear" else args.targets.split(",")
model = get_peft_model(model, LoraConfig(r=args.rank, lora_alpha=2 * args.rank, lora_dropout=args.dropout, target_modules=targets, task_type="CAUSAL_LM"))
causal = model.get_base_model()
body, head = getattr(causal, causal.base_model_prefix), causal.get_output_embeddings()
trainable = [q for q in model.parameters() if q.requires_grad]
opt = torch.optim.AdamW(trainable, lr=args.lr, weight_decay=0.0)
import importlib.util as _u
json.dump({"args": vars(args), "versions": {"torch": torch.__version__, "transformers": transformers.__version__, "peft": peft.__version__,
                                              "bitsandbytes": bitsandbytes.__version__},
           "kernels": {"linear_attention": "fla" if _u.find_spec("fla") else "torch fallback",
                       "causal_conv": "causal_conv1d" if _u.find_spec("causal_conv1d") else "torch fallback"},
           "gpu": torch.cuda.get_device_name(0), "trainable_parameters": sum(q.numel() for q in trainable),
           "model_class": type(causal).__name__}, open(os.path.join(args.out, "run.json"), "w"), indent=1)
log(event="model", load_seconds=round(time.time() - t, 1), trainable_parameters=sum(q.numel() for q in trainable),
    gpu_gib_after_load=round(torch.cuda.memory_allocated() / 2 ** 30, 2))


def lr_at(step):
    if step < args.warmup_steps:
        return args.lr * (step + 1) / args.warmup_steps
    done = (step - args.warmup_steps) / max(1, total_steps - args.warmup_steps)
    return args.lr * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * min(1.0, done))))


def reply_loss(batch, train_mode):
    """Mean cross-entropy over the reply tokens of the batch. In training mode it also leaves gradients on the adapter."""
    ids, mask, labels = tensors(batch)
    want = labels[:, 1:].reshape(-1)                       # position t predicts token t+1
    where = (want != -100).nonzero(as_tuple=True)[0]
    n = where.numel()
    with torch.autocast("cuda", dtype=torch.bfloat16):
        hidden = body(input_ids=ids, attention_mask=mask).last_hidden_state
    flat = hidden[:, :-1].reshape(-1, hidden.shape[-1])
    src = flat.detach().requires_grad_(True) if train_mode else flat
    total = 0.0
    for a in range(0, n, args.loss_chunk):                 # logits for a slice of positions at a time
        idx = where[a:a + args.loss_chunk]
        with torch.autocast("cuda", dtype=torch.bfloat16):
            lg = head(src[idx])
        lc = torch.nn.functional.cross_entropy(lg.float(), want[idx], reduction="sum") / n
        if train_mode:
            lc.backward()
        total += float(lc.detach())
        del lg, lc
    if train_mode:
        flat.backward(src.grad)
    return total, n, ids.numel()


def validate(step):
    model.eval()
    by, t = {}, time.time()
    with torch.no_grad():
        for b in batches(val):
            for e in b:                                    # one example at a time, so the loss can be split by kind
                loss, n, _ = reply_loss([e], False)
                s = by.setdefault(e["kind"], [0.0, 0])
                s[0] += loss * n; s[1] += n
    model.train()
    out = {k: round(v[0] / v[1], 4) for k, v in sorted(by.items())}
    out["all"] = round(sum(v[0] for v in by.values()) / sum(v[1] for v in by.values()), 4)
    log(event="val", step=step, loss=out, seconds=round(time.time() - t, 1))
    return out


def train_step(batch, step):
    for g in opt.param_groups:
        g["lr"] = lr_at(step)
    opt.zero_grad(set_to_none=True)
    loss, n, cells = reply_loss(batch, True)
    norm = float(torch.nn.utils.clip_grad_norm_(trainable, args.clip))
    opt.step()
    return loss, n, cells, norm


model.train()
validate(0)
step, rng, ooms, validated_at = 0, random.Random(args.seed), 0, 0
torch.cuda.reset_peak_memory_stats()
for epoch in range(1, args.epochs + 1):
    for batch in batches(train, rng):
        t, oom = time.time(), False
        try:
            loss, n, cells, norm = train_step(batch, step)
        except torch.OutOfMemoryError:
            oom = True                                     # handled below, once the failed step's tensors are released
        if oom:
            ooms += 1
            opt.zero_grad(set_to_none=True); gc.collect(); torch.cuda.empty_cache()
            if len(batch) > 1:                             # the same examples in two smaller steps
                half = len(batch) // 2
                train_step(batch[:half], step)
                loss, n, cells, norm = train_step(batch[half:], step)
            else:                                          # one long example: train on its first three quarters
                e = dict(batch[0]); e["ids"] = e["ids"][:len(e["ids"]) * 3 // 4]
                loss, n, cells, norm = train_step([e], step)
            log(event="out_of_memory_recovered", step=step, batch=len(batch), longest=max(len(e["ids"]) for e in batch))
        step += 1
        if step % 10 == 0 or step == 1:
            log(event="step", step=step, epoch=epoch, loss=round(loss, 4), lr=round(lr_at(step - 1), 7), batch=len(batch), cells=cells, reply_tokens=n,
                grad_norm=round(norm, 3), seconds=round(time.time() - t, 2), peak_gib=round(torch.cuda.max_memory_reserved() / 2 ** 30, 2))
        if step % args.val_every == 0 and step < total_steps:
            validate(step); validated_at = step
        if args.save_every and step % args.save_every == 0 and step < total_steps and step % steps_per_epoch:
            model.save_pretrained(os.path.join(args.out, f"step{step}"))
            log(event="saved", step=step)
        if step >= total_steps:
            break
    if validated_at != step:                               # not twice when an epoch ends on a validation step
        validate(step)
    model.save_pretrained(os.path.join(args.out, f"epoch{epoch}"))
    log(event="saved", epoch=epoch, step=step)
    if step >= total_steps:
        break
log(event="done", steps=step, out_of_memory_recoveries=ooms, peak_reserved_gib=round(torch.cuda.max_memory_reserved() / 2 ** 30, 2))
