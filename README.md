# local-finetune-memory

Measurements behind a blog post: how big a model can you fine-tune on a local machine, starting from
the model you can already run at 4-bit. Everything here was measured on one RTX 4090 (24 GB).

See `outline.md` for the post outline.

## Layout

| Path | What it is |
|---|---|
| `catalog/models.json` | The nine models this post uses (the seven measured, plus Qwen3.6-35B-A3B and Llama-3.3-70B, whose memory is predicted), with shapes parsed from their Hub configs |
| `catalog/configs/` | Their `config.json` files; the memory probes build random-weight models from these |
| `catalog/param_breakdown.json` | Exact parameter split per model (embedding, head, linear, vision), and the share bitsandbytes would quantize |
| `results/inference_llamacpp.json` | llama.cpp GPU memory for three local GGUF models across context sizes |
| `results/probes.jsonl` | One record per memory probe (training and PyTorch inference) |
| `results/probes_tidy.csv` | The same, flattened for charting (`analysis/export_tidy.py`) |
| `results/template_check.json` | Whether chat-marker tokens are trained in Qwen3.5-0.8B-Base |
| `results/archive/` | Records from earlier harness versions, kept for provenance |
| `blender_task/` | Blender tooling: the sandbox that runs and renders model-written scripts (`run_sandboxed.py`, `harness.py`), generation through llama.cpp (`generate.py`), the multi-run session loop (`agent_loop.py`), and the request lists (`prompts_*.json`) |
| `finetune/` | The fine-tune itself: train a QLoRA adapter on the 27B (`train_qlora.py`), compare before and after (`eval_report.py`, `scene_sheet.py`, `session_sheet.py`) |
| `results/finetune_v3/` | Run 3: the scenes as the trainer's files (`train.jsonl`, `val.jsonl`), the training log (`run3/log.jsonl`), and what the untuned and tuned model wrote for the 100 held-out scene requests (`scenes/`) and for 50 everyday requests (`eval50/`; the untuned model's scripts are in `eval50/before/`), with numbers and sheets in `report*/` |
| `results/finetune_v3/movies/` | 20 famous film scenes, each built over many runs by the untuned and by the tuned model: per scene the transcript, every step's script and result, and `session.json`; sheets in `report/` |
| `synth/` | Tooling for the scene dataset written by a larger model: the writers' guide (`guide.md`), the checker (`check.py`), the review-sheet builder (`sheet.py`), and the request writers' brief, categories and overlap checks (`requests/`) |
| `results/synth_v1/` (not in git) | The scenes, to be published as a Hugging Face dataset: `pilot_a`, `pilot_b` (40), then batches of 20: wave 1 is `train_b01` to `train_b20` and `test_b01` to `test_b05`, wave 2 is `train_b21` to `train_b100`. Each batch has `requests.json`, one `<id>.py` per request, its report, the writer's `manifest.jsonl`, and the first versions in `first/` (the version first run; a few were tidied before that run) |

## Units

Data files store raw bytes. Divide by 2**30 for GiB, the unit in which the card is "24 GB".

Three memory columns in `results/probes_tidy.csv` answer different questions:

- `process_peak_bytes`: the most the process held (PyTorch's peak reserved memory plus what the process
  holds outside PyTorch). This is the number to compare with the card, and the one the outline quotes.
- `peak_allocated_overall_bytes`: the most PyTorch had in use. The gap to the first column is allocator
  slack: median about 0.4 GiB, above 2 GiB in some full fine-tuning runs.
- `process_bytes_at_end`: what the process held when the probe finished. Equal to the peak in all but
  three runs, where the allocator returned memory after the peak.

## Reproducing

```bash
uv sync                                    # torch is pinned to the CUDA 12.6 build (see pyproject.toml)
uv run python catalog/build_catalog.py catalog/model_ids.txt catalog
CUDA_VISIBLE_DEVICES="" uv run python -I measure/build_random_checkpoint.py Qwen/Qwen3.5-0.8B-Base catalog/configs/Qwen__Qwen3.5-0.8B-Base.json
uv run python measure/run_matrix.py pilot  # see run_matrix.py for the other matrices
uv run python measure/run_matrix.py ladder --tag-suffix _k   # tag for runs with the fast kernels installed
uv run python analysis/export_tidy.py results/probes.jsonl results/probes_tidy.csv
uv run python analysis/predict.py fit        # activation coefficients fitted from the probes
uv run python analysis/predict.py validate   # predictions against measurements (--fallback for the default install)
uv run python analysis/predict.py budget 110 # what fits a 110 GiB budget (predicted)
```

## Fast kernels for Qwen3.5-family models

Qwen3.5/3.6/3.8 use linear-attention layers that fall back to slow PyTorch code unless two optional
packages are present. Both are in `pyproject.toml`:

- `flash-linear-attention`: installs from a wheel, no extra setup.
- `causal-conv1d`: source only. It compiles against the torch already in the environment, so it needs the
  CUDA toolkit: `CUDA_HOME=/usr/local/cuda-12.8 PATH=/usr/local/cuda-12.8/bin:$PATH uv sync` (about five minutes).

Records store which path ran (`linear_attention_kernel`, `causal_conv_kernel`). Probe tags ending in `_k`
were measured with both kernels; the same tags without the suffix used the fallback. The first run of a
model shape compiles Triton kernels and holds up to 1.6 GiB extra for that run; the runner repeats any run
whose memory outside PyTorch is above 550 MiB (it is 462 to 472 MiB otherwise). Two partial compiles that an
earlier, looser threshold missed were repeated by hand; their records carry a `note` field.

## The fine-tune

Run 3 trains Qwen3.8-27B (real weights, in `.models/`, not stored here) on the scene dataset alone (written by a
larger model, see below), two passes; results are in `outline.md` under "Run 3":

```bash
uv run python synth/build_train.py          # results/finetune_v3/train.jsonl (2,000 scenes), val.jsonl (100 held out)
uv run python -I finetune/train_qlora.py --model .models/Qwen3.8-27B --train results/finetune_v3/train.jsonl \
    --val results/finetune_v3/val.jsonl --out results/finetune_v3/run3 --epochs 2 --max-example-tokens 4096 \
    --targets q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj --val-every 500 --save-every 500   # 6 hours
bash results/finetune_v3/run_chain.sh       # convert both adapters; the 100 held-out requests and the 50 everyday ones; sheets, numbers
```

The film-scene sessions give the untuned and the tuned model 20 famous film scenes, each to build over many runs:

```bash
bash results/finetune_v3/run_movies.sh      # untuned, then the two-pass adapter, then the sheets; about 5 hours on the GPU
```

- One session (`blender_task/agent_loop.py`): the model replies with a code block; it runs in a sandboxed Blender that
  keeps the scene from run to run (`blender_task/session_step.py`); the model is shown the error or "ran", what the
  code printed, object and light counts and a picture of the scene, and writes the next block. The session ends when
  the next reply would not fit in the context (32,768 tokens).
- The server loads the model's vision part (`mmproj-F16.gguf`) so that it can see the pictures. Two sessions run side
  by side, one per server slot; that and the vision part fill the 24 GB card.
- `finetune/session_sheet.py` lays the final pictures of the two models side by side, puts each model's first working
  run beside its last, and makes, per scene, a strip of the picture after each run.

- Before and after use the same 4-bit GGUF in llama.cpp, the same prompt and sampling settings, and seeds 0, 1 and 2.
  The only difference is the `--lora` flag.
- LoRA targets are the attention and MLP projections. The converter to llama.cpp's adapter format cannot handle this
  architecture's linear-attention projections, and leaving them out also keeps the peak under the card's limit
  (21.5 GiB in run 3).
- Every model-written script runs in the same sandbox as the scene files. Each picture shows three views: the script's
  own camera and lights, then two fixed views under the same sun.
- Training rounds the frozen model with bitsandbytes NF4; the tests run the adapter on a GGUF rounded another way
  (Q4_K). The adapter's scale is the same in both (alpha 32 at rank 16), and all 256 adapted layers are converted.
  What the different rounding costs was not measured.

The scene dataset (`synth/`) is written by agents, each given `synth/guide.md` and a folder holding a `requests.json`.
The dataset itself is not in git; it is to be published as a Hugging Face dataset. The scripts here expect it at these
paths: the scenes in `results/synth_v1/`, the pilot and style rounds in `results/synth_pilot/` and `results/synth_style/`,
the request lists in `synth/requests/*.jsonl`, and the 100 test requests in `blender_task/prompts_scenes100.json`.
What is run by hand around them:

```bash
uv run python synth/requests/assemble.py                   # overlap checks; writes train, test and spare request lists
uv run python synth/check.py results/synth_v1/train_b01    # PASS or FAIL per script, with the reason
uv run python synth/tighten_camera.py plan <backup dir>    # one-off, wave 1: see the file's header
uv run python synth/build_train.py                          # the trainer's files from the scenes: results/finetune_v3/train.jsonl, val.jsonl
# cleaner pictures for a person to review: a copy of the scripts, own view only, then one sheet
uv run python blender_task/run_sandboxed.py results/synth_v1/show/train_b01 --own-view --only-own-view --size 640 --samples 128 --denoise --workers 4
uv run python synth/sheet.py results/synth_v1/show/train_b01 results/synth_v1/sheets/train_b01.png --cols 5 --all-views
```
- `finetune/checks.py` holds the checks shared by the dataset checker and the reports: did it run, did it build anything,
  does its own camera show the scene. `results/finetune_v3/eval50/before/bare_geometry/` are the untuned model's scripts
  for the 50 everyday requests run again without rendering, to record where their cameras and lights point (they were
  written before the harness recorded that).
- Adapters (`*.safetensors`, `*.gguf`) and the per-script renders are not in git; the sheets and reports are.

## Method notes

- One probe is one process: it loads a model, sets up one technique, runs three steps at a fixed
  batch x sequence shape, and records weights, gradients, optimizer state, and the peak in each phase.
  It writes its record even when it runs out of memory.
- Memory does not depend on weight values, so most probes use random weights built from the real
  config. This was checked against the real Qwen3.5-0.8B-Base checkpoint: identical in every field.
- Only one probe runs at a time, and each record stores how much GPU memory the desktop was using. That
  share moved between campaigns (1.4 to 1.9 GiB for the fallback runs, 0.9 to 1.1 GiB for the fast-kernel
  runs), so a result within about 1 GiB of the limit can go either way. One did: Qwen3.8-27B under QLoRA
  with the stock loss at 1,024 tokens peaked at 22.6 GiB, completing in one set and failing in another.
