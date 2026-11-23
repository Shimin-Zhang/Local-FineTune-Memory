"""Check the writers' scene requests for overlap, and split them into a training list and a held-out test list.

Usage: python synth/requests/assemble.py [--test 100] [--train 2000] [--seed 20261112]
Reads synth/requests/part_*.jsonl ({"category", "head", "setting", "request"} per line) and categories.json. Writes
train.jsonl, test.jsonl, spare.jsonl and overlap_report.json next to them.

What counts as overlap, and what is done about it:
  - a request whose main subject (head) is on the held-back list, or that names how the scene will look: dropped;
  - the same head more than twice in the whole set: the third and later ones are dropped;
  - two requests whose wording shares nearly half of its content words: the later one is dropped;
  - a request that mentions a subject of the 50 everyday test requests (blender_task/prompts_eval50.json), even in passing: dropped;
  - a test request's head may not be the head of any training request, nor appear in the text of one. Test heads
    are drawn from heads used once, a few from every category, and any training request that mentions one is
    moved to the spare list.
"""
import argparse, collections, glob, json, os, random, re

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--test", type=int, default=100); ap.add_argument("--train", type=int, default=2000); ap.add_argument("--seed", type=int, default=20261112)
a = ap.parse_args()
HELD_BACK = ["lighthouse", "castle", "farm", "farmyard", "barn", "harbour", "harbor", "park", "playground", "kitchen", "bedroom", "living room",
             "campsite", "street corner", "desk", "office", "solar system", "house", "snowman", "rocket", "car", "traffic light", "chess",
             "campfire", "wizard tower", "wizard's tower", "clock tower", "step pyramid", "desert island", "corridor"]
# subjects of the first test set (blender_task/prompts_eval50.json): not even as a side element of a training scene
FIRST_TEST = r"\b(lighthouses?|castles?|barns?|harbou?rs?|playgrounds?|kitchens?|bedrooms?|living rooms?|campsites?|street corners?|solar system|snowm[ae]n|rockets?|traffic lights?|chess|campfires?)\b"
LOOK_WORDS = r"\b(low[- ]?poly|diorama|styli[sz]ed|3d|render(ed|ing)?|blender|camera|lighting set-?up|polygon|voxel)\b"
MOOD = r"\b(dusk|dawn|night|midnight|twilight|sunrise|sunset|sundown|moon(lit|light)?|fog(gy)?|mist(y)?|storm(y)?|rain(y|ing)?|snow(ing|fall|storm)?|blizzard|noon|midday|first light|golden hour|evening|morning|festival|abandoned|overcast|thunder|starlit|stars|candle-?lit|lantern-?lit|winter|autumn|spring|summer|heat|frost(y)?|aurora)\b"
STOP = set("""a an the and or of in on at by to with for from into onto over under beside near next behind above below around between through its it is are be as
that this these those there their one two three four five six seven eight nine ten some few several small little tiny large big old new me my i id like
would could can you please make build create model show give want need design set put add let us have has scene place where which whose while each
every also just very up out off down along across inside outside front back side top""".split())


def stem(w):
    for suf in ("ies", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[:-len(suf)] + ("y" if suf == "ies" else "")
    return w


def words(text):
    return [stem(w) for w in re.findall(r"[a-z]+", text.lower().replace("'s", "")) if w not in STOP]


def norm_head(h):
    return " ".join(stem(w) for w in re.findall(r"[a-z]+", h.lower()) if w not in ("a", "an", "the"))


cats = {c["id"]: c for c in json.load(open(os.path.join(HERE, "categories.json")))}
rows, bad_lines = [], 0
for f in sorted(glob.glob(os.path.join(HERE, "part_*.jsonl"))):
    for i, line in enumerate(open(f)):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
            assert r["category"] in cats and all(isinstance(r[k], str) and r[k].strip() for k in ("head", "setting", "request"))
        except Exception:
            bad_lines += 1
            continue
        r.update(writer=os.path.basename(f)[5:-6], key=norm_head(r["head"]), content=frozenset(words(r["request"])))
        rows.append(r)

dropped, kept, head_count = collections.Counter(), [], collections.Counter()
held = {norm_head(h) for h in HELD_BACK}
near = []
by_word = collections.defaultdict(list)                    # content word -> indexes of kept rows, to find near-duplicates quickly
for r in rows:
    n = len(r["request"].split())
    why = ("main subject is held back" if r["key"] in held else "names the look or how it is made" if re.search(LOOK_WORDS, r["request"].lower())
           else "mentions a subject of the first test set" if re.search(FIRST_TEST, r["request"].lower())
           else "request shorter than 6 or longer than 40 words" if not 6 <= n <= 40 else "head used more than twice" if head_count[r["key"]] >= 2 else None)
    if not why:
        seen = collections.Counter(j for w in r["content"] for j in by_word[w])
        for j, shared in seen.most_common(5):
            other = kept[j]
            score = shared / len(r["content"] | other["content"])
            if score >= 0.45 or (other["key"] == r["key"] and score >= 0.4):
                why = "wording nearly the same as another request"
                near.append({"dropped": r["request"], "kept": other["request"], "shared": round(score, 2)})
                break
    if why:
        dropped[why] += 1
        continue
    head_count[r["key"]] += 1
    for w in r["content"]:
        by_word[w].append(len(kept))
    kept.append(r)

# the closest pairs that were kept, for a person to look over
close = []
for i, r in enumerate(kept):
    seen = collections.Counter(j for w in r["content"] for j in by_word[w] if j < i)
    for j, shared in seen.most_common(2):
        score = shared / len(r["content"] | kept[j]["content"])
        if score >= 0.45:
            close.append((round(score, 2), r["request"], kept[j]["request"]))
close.sort(reverse=True)

# even out the form of the requests: the writers leaned on bare descriptions ("A mill beside ..."), so some of those
# are turned into a command or a wish by putting a few words in front. The scene asked for does not change.
rng = random.Random(a.seed)
def form(text):
    t = text.split()[0].lower().strip(",.")
    return ("bare" if t in ("a", "an", "the", "two", "three", "four", "five", "six") else
            "wish" if t in ("i'd", "i", "could", "can", "would", "please", "may", "i'm") else "command")
COMMANDS = ["Build", "Create", "Make", "Model", "Put together", "Construct"]
WISHES = [("I'd like", "."), ("I want", "."), ("Could you make", "?"), ("Can you build", "?"), ("Please make", ".")]
target = {"command": 0.45, "wish": 0.22}                   # the rest stay bare
counts = collections.Counter(form(r["request"]) for r in kept)
bare = [r for r in kept if form(r["request"]) == "bare" and r["request"].split()[0] in ("A", "An", "The")]
rng.shuffle(bare)
changed = collections.Counter()
for r in bare:
    want = next((k for k in ("command", "wish") if counts[k] < target[k] * len(kept)), None)
    if not want:
        break
    body = r["request"][0].lower() + r["request"][1:]
    one_sentence = body.rstrip().endswith(".") and body.count(". ") == 0
    if want == "wish" and one_sentence:
        lead, end = rng.choice(WISHES)
        r["request"] = f"{lead} {body.rstrip()[:-1]}{end}"
    else:
        want = "command"
        r["request"] = f"{rng.choice(COMMANDS)} {body}"
    counts[want] += 1; counts["bare"] -= 1; changed[want] += 1

# test: heads used once, a few from each category, and absent from every other request
text = [" " + " ".join(stem(w) for w in re.findall(r"[a-z]+", r["request"].lower() + " " + r["setting"].lower())) + " " for r in kept]
def clean(i):
    r = kept[i]
    return head_count[r["key"]] == 1 and not any(f" {r['key']} " in t for j, t in enumerate(text) if j != i)
pool = collections.defaultdict(list)
for i, r in enumerate(kept):
    pool[r["category"]].append(i)
for v in pool.values():
    rng.shuffle(v)
order, test = sorted(pool), []
while len(test) < a.test and any(pool.values()):           # round robin over categories
    for c in order:
        while pool[c]:
            i = pool[c].pop()
            if clean(i):
                test.append(i)
                break
        if len(test) >= a.test:
            break
test_set, test_keys = set(test), {kept[i]["key"] for i in test}
mentions = {i for i, t in enumerate(text) if i not in test_set and any(f" {k} " in t for k in test_keys)}
train_idx = [i for i in range(len(kept)) if i not in test_set and i not in mentions]
# keep the training list even across categories; the rest is spare
per = collections.defaultdict(list)
for i in train_idx:
    per[kept[i]["category"]].append(i)
for v in per.values():
    rng.shuffle(v)
train = []
while len(train) < a.train and any(per.values()):
    for c in sorted(per):
        if per[c] and len(train) < a.train:
            train.append(per[c].pop())
spare = sorted(set(train_idx) - set(train)) + sorted(mentions)


def write(name, idx):
    out = sorted(idx, key=lambda i: (kept[i]["category"], kept[i]["key"]))
    with open(os.path.join(HERE, name), "w") as f:
        for n, i in enumerate(out):
            r = kept[i]
            f.write(json.dumps({"id": f"{name.split('.')[0]}_{n:04d}", "category": r["category"], "head": r["head"], "setting": r["setting"],
                                "request": r["request"]}, ensure_ascii=False) + "\n")


write("train.jsonl", train); write("test.jsonl", test); write("spare.jsonl", spare)
mood = lambda idx: sum(bool(re.search(MOOD, kept[i]["request"].lower())) for i in idx)
first = lambda idx: collections.Counter(kept[i]["request"].split()[0].lower().strip(",.") for i in idx).most_common(8)
report = {"written": len(rows), "lines that did not parse": bad_lines, "kept": len(kept), "dropped": dict(dropped),
          "distinct heads kept": len(head_count), "heads used twice": sum(v == 2 for v in head_count.values()),
          "train": len(train), "test": len(test), "spare": len(spare), "moved to spare because they mention a test head": len(mentions),
          "train per category (min, max)": [min(collections.Counter(kept[i]["category"] for i in train).values()), max(collections.Counter(kept[i]["category"] for i in train).values())],
          "test per category (min, max)": [min(collections.Counter(kept[i]["category"] for i in test).values()), max(collections.Counter(kept[i]["category"] for i in test).values())],
          "requests with a mood or time": {"train": mood(train), "test": mood(test)},
          "bare descriptions turned into": dict(changed), "forms": dict(collections.Counter(form(kept[i]["request"]) for i in train)),
          "median words per request": sorted(len(kept[i]["request"].split()) for i in train)[len(train) // 2] if train else None,
          "commonest first words in train": first(train),
          "near-duplicates dropped (sample)": near[:15], "closest pairs kept": [{"shared": s, "a": x, "b": y} for s, x, y in close[:25]]}
json.dump(report, open(os.path.join(HERE, "overlap_report.json"), "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in report.items() if k not in ("near-duplicates dropped (sample)", "closest pairs kept")}, indent=1))
