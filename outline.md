# How big a model can you fine-tune locally? (outline)

Status: 2026-11-11. Memory measurements are done (see `results/`). Numbers below are measured on one RTX 4090 unless marked "predicted" or "arithmetic". All memory is in GiB and is the highest memory the training process held. The fine-tunes themselves have not been run.

Every probe was run twice: once on a default install, and once with the two optional fast kernels for Qwen3.5-family models (`flash-linear-attention` and `causal-conv1d`). The numbers below use the fast-kernel runs unless they say "default install".

## Audience

People who use LLMs, perhaps run one locally, and have never had to think about what training holds in memory. Not local-LLM specialists. Lead with plain statements; put mechanism names and citations in sidebars. The value is usefulness, not novelty: most of these effects are documented somewhere, and none of the calculators we surveyed model them.

## The post is a trip

There is no moral. You have a model you run, and you want to change how it behaves. The post walks from running it to training it, one trick at a time. Each stop answers the same four questions:

1. What is the trick?
2. What makes it tick: which line of the memory bill does it remove, and why is that allowed?
3. How much does it save? (measured)
4. What does it cost? (speed measured; effect on the result to be measured by the fine-tune)

The trip ends with an actual fine-tune.

## Fixed setup

- **Machine:** RTX 4090, 24 GB (23.99 GiB). The desktop held 0.9 to 1.9 GiB of it during the runs, leaving 22.1 to 23.1 GiB.
- **The model you run:** `Qwen/Qwen3.8-27B`. 26.90B text parameters (27.78B stored, including a vision tower and a draft-prediction head that text-only training never loads), 64 layers, width 5,120, vocabulary 248,320.
- **Smaller models from the same family**, used wherever the 27B cannot show a before and an after on this card: Qwen3.5 0.8B, 2B, 4B, 9B, plus Qwen3-14B and Nanbeige4.3-33B.
- **Step size:** 4,096 tokens per step (2,048-token cap x micro-batch 2) unless stated.
- **Method:** random weights built from each model's real config. Checked against the real Qwen3.5-0.8B-Base checkpoint: identical in every memory field (14 probe pairs, 174 fields, 0.00 MiB apart).

## The stops

### 0. Where you start: running it

- 4-bit GGUF in llama.cpp: 16.7 at 4k context, 18.5 at 32k. Largest context that loads: 73,728 tokens (21.0).
- In memory: 4-bit weights, a KV cache of exactly 64 KiB per token, runtime.
- Inference keeps nothing else. That is the contrast for everything after.

### 1. The bill for training

Not a trick: the reason the tricks exist. Training holds five things inference does not.

| Line | What it is | Scales with |
|---|---|---|
| Weights, at training precision | the original weights, not the GGUF | parameters |
| Gradients | one number per weight being updated | parameters being updated |
| Optimizer history | AdamW keeps two numbers per updated weight, plus one more while it steps | parameters being updated |
| Activations | every intermediate result of the forward pass, kept for the backward pass | tokens per step x model depth and width |
| Loss | a score for every vocabulary entry at every token, in several copies | tokens per step x vocabulary |

- Measured on the 0.8B, 16-bit: weights 1.40, gradients 1.40, optimizer history 2.80, step-time temporary 1.40. Five copies, 7.0 of the 7.1 in use at the optimizer step.
- For the 27B at 32-bit: 502 (predicted). Thirty times what it takes to run.
- With every default left on (32-bit, stock loss, no checkpointing), the 0.8B does not fit on the card at 4,096 tokens per step.

### 2. Train in 16-bit

- **Ticks because:** every number takes 2 bytes instead of 4, so every parameter-sized line halves.
- **Saves:** 0.8B full fine-tune 15.0 -> 8.7. 27B 502 -> 251 (predicted).
- **Costs:** nothing in speed (2.2x faster on the 0.8B). Updates smaller than 16-bit precision can be lost; effect on the result to be measured.
- Sidebar: "mixed precision" with 32-bit weights (15.8) does not save the parameter-sized lines.

### 3. Freeze the model, train an add-on (LoRA)

- **Ticks because:** a weight you never update needs no gradient and no optimizer history. Only the add-on has them, and it is 0.4% of the model (27B: 117M of 26.9B).
- **Saves:** four of the five copies. 0.8B 8.7 -> 2.9. 2B 20.0 -> 5.5. 27B 251 -> 57 (predicted).
- **Costs:** you steer the model through a narrow add-on. Effect on the result to be measured. Rank is the dial: cheap up to 16, expensive past 64 (9B: 10.9 at rank 16, 20.6 at rank 256).

### 4. Round the frozen model to 4 bits (QLoRA)

- **Ticks because:** frozen weights only need to be good enough to run, not precise enough to update.
- **Saves:** 2B 5.5 -> 3.5. 4B 11.2 -> 6.2. 9B 20.7 -> 10.9. 27B weights 50.1 -> 16.5.
- **Costs:** no speed cost measured. The model being steered is an approximation; effect on the result to be measured.
- **Fine print:** "4-bit" is 0.517 bytes per rounded weight, and the two vocabulary matrices are not rounded at all. On the 27B that is 11.3 of rounded weights plus 4.7 of vocabulary matrices (16.5 loaded), not the 12.5 the name suggests.

**The turn.** Those are the three famous tricks, and at 4,096 tokens per step nothing fits yet, not even the 0.8B. Every one of the seven models fails. The lines that are left scale with tokens, not with parameters.

### 5. Forget the forward pass and redo it (gradient checkpointing)

- **Ticks because:** the backward pass needs the forward pass's intermediate results, but not all at once. Keep a few, recompute the rest when needed.
- **Saves:** per-token cost on the 2B 3.3 -> 0.33 MiB. 2B LoRA at 4,096 tokens 17.7 -> 5.5.
- **Costs:** 19 to 26% slower (2B and 9B).

### 6. Grade the output in slices (chunked loss)

- **Ticks because:** the stock loss builds one table of tokens x vocabulary, in 32-bit, several times over: about 13 bytes x 248,320 x tokens. Grading 128 tokens at a time and discarding each slice gives the same loss and the same gradients (norms within 0.04%).
- **Saves:** 12 to 13 at 4,096 tokens with a 248k vocabulary, whatever the model size (7 on the 14B, whose vocabulary is 152k). 2B LoRA 18.2 -> 5.5.
- **Costs:** 13% slower on the 2B, 7% on the 9B, about 3% on the 27B (slice size not tuned). Needs a custom loss; the stock trainer does not do it.
- Sidebar: Apple's Cut Cross-Entropy paper.

### 7. Put fewer tokens in each step

- **Ticks because:** activations and loss scale with the tokens in one step, not with the dataset. Accumulating gradients over several small steps gives the large effective batch.
- **Saves:** per token, with stops 5 and 6 applied: 0.13 MiB on the 0.8B, 0.33 on the 2B, 0.55 on the 4B, 0.62 on the 9B, 1.19 on the 27B.
- **Costs:** nothing in memory. Examples longer than the cap are truncated, or trained as a step of their own (run 3 does this for its scenes). Accumulation itself was not measured.

### 8. Install the fast kernels

- **Ticks because:** Qwen3.5-family models use linear-attention layers that run on slow general-purpose code unless two optional packages are present.
- **Saves:** per-token memory down a quarter to a half (2B 0.46 -> 0.33 MiB, 27B 1.55 -> 1.19). Time: 1.5x to 2.4x faster at 4,096 tokens, 8.9x at 32,768.
- **Costs:** an install step and a five-minute compile. The first run holds about 1.6 extra while it compiles.
- No effect on models without those layers (Qwen3-14B: identical).

### 9. Small levers

- **Optimizer:** matters in full fine-tuning (2B: 20.0 with AdamW, 18.4 fused AdamW, 15.0 8-bit AdamW, 11.2 SGD), barely under LoRA (0.8B: 2.89 vs 2.77).
- **Rank:** see stop 3.

### 10. Arrival

- The 27B, with stops 3 to 8 applied: 21.6 at 2,048 tokens per step, about 620 tokens per second. 3,072 fails (predicted 22.6).
- On a default install: 1,536 tokens per step at about 400 tokens per second.
- The model you can run is the model you can fine-tune, with 0.5 to 1.5 to spare depending on what the desktop holds.

## What fits at each stop

Largest model that completed at 4,096 tokens per step.

| Tricks applied | Full, 32-bit | Full, 16-bit | LoRA | QLoRA |
|---|---|---|---|---|
| None of 5 and 6 | none | none | none | none |
| Checkpointing | none | 0.8B (19.4) | 2B (18.2) | 14B (21.2) |
| Chunked loss | none | 0.8B (17.1) | 2B (17.7) | 2B (14.4) |
| Both | 0.8B (15.0) | 2B (20.0) | 9B (20.7) | 14B (14.2) |

- Under checkpointing alone the 14B fits and the 9B does not: the 14B has the smaller vocabulary (152k against 248k).
- At 1,024 tokens per step the 27B completes with both (20.1); Nanbeige4.3-33B does not. With checkpointing alone the 27B is on the edge: it peaked at 22.6, completed in one run and failed in another.
- The same models win on a default install, up to 0.8 higher.

## Traps along the way

- **A recommended recipe that costs gigabytes.** PEFT's `prepare_model_for_kbit_training` upcasts the unrounded weights to 32-bit: +3.8 of weights on the 9B, and it fails outright on the 27B and 33B.
- **Models the 4-bit trick skips.** Stock bitsandbytes leaves mixture-of-experts weights at 16-bit, so "QLoRA" on Qwen3.6-35B-A3B would need about 66 (predicted from the library's conversion rule; not measured at full size).
- **Names.** Parameter counts in model names can understate what is stored (vision towers, untied vocabulary matrices).

## Other machines

Predicted with `analysis/predict.py`. For a 110 GiB budget: full 32-bit about 4B (79), full 16-bit about 9B (84), LoRA about 33B (71), QLoRA Llama-3.3-70B (52). Labelled as predictions. Predictor accuracy against the 4090 runs: fit-or-not correct for 63 of 63; on memory, the generic formula used for unmeasured models has a 6% median error (worst 35%, on a 2 GiB run); 16-bit full fine-tuning is under-predicted by 8 to 10% because of allocator slack.

## The fine-tune

The first plan (teach a base model to follow instructions, FineTome + IFEval) is out: Qwen3.5 "Base" checkpoints already answer in chat format. Two runs replace it: a narrow job, and a voice as the closing run. The narrow job is "Run 3" below (the name matches its folder, `results/finetune_v3/`), trained on a dataset of whole scenes written by a larger model; the voice run is not designed.

### Narrow job: drive Blender through its MCP server

Teach the model to use one tool well, rather than a general skill like text-to-SQL. In practice that is mostly writing correct `bpy` code for the `execute_blender_code` tool, on the Blender version installed here (5.2.3), following the server's own rules.

"Well" has to be scoreable without a human. Three automatic scores:

1. The code runs in Blender 5.2.3 without an error.
2. It follows the server's house rules (for example: colours go on shader node inputs, not `diffuse_color`; shader nodes are looked up by type, not name; no hard-coded enum strings).
3. The scene matches the request. Exact only for requests generated from a structured spec (objects, positions, colours, lights), where a script can compare scene to spec.

Constraints from the memory work:

- The server's tool definitions are about 6,200 tokens, and the 27B fits 2,048 tokens per step. So the training prompt leaves them out, and the comparison becomes: untuned model with the definitions in its prompt, against tuned model without them.
- Everything measured so far is text-only. Training on images loads the vision tower and spends step tokens on each image, so it would need new measurements.

The sandbox: every model-written script runs in a headless Blender 5.2.3 with a read-only filesystem and no network (`blender_task/run_sandboxed.py`), and is rendered through its own camera and lights and from two fixed views. One fact about this Blender shapes the checks: a colour set only on `material.diffuse_color` shows in the viewport but not in a render (a sphere coloured that way renders white), so the sandbox flags such materials.

**Where the training data comes from** (decided with Shimin, 2026-11-12): written, not converted: whole-scene scripts by a larger model (Claude Sonnet, as agents that write a script, run it in the sandbox, look at the render and fix it), in one look chosen by Shimin, a low-poly diorama with dramatic light and glow, 2,500 to 3,300 tokens each so that each trains whole. Guide and checks: `synth/`. Not for commercial use or for training a general model.

**The scene dataset so far** (`synth/`, `results/synth_v1/`).

- Requests (`synth/requests/`): 2,288 written by four agents over 44 categories of place; 2,253 kept after the overlap checks (a main subject at most twice, no two requests sharing nearly half their content words, nothing from the first test set). Split into 2,000 for training, 100 held out for testing (their main subjects appear in no training request) and 153 spare.
- Pilot: 40 scenes by two agents. All pass the checks; 39 ran the first time. Shimin looked at all 40: "not perfect, but should be good training data for the 27B".
- Wave 1 (2026-11-12): 25 agents, four at a time, 20 scenes each, giving 400 training scenes and all 100 test scenes. All 500 pass `synth/check.py` (runs without error, starting cube removed, every object has a material, the script's own camera shows the scene, no outside files, at most 3,300 tokens). By the writers' own records 490 first versions ran without error, and 128 first versions were over the token limit and were cut down. Scripts: median 3,108 tokens (2,253 to 3,299). Scenes: median 144 objects (58 to 723).
- The writers rated their own pictures from 1 to 5: 6 scenes at 2, 303 at 3, 189 at 4, 2 at 5. The usual complaints in their notes: the subject small in a wide scene, small props hard to read, glow burnt to white, mist and steam as flat blobs.
- Cost of wave 1: 5.47M tokens and 2 h 20 min, about 10,900 tokens a scene. The remaining 1,600 training scenes would take about 17.5M tokens and 7.5 hours at the same rate.
- Review sheets, one per batch of 20 (`results/synth_v1/sheets/`, not in git; `show/` holds the cleaner renders they are made from).
- Spot check of wave 1 (one batch sheet and the flagged scenes): the look holds across writers, but some scenes are cut off by the edge of their own picture. A pixel check (`own_view_edge_share` in `finetune/checks.py`: the share of the picture's edge covered by something other than the background) puts 48 of the 500 at 15% or more: 27 of the 400 training scenes and 21 of the 100 test scenes, 18 of those in two test batches. Another 105 touch the edge. The worst dozen are plainly cropped; nearer 15% it is the rim of the base that is clipped while the subject is whole. All 40 pilot scenes are under the limit. The check is now a failing rule in `synth/check.py` and the guide says so (`results/synth_v1/edge_share_wave1.json` has the value per scene).
- Shimin looked through all the wave 1 sheets: "they are all usable, even the cropped ones". The 48 flagged scenes were repaired anyway, so the set agrees with its own guide: three agents moved each camera back along its line of sight (one line changed per script, by 1.15 to 1.8 times), and a script then moved 7 of those cameras part of the way forward again where the scene had become small (`synth/tighten_camera.py`). All 500 now pass the checker with the cut-off rule. What the repair cost: where the base is much larger than what stands on it, the subject is now smaller in the picture; a smaller base would have been the better fix and was not tried. Before and after: `results/synth_v1/sheets/repair_before_after.png`. The checker also warns when a scene spans under 75% of its picture, so that the next writers do not overshoot the other way.
- Wave 2 (2026-11-12): the other 1,600 training scenes, by 80 agents in batches of 20 (`train_b21` to `train_b100`, list in `results/synth_v1/batches_wave2.json`), same writers' brief plus the two framing rules, four at a time. All 1,600 pass `synth/check.py`, run again by me after the writers finished (one script had been edited after its last run and was run again first). None is cut off by its picture; 150 (9%) touch the edge, against 31% touching or cut off in wave 1 before its repair; 8 span under 75% of their picture, and the median span is 91%. Scripts: median 3,077 tokens (2,033 to 3,300). Scenes: median 140 objects (8 to 852). Two writers (`train_b31`, `train_b68`) built each scene as a few meshes, one per material with many parts in each, so their scenes count 8 to 32 objects; their pictures are as detailed as the others.
- The writers' own records for wave 2: 1,460 first versions ran without error and 140 did not; 361 first versions were over the token limit (74 of the 80 writers gave a count); 318 scripts were left as first written, 852 were changed once, 320 twice, 99 three times and 11 four times. Ratings: 22 scenes at 2, 933 at 3, 632 at 4, 13 at 5. These records are approximate: one writer filled in the first-run field from the final run, and in about 20 batches some copies in `first/` were tidied (dead lines removed, a slip fixed) before they were first run, so `first/` holds the version that was first run and not always the first draft.
- Cost of wave 2: 16.80M tokens and 7 h 13 min, about 10,500 tokens a scene. Waves 1 and 2 together: 22.3M tokens and about 9.5 hours for 2,100 scenes.
- The finished set: 2,000 training scenes, one for every request in `synth/requests/train.jsonl`, and 100 test scenes. The training scripts hold 6.05M tokens (median 3,088 a script). Writers' ratings over the 2,000: 27 at 2, 1,172 at 3, 787 at 4, 14 at 5.
- How alike are one writer's scripts? Within a batch, a median 19% of a script's text is in lines that at least half of that writer's other scripts also have word for word (the imports, the line that empties the scene, material set-up, the aiming line from the guide). The highest batch is at 28%. The guide forbade a carried helper block; this is what was shared anyway.
- The training file (`synth/build_train.py` writes `results/finetune_v3/train.jsonl` and `val.jsonl`, rebuilt from the scenes, not in git): 2,000 scenes and 6.22M tokens as the trainer counts them (request, script and markers), median 3,172 a scene, longest 3,392. Every scene is longer than the 2,048-token step, so each is a step on its own: 2,000 steps a pass. The 100 test scenes are the validation file (307,000 tokens).
- Spot check of wave 2 (three batch sheets and the low-rated sheet, of 80): the look holds. Mist and fog are drawn as large see-through flat sheets that veil some scenes. Shimin reviews the sheets by eye.

**Run 3: the 27B on the scene dataset** (`results/finetune_v3/`; trained 2026-11-13 21:42 to 2026-11-14 03:41).

- **Recipe** (`finetune/train_qlora.py`): the stops of the trip, on the real 27B. Model in 4-bit (NF4), LoRA rank 16 on the attention and MLP projections (79.7 million trainable weights), gradient checkpointing, loss on the reply only and taken in slices, learning rate 1e-4 with warm-up and cosine decay, on the 2,000 scenes alone. Every scene is longer than the 2,048-token step, so each is a step of its own (`--max-example-tokens 4096`). Two passes, at Shimin's request, with the adapter saved after each, so one pass can be compared with two. 4,000 steps of one scene each.
- Why only the attention and MLP projections: LoRA on every linear layer (116.7 million weights) peaked 50 MB under the card's limit with the desktop running, and the tool that converts an adapter for llama.cpp cannot handle this architecture's linear-attention projections.
- The adapter runs in llama.cpp on top of the same 4-bit GGUF used everywhere else, so before and after differ by one flag. Checked against PyTorch on greedy outputs.
- A two-minute test on the six longest scenes first: they fit (peak 21.5 GiB, no out-of-memory recovery) and train at about 590 tokens a second, the same as short examples. So the estimate is about 6.3 hours for the two passes, validation included.
- Validation is the 100 held-out scenes, every 500 steps. Untuned, the loss on them is 0.619.
- Training took 5 h 59 min for the 4,000 steps (5.2 s a step; 23 min of it in the nine validations), a little under the estimate. Peak 21.5 GiB, no out-of-memory recovery.
- Loss on the 100 held-out scenes: 0.619 untuned, 0.395 after 500 steps, 0.384, 0.376, 0.370 at the end of the first pass, then 0.371, 0.368, 0.366 and 0.365 at the end of the second. Nine tenths of the first pass's gain (0.224 of 0.249) comes in its first quarter, and the second pass adds 0.005. The training loss, averaged over each 500 steps, goes 0.443, 0.397, 0.390, 0.377 in the first pass and 0.343, 0.335, 0.330, 0.330 in the second: on the second reading the model does better on scenes it has seen (0.33) than on ones it has not (0.365), and the held-out loss barely moves. It has not started to get worse.
- The trainer gained `--save-every` (an extra copy of the adapter every 500 steps here), so a crash late in a long run leaves something.
- The test that follows (`results/finetune_v3/run_chain.sh`): the 100 held-out requests written by the untuned 27B and by each pass's adapter, one sample each, run in the sandbox and laid side by side with the reference scene (`finetune/scene_sheet.py`); the dataset's own checker applied to what each wrote; and 50 everyday requests (`blender_task/prompts_eval50.json`: 18 that need a texture, 10 simple objects, 10 about lighting, 12 complex scenes; written before the scene dataset, none of them a diorama), three samples each, untuned against the two-pass adapter, to see what the scene training did to plain objects and materials. Each of those scripts is run in the sandbox and rendered through its own camera with its own lights, and from two fixed views under the same sun.

Results of run 3 (test run 2026-11-14 03:42 to 06:06; 2 h 24 min, of which 2 h 21 min on the GPU; then 17 min more for the 24 re-written replies below):

| 100 held-out scene requests, one script each | Untuned 27B | One pass | Two passes | Sonnet (the reference) |
|---|---|---|---|---|
| Script runs without error | 42 | 77 | 85 | 100 |
| Picture through its own camera that shows the scene and fits it | 1 | 76 | 84 | 100 |
| Picture that runs past the frame | 29 | 1 | 1 | 0 |
| Own camera shows nothing | 9 | 0 | 0 | 0 |
| No camera of its own | 3 | 0 | 0 | 0 |
| Passes the dataset's own checker | 0 | 66 | 80 | 100 |
| Median script length, tokens | 3,190 | 2,933 | 2,893 | 2,984 |

- **The headline.** The tuned 27B writes scenes in the dataset's look: a diorama on a base, flat colours, glowing lamps, a dark sky, framed by its own camera. On the sheets its pictures sit beside Sonnet's and are the same kind of picture; the untuned model's column is mostly errors, blank views and plain scenes that fill the frame. This is the before/after picture the earlier runs did not give. (Judged by me on eight rows; Shimin reviews the sheets.)
- **The untuned model's side, made fair.** With the test's limit of 4,096 tokens a reply, 24 of its 100 replies were cut off and 22 of those failed for that reason alone (36 ran). Those 24 were written again with a limit of 8,192 (`scenes/before_long/`): all finished, median 4,146 tokens, longest 7,643, and 8 ran. The table and the sheets use the second version for those 24. `scenes/report_numbers/` still has the first version (36 ran).
- "Runs past the frame" is the dataset's rule (a scene must fit its own picture), which the untuned model was never shown: a ground plane to the horizon is not a mistake for it. The same goes for the checker row: the limit of 3,300 tokens alone fails 45 of its replies.
- **What still goes wrong.** The untuned model's errors are mistakes about Blender: a colour given three numbers where four are needed (13 of the first 64), operator arguments that do not exist, names from other Blender versions. The tuned model's are mostly slips inside its own script: it defines helper functions as the training scripts do and later calls one with the arguments in the wrong order or uses a name for two things (17 of 23 errors after one pass, 10 of 15 after two; the commonest, 10 and 6 times, hands a function or a mesh to `materials.append`). Mistakes about Blender are down to 5 and 4, and one script on each side does not parse.
- **Writing, not reciting.** 47% of the lines of a tuned script occur word for word in some training script (median; lines of 25 characters and up). For Sonnet's own held-out scripts the figure is 40%, for the untuned model 2%. So the overlap is the set-up every scene shares (render settings, world, helper bodies), about as much as the writers share among themselves.
- **One pass or two.** Two passes: 85 run against 77, 80 pass the checker against 66, held-out loss 0.365 against 0.370. Request by request, 15 ran only after two passes and 7 only after one (sign test p = 0.13), with one sample per request. So two passes look better and it is not settled.
- **Speed.** The tuned model with the adapter loaded at run time wrote 146 tokens a second across six requests at once, the untuned model 175.

| The 50 everyday requests, three scripts each (150) | Untuned 27B | Run 3, two passes |
|---|---|---|
| Script runs without error | 77 | 113 |
| of the 30 simple-object scripts | 22 | 21 |
| of the 54 material scripts | 19 | 40 |
| of the 30 lighting scripts | 14 | 23 |
| of the 36 complex-scene scripts | 22 | 29 |
| With a procedural pattern in a material | 14 | 0 |
| With surface relief | 6 | 0 |
| Mean objects built | 21 | 92 |
| Mean script length, tokens | 1,799 | 2,428 |

- **The look took over everything.** Asked for "a yellow rubber duck", the run-3 model builds a duck on a pond with stones and four lights; "a blue car with four black wheels" gives a car on a night road with street lamps. Every one of its 113 running scripts has its own camera and at least two lights, and none has a procedural pattern or surface relief, which the untuned model used in 14 and 6. The dataset has flat colours only, so the model stopped reaching for texture nodes even when the request is "a rusty metal barrel".
- It runs more often than the untuned model overall (113 against 77), but on simple objects no more often (21 of 30 against 22): it writes 2,400 tokens where 1,200 did, and its errors are the helper slips above.
- Sheets: `results/finetune_v3/scenes/report_3way/scenes_1..5.png` (untuned, two passes, Sonnet), `scenes/report/scenes_1..5.png` (with the one-pass column), `eval50/report/sheet_*.png` (the 50 everyday requests; untuned against run 3). The scene sheets are not in git (large); `finetune/scene_sheet.py` rebuilds them.

**Film scenes, built over many runs** (`blender_task/agent_loop.py`, `blender_task/prompts_movies20.json`, `results/finetune_v3/movies/`). Asked for by Shimin on 2026-11-14 after the run-3 sheets: very complex scenes, the 27B allowed to use the tool and see its output, each session run until it is out of context; then: make them 20 famous film scenes and ask for detail explicitly.

- **The requests:** one famous moment from each of 20 films (the T. rex at the paddock fence, the bow of the Titanic, the bicycle across the moon, the binary sunset, ...). Each ends with "Be detailed: build every part of the scene, and keep adding and refining detail for as long as you can." There is no Sonnet reference for these.
- **The loop:** the model replies with one code block. That is the reply format the adapter was trained on, not the server's JSON tool calls, so both models get the same loop. The block runs in a sandboxed Blender whose scene is kept from run to run, as a live Blender behind a "run this Python" tool keeps it: Python variables are not kept, and whatever ran before an error stays. The model is then shown the error with its line, or "ran without error"; what the code printed; object and light counts; a 768-pixel picture through its own camera (a default view until it sets one up); and how much room is left. Then it writes the next block.
- **Seeing:** the pictures go through the model's vision part (`mmproj-F16.gguf`, 0.9 GB), which the single-script tests never loaded. One 768-pixel picture costs about 570 tokens.
- **Out of context** is 32,768 tokens. Two sessions side by side at that size, plus the vision part, fill the card (23.3 of 24.6 GB with the desktop). A session ends when fewer than 700 tokens are left for the next reply.
- **Limits:** one reply is capped at 8,192 tokens. A reply cut off by the cap is half a script, so it is not run, and the model is told to write a shorter step; the tokens are spent all the same. One run in Blender is stopped at 240 seconds, as in the single-script tests.
- **Sides:** the untuned 27B and the two-pass adapter of run 3, same seed. About 40 tokens a second per session with two running.

Results of the film-scene sessions (2026-11-14 10:11 to 15:16: 2 h 32 min untuned, 2 h 33 min tuned; all 40 sessions finished at the first start; one sample per scene):

| 20 film scenes, one session each | Untuned 27B | Run 3, two passes |
|---|---|---|
| Runs in Blender | 139 | 162 |
| Runs that ended in an error | 53 | 27 |
| First reply ran without an error | 3 | 12 |
| Sessions with at least one error-free run | 20 | 19 |
| Turn of the first error-free run, median | 3 | 1 |
| Replies cut off by the 8,192-token cap, not run | 6, in 5 sessions | 0 |
| Replies the model ended in the middle of its code | 7 | 0 |
| Runs stopped at 240 seconds | 4 | 0 |
| Lines of a script already in the script before it, median share | 0.32 | 0.99 |
| Consecutive scripts that are identical | 0 of 119 | 56 of 142 |
| Final picture black | 2 | 0 |
| Median reply, tokens | 3,336 | 3,162 |

- **The tuned model does not iterate.** Its first script that runs is its scene. Its second script changes about a tenth of the lines (median share repeated 0.91); from the fourth on, 77 of 102 scripts are at least 98% the script before, usually with nothing changed but the number in `random.seed`, raised by one. What that does depends on whether the script clears the scene first. In 13 sessions it does not, so every run stacks another copy of the scene on the last: Up goes 297, 634, 963 and on to 2,942 objects in nine runs, with 63 lights at the end, and in 5 sessions the stacked lights leave the final picture at least 1.3 times brighter than the first. In 5 sessions it clears and builds the same scene again each time. Jurassic Park stacks three times, then clears. In Jaws it sent the same failing script eight times (a function handed to `materials.append`, the slip from the single-script test). So the tuned side's object and light counts at the end say nothing about detail; `first_and_end_*.png` puts its first working run beside its last.
- **It does read the error message, mostly:** of the 8 sessions whose first reply failed, 7 reached a script that ran (three at the second turn, two at the third, one at the fourth, one at the sixth).
- **The untuned model does iterate, and pays for it.** 3 of its 20 first replies ran (13 ended in an error, 4 were cut off at the cap), and the median first working run is its third turn. After that its scripts are new code (median share repeated 0.32) and the scene grows: the object count rises in 70 of 80 error-free later runs. But 53 of 139 runs end in an error, and a late run can break the scene: two sessions end on a black picture (The Fellowship of the Ring, Up; Up had a good picture two runs earlier).
- **The pictures** (my look at 10 of the 20 rows; Shimin's review to come). Tuned: every one is the dataset's picture, a lit low-poly diorama on a floating base seen from above, in frame, with the film's props on it (the two tour cars in the rain, the house under its balloons, three gunmen in the stone circle). The film's shot is not attempted: Titanic is a whole ship seen from the side. Untuned: hit and miss, and when it hits it is closer to the shot, with the camera at eye level and a sky (the yellow road running to the Emerald City, the Marshmallow Man between the buildings, two figures at the bow against the sunset). Its misses: Jurassic Park and the cemetery nearly empty, two black.
- **A fault of the loop that hurt the untuned model.** A reply cut off by the cap stays in the conversation as a turn that ends in the middle of the code. Of the 7 replies the untuned model itself ended in the middle of its code, 6 came after such a turn (Jaws three times, Back to the Future twice, The Wizard of Oz once). My reading, not tested: it copies the cut-off turn it can see. The seventh (The Shining, first reply) had none before it and ended after a run of "1,0,1,0". The untuned Jaws session is lost to this: two capped replies, then three truncated ones, 20 objects. The fix is to leave a cut-off reply out of the conversation; the five sessions were not run again.
- **Why the tuned model repeats** (reading, not tested): every one of the 2,000 training examples is one request answered by one whole script: seed, helpers, materials, the build, camera, lights. The adapter learned that a reply is that. With its own script already in the conversation, the nearest reply of that shape is the same script. Whether it uses the picture at all cannot be told from these sessions.
- **What it says for the post:** the loop does not make the tuned model better. Narrow tuning bought a first draft that runs, in one look, and cost the model its second draft; the untuned model, given the loop, gets part of the way to a scene by itself. The single-script result of run 3 stands.
- Sheets (not in git; `finetune/session_sheet.py` rebuilds them): `results/finetune_v3/movies/report/finals_1..2.png` (the scene at the end, side by side), `first_and_end_1..2.png` (first working run beside the end, per model), `strips/<id>.png` (the picture after every run). Numbers: `report/session_summary.json`.

Open: text-only or with images; one tool call per request or a multi-step loop (inspect, act, look, fix). The film-scene sessions above are the first test of the loop: the model tuned on single scripts does not use it.

### Voice

One run of the 27B on Shimin's own writing. Corpus and scoring not designed yet.

## Notes on the measurements

- **Fast kernels vs default install.** 432 probes were run both ways. 15 changed outcome, all from failing to completing; 14 of them with at least 0.7 of margin, the other being the edge case above. Losses agree within 0.05% and gradient norms within 0.16%. Stock-loss runs with checkpointing peak in the loss, so the kernels do not change what those runs have in use at the peak.
- **Process memory includes allocator slack.** PyTorch reserves more than it uses: median 0.4, above 2 in some full fine-tuning runs, and 3.9 in one (0.8B, PEFT prep step, stock loss: 19.8 held, 15.5 in use, reproducible). `results/probes_tidy.csv` has both columns.
- **The desktop's share moved.** It held 1.4 to 1.9 during the default-install runs and 0.9 to 1.1 during the fast-kernel runs. Each probe records it.

## Open items

- Film-scene sessions done (above). Not decided: whether to teach the tuned model the loop (training examples that are sessions: script, result, then a fix or an addition), and whether to run the five untuned sessions hit by the cap fault again.
- Narrow job: run 3 on our own scene dataset is done and tested (above). Next: Shimin's review of the three-way sheets. Not decided: whether the post wants a model that keeps plain objects plain (mix scenes with plain-object and material examples, or put the look in the request), and whether to settle one pass against two with more samples.
- Seeded for later: improve the tuned model with the frozen base model as judge of its renders (pairwise preference as the reward).
- Design the voice run.
- Possible follow-up measurements: Apple's loss in place of the chunked one; a tool that quantizes MoE experts; gradient accumulation.
- Charts.
