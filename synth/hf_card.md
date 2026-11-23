---
license: other
license_name: anthropic-usage-policy
license_link: https://www.anthropic.com/legal/aup
pretty_name: Blender Low-Poly Diorama Scenes
language:
- en
task_categories:
- text-generation
tags:
- blender
- bpy
- 3d
- code
- synthetic
size_categories:
- 1K<n<10K
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-*.parquet
  - split: test
    path: data/test-*.parquet
---

# Blender Low-Poly Diorama Scenes

{n_all} requests for a 3D scene, each paired with a Blender Python (`bpy`) script that builds the whole scene, and a
render of it. Every scene is in one look: a low-poly diorama on a floating base, with dramatic lighting and glowing
lights. Every script runs without error in Blender 5.2.3 and passes the checks listed below.

The scripts were written by Claude Sonnet 5.5 (Anthropic), running as agents in Claude Code: each agent wrote a script,
ran it in a sandboxed Blender, looked at the render, and fixed what it saw. (It was first used for a fine-tuning
experiment, in [Local-FineTune-Memory](https://github.com/Shimin-Zhang/Local-FineTune-Memory).)

```python
from datasets import load_dataset
train = load_dataset("{repo_id}", split="train")
```

## Splits

| Split | Scenes | Notes |
|---|---|---|
| train | {n_train} | |
| test | {n_test} | The main subject of each test request appears in no training request. |

## Columns

| Column | What it is |
|---|---|
| `id` | `train_0000` ... / `test_0000` ... |
| `category`, `subject`, `setting` | The kind of place ({n_categories} categories), the main subject, and the setting the request was written around |
| `instruction` | The request, e.g. "Model a drained aquarium with green-stained tanks, cracked glass, scattered tools, a fish-shaped sign and a thin beam of light." |
| `script` | The final `bpy` script. It clears the scene, builds everything, and sets its own camera, lights, world and render settings |
| `messages` | System prompt, request, and the script in a Python code block, ready for chat-format fine-tuning |
| `image` | The render through the script's own camera (Cycles, 640 x 640, 128 samples, denoised; JPEG) |
| `script_tokens`, `script_lines` | Length of the script (tokens counted with the Qwen3.8 tokenizer, for the script in its code block) |
| `n_objects`, `n_materials`, `n_lights` | What the script built, read from Blender after it ran |
| `render_engine`, `blender_version` | As reported by Blender after the run |
| `writer_rating`, `writer_note` | The writing agent's own rating of its picture (1 to 5) and its note |
| `first_run` | `ok`, or the error the first version of the script raised |
| `revisions` | How many times the agent changed the script after its first run |
| `fixes` | The agent's note for each revision |
| `framing_repair` | Set for the scenes whose camera was later moved back because the scene was cut off by the frame |
| `first_script` | The version of the script that was first run |

## How it was made

1. **Requests.** Written by Claude agents across {n_categories} categories of place, then filtered: a main subject at
   most twice in the set, and no two requests sharing nearly half of their content words.
2. **Scripts.** Each agent got a written guide (the look, rules for Blender 5.2, the checks) and 20 requests. For each
   request it wrote a script, ran it in a headless Blender 5.2.3 with a read-only filesystem and no network, looked at
   the render, and revised.
3. **Checks** that every scene passes: the script runs without error; the starting cube is removed; every object has a
   material; colours are set on shader nodes (a colour set only on `material.diffuse_color` does not reach a render
   in Blender 5.2); the script's own camera shows the scene and the scene is not cut off by the frame; no outside files
   (no image textures, nothing downloaded); at most 3,300 tokens.
4. **Framing repair.** {framing_repaired} scenes of the first wave were cut off by their own frame; their camera was
   moved back along its line of sight, and all of them were checked again.

## Numbers

- Scripts: median {med_tokens} tokens ({min_tokens} to {max_tokens}), median {med_lines} lines; {sum_tokens} tokens in all.
- Scenes: median {med_objects} objects ({min_objects} to {max_objects}), {med_materials} materials and {med_lights} lights.
- The first version ran without error for {first_ok} of {n_all} scenes; {revised_0} scripts were kept as first written.

Each writing agent also rated its own final picture (the view through the script's camera) against the request, from
1 to 5. These are the model's ratings of its own work, not human scores. Scenes rated 2 pass every check and are kept;
filter on `writer_rating` to drop them.

| Writer's rating (1 to 5) | Number of scenes |
|---|---|
| 1 | {rating_1} |
| 2 | {rating_2} |
| 3 | {rating_3} |
| 4 | {rating_4} |
| 5 | {rating_5} |

## Limitations

- One look, flat colours: no script uses an image texture or a procedural texture node. A model fine-tuned on this set
  alone tends to give every request that look, plain objects included; mix in other data if they should stay plain.
- Shapes are assembled from primitives and simple meshes; nothing is sculpted.
- The scripts target Blender 5.2. Older versions differ in places (render engine names, shader inputs).
- The writer fields (`first_run`, `revisions`, `fixes`, `writer_rating`) are the agents' own records and approximate:
  in some batches the copy kept as `first_script` was tidied before it was first run, and one agent filled in
  `first_run` from its final run. {no_first} scene has no saved first version.

## Origin and terms

The requests and scripts were generated with Claude (Anthropic). Their use is subject to Anthropic's Usage Policy:
https://www.anthropic.com/legal/aup. No separate license is claimed over them.
