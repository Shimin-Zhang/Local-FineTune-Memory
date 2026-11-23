# Writing scene requests

You are writing the requests for a dataset of small 3D scenes. Someone else will build each scene later; you only
write what a person would type to ask for it. The whole set is 2,300 requests written by four writers, and the
point of the way the work is divided is that no two requests anywhere ask for the same thing.

## What one request is

- A full scene: one place with a main subject and the things around it. It must be buildable as a tabletop
  diorama of some dozens of parts: a building or structure with its surroundings, not a whole city, and not a
  single loose object.
- Each line of your file is one JSON object:
  `{"category": "<category id>", "head": "...", "setting": "...", "request": "..."}`
  - `head`: the main subject in one to three plain words, lower case, singular, as generic as it can be while
    still being the subject ("watermill", "rope bridge", "bell tower", "tea house").
  - `setting`: in a few words, what makes this scene this one: where, when, in what state.
  - `request`: what the person types. 8 to 35 words.

## Staying apart from each other

- You have 11 categories, 52 requests each, listed with their scope in `synth/requests/categories.json` (yours are
  the ones with your letter in `"agent"`). Read the whole list: if a subject fits another writer's category
  better, leave it to them.
- Inside your list, use a `head` once. You may use one a second time only when the two scenes would look clearly
  different (another continent, era or state), and never a third time.
- Reach for the breadth of the category: different cultures, eras, climates, sizes and purposes. If two of your
  requests could be answered by the same scene, change one.

## Never the main subject

These are held back for testing or are already made: lighthouse, castle, farm or barn, harbour, park, playground,
kitchen, bedroom, living room, campsite, street corner, desk or office, solar system, a plain house, snowman,
rocket, car, traffic light, chess pieces, a campfire on its own, wizard's tower, clock tower, step pyramid,
ruined hilltop temple, desert island with a palm, a plain science-fiction corridor.

Also: no named real buildings or brands (a kind of building is fine: "a Khmer temple", not a famous one by name),
no real people, nothing gory or cruel.

## How the requests should read

- Plain language. Never mention how it will look or be made: no "low-poly", "diorama", "stylised", "3D", "render",
  "Blender", camera or lighting set-up (saying it is night or foggy is not a lighting set-up; see Mood below).
- Vary the form across your list, roughly: four in ten a command that names two to five things to include
  ("Build a ... with a ..., a ... and ..."); two in ten a bare description ("A ... beside a ..."); two in ten a wish
  or a question ("I'd like ...", "Could you make ...?"); two in ten with something exact (a count, a colour).
  Vary the verbs and the sentence shapes; do not start every line the same way.
- Mood. In about three requests in ten, of any form, say when or in what weather or mood the place is seen: at
  dusk, under a full moon, in thick fog, on a stormy night, at first light, in the heat of noon, during a festival,
  long abandoned. Spread these widely; the builder will light each scene to match, so the more varied the better.

## What to hand back

Write `synth/requests/part_<your letter>.jsonl` with exactly 52 lines per category, in category order. Before you
finish, check your own file: every line parses, every category has 52, no `head` appears three times, and no
subject from the held-back list is a main subject. Then reply in under 150 words: the counts, and any category
where you struggled to find 52 distinct scenes.
