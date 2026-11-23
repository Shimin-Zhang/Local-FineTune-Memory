# Writing dataset scripts for Blender

You are writing training examples: a plain request, and the Blender Python script that fulfils it. A smaller model
will learn from these scripts to write one, in a single reply, with no chance to run it. So each script must work
the first time on its own, and must be the script you would want copied.

## What one example is

- `<id>.py`: one self-contained script for one request on your list. It will be run in
  Blender 5.2.3, headless, from a new file, and nothing else is run before or after it.
- Every request is a full scene: a place with a main subject (often a building or a structure) and the things
  around it. Aim for the detail of a spiral staircase with every step, post and rail modelled: some dozens of parts,
  each one deliberate.
- The picture made from it must show what the request asked for, well lit and well framed, through the script's
  own camera.

## Rules for every script

1. **Empty the scene first.** A new file holds a cube, a light and a camera. Start with
   `for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)`.
2. **Blender 5.2.3 only.** Names changed several times in Blender 4 and 5 (shader inputs, node types, render
   engine names, mesh smoothing). Your memory of `bpy` may be older than this version. The run decides, not memory.
3. **Colour goes on shader nodes.** Set colours on the inputs of nodes in the material's node tree, with four
   values (red, green, blue, alpha). `material.diffuse_color` alone does not reach a render. Find a node by its
   type, not by its display name.
4. **No outside files.** No image files, no asset libraries, no add-ons.
5. **Every object gets a material.**
6. **Deliberate shape.** Build each thing so its outline reads at a glance, in the look described below: tapered
   and extruded forms, profiles spun with few steps, `bmesh`, booleans. A pile of untouched cubes is the thing to
   avoid. Sizes in metres, sensible proportions, things resting on what is under them, no parts floating or
   cutting through each other by accident.
7. **Light it and frame it,** in the look described below. Aim the camera, and any spot or area light, at a point
   instead of typing angles: `obj.rotation_euler = (target - obj.location).to_track_quat('-Z', 'Y').to_euler()`
   with `target` a `mathutils.Vector`. Set `scene.camera`.
8. **Nothing outside the scene.** No file reading or writing, no rendering or saving, no render settings (engine,
   resolution, samples, output path), no `print`, no `os`, `sys` or network. Use a fixed `random.seed` if you use
   random numbers.
9. **Detailed, within a limit.** Aim for 2,500 to 3,300 tokens as counted by `synth/check.py`; 3,300 is the limit.
   Spend the room on more parts and more varied forms (steps, columns, arches, roofs, windows, railings, rocks,
   plants, props that say what the place is), not on repetition or commentary. Build repeated parts with loops.
10. **Written for this scene.** No block of helper code carried from one script to the next. Define a helper only
    where it shortens this script, keep it to a few lines, and name things for this scene. The ground, the light
    and the camera are written out for this place each time, because choosing them is part of what is being taught.

## The look: a low-poly diorama with dramatic light and glow

Every picture in this dataset shares one look, so that a model trained on it is recognisable at a glance. Whatever
the request, the result is a small low-poly diorama floating in the dark, lit like a stage, with something glowing.

- **Low-poly.** Faceted, flat-shaded forms: no smooth shading, no subdivision, no bevels. Few sides (cylinders and
  cones with 5 to 10, icospheres with 1 or 2 subdivisions). Chunky, slightly exaggerated proportions. Make natural
  things irregular (rocks, foliage, ground: move their vertices a little with seeded random numbers; vary sizes and
  turns), and keep made things crisp.
- **Diorama.** The scene stands on a base that floats in darkness: a low-poly slab of ground sized to the scene,
  with a tapered, rough underside, in a ground that suits the place (grass, sand, rock, snow, planks, metal deck).
  Shape the top of the base where the place calls for it (a hill, steps, a pond, a path). Everything stays inside
  the base's outline, so make the base a little larger than the scene. No floor beyond it, no walls around it, no backdrop. An interior is shown as a cutaway: its
  floor is the base and at most two walls stand, so the camera sees in.
- **Flat colour.** Each material is one colour with a rough finish; no texture nodes. A pattern (stripes, tiles,
  speckles, planks) is built from pieces or faces in different colours. Keep to a small palette, 4 to 7 colours
  that sit well together, plus the glow.
- **Glow.** Something in every scene gives off light: a window, lantern, crystal, screen, fire, molten metal,
  sign, magic. Give it an emission colour strong enough to read as a light source, and put a point light of the
  same colour at the same place so the glow spills onto what is around it. If nothing in the request would glow,
  set a thin glowing line into the rim of the base in an accent colour.
- **Dramatic light, chosen for the place.** A near-black background with a hint of colour. One strong key light,
  low and from one side, throwing long shadows, and one dimmer rim light from behind on the other side to pick out
  the outline. No flat fill: let the shadows go dark, but keep the subject readable. Choose the colours and
  directions for the mood of this place and of the request (a moonlit ruin, a forge at night, a foggy swamp, a
  harbour at dawn should not be lit alike). As a starting point that reads well: a key sun of strength about 5 some
  20 degrees above the horizon, a rim sun of about 2, a background near (0.01, 0.01, 0.03), and glow lights of 150
  to 2,500 W, more for tall scenes.
- **Camera.** A three-quarter view from above, 25 to 35 degrees up, through a long lens (70 to 90 mm), far enough
  back that the whole scene fits with a small margin: about 2.5 to 3 times the scene's width away, and more for a
  tall scene, because the picture is square. The whole base, and everything on or above it (light shafts, rain,
  smoke, sky), must sit inside the picture with dark background all round it: the checker fails a scene that is cut
  off by the picture's edge. Do not overshoot either: the scene should span most of the picture (85 to 90% of its
  width or height), and the checker warns when it is small.
- **Readable at a glance.** Make small things that matter (hands of a clock, coins, tools, signs) larger than life,
  and keep large surfaces mid to dark in colour so they do not burn out under the key light.

If the request describes its own lighting or colours, follow it inside this look: the forms stay low-poly, the base
still floats in the dark, and something still glows.

## How to work

All commands run from `/home/shimin/agents/scrap/local-finetune-memory`. `<dir>` is your own folder.

1. Write a script for each of your requests into `<dir>/<id>.py`. Copy each first version, before any fix, to
   `<dir>/first/<id>.py` and never edit that copy.
2. Run them: `uv run python blender_task/run_sandboxed.py <dir> --own-view --workers 6`
   It runs every script in `<dir>` that has no report yet, and writes next to each one:
   - `<id>.report.json`: `error` and `error_line` if it failed, objects, materials with their node types, lights,
     camera.
   - `<id>.png`: three views side by side. Left: through the script's own camera with its own lights. Middle and
     right: two fixed views from opposite sides under a plain sun, to judge the shape.
3. Check the rules: `uv run python synth/check.py <dir>` prints PASS or FAIL with the reason for each script.
   Do this on your first two or three scripts before writing the rest: most first versions come out too long, and
   it is cheaper to learn your length early than to trim twenty scripts afterwards.
4. Look at every picture (read the `.png`). Ask: would a person who typed the request be pleased with the left
   view? Common faults: the subject is tiny or cut off, too dark or burnt out, parts float or intersect, the
   shape reads as blocks, or the picture does not have the look described above.
5. Fix what is wrong. To run one script again, delete its `.report.json` and repeat step 2. Go round at most
   three times per script; if it still fails, keep your best version and say so in the manifest.
6. To find out a name in this Blender (an input of a node, a property, an enum value), write a small script in
   `<dir>/probe/` that writes what it finds to a text file beside it, and run it the same way:
   `uv run python blender_task/run_sandboxed.py <dir>/probe --no-render`.

## Hard limits

- Blender is run only through `blender_task/run_sandboxed.py`. Do not start Blender any other way, and do not use
  any Blender MCP tool: that one drives a person's open Blender session.
- Write only inside your own folder. Do not edit other files, do not commit, do not download anything.

## What to hand back

`<dir>/manifest.jsonl`, one line per request:
`{"id", "status": "accepted" | "failed", "rounds": how many times you changed the script after the first run,
"first_run": "ok" or the error message, "fixes": [short notes, one per round], "picture": 1-5 (your honest rating
of the left view against the request), "note": anything a reviewer should know}`.

Then a report of under 400 words: how many passed first time, which errors came up and what the right names turned
out to be in 5.2.3, what kinds of request were hardest, where the rules in this guide were unclear or got in the
way, and your frank view of how good the pictures are.
