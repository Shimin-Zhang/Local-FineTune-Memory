"""Read the tensor table of GGUF files on the Hub without downloading the weights: fetch the header with an HTTP
range request into a sparse file of the full length, then let gguf-py read it (tensor data is never touched)."""
import sys, os, re, json, urllib.request
sys.path.insert(0, "/home/shimin/ai/llama.cpp/gguf-py")
from gguf import GGUFReader
from huggingface_hub import hf_hub_url, HfApi
OUT = sys.argv[1]
REPO = "unsloth/Qwen3.8-27B-GGUF"
api = HfApi(); sizes = {s.rfilename: s.size for s in api.model_info(REPO, files_metadata=True).siblings}

def header_file(fn, nbytes):
    path = os.path.join(OUT, fn.replace("/", "__"))
    if os.path.exists(path + ".ok"): return path
    req = urllib.request.Request(hf_hub_url(REPO, fn), headers={"Range": f"bytes=0-{nbytes-1}"})
    data = urllib.request.urlopen(req, timeout=300).read()
    with open(path, "wb") as f:
        f.write(data); f.truncate(sizes[fn])          # sparse: the rest reads as zeros, nothing stored
    open(path + ".ok", "w").close(); return path

def tally(path, mtp_prefix=None):
    r = GGUFReader(path)
    nl = None; bc = None
    for f in r.fields.values():
        if f.name.endswith("nextn_predict_layers"): nl = int(f.parts[f.data[0]][0])
        if f.name.endswith(".block_count"): bc = int(f.parts[f.data[0]][0])
    if bc is not None: mtp_prefix = f"blk.{bc-1}." if nl else None   # later split files carry no model settings
    tot = {"all": [0, 0], "text": [0, 0], "token_embd": [0, 0]}; types = {}
    for t in r.tensors:
        n, b = int(t.n_elements), int(t.n_bytes)
        tot["all"][0] += n; tot["all"][1] += b
        if mtp_prefix and t.name.startswith(mtp_prefix): continue
        tot["text"][0] += n; tot["text"][1] += b
        types.setdefault(t.tensor_type.name, [0, 0]); types[t.tensor_type.name][0] += n; types[t.tensor_type.name][1] += b
        if t.name == "token_embd.weight": tot["token_embd"] = [n, b]
    return {"block_count": bc, "nextn_layers": nl, "mtp_prefix": mtp_prefix, "tensors": len(r.tensors), "totals": tot, "types": types}

spec = json.loads(sys.argv[2])
if spec == "ALL":
    spec = {}
    for fn in sorted(sizes):
        if not fn.endswith(".gguf") or fn.startswith("MTP/") or "mmproj" in fn or "imatrix" in fn: continue
        key = fn.split("/")[0] if "/" in fn else re.sub(r"^Qwen3\.8-27B-|\.gguf$", "", fn)
        spec.setdefault(key, []).append(fn)
res = {}
for name, files in spec.items():
    agg = None
    for fn in files:
        for nb in (12 << 20, 48 << 20):
            try:
                p = header_file(fn, nb); one = tally(p, agg["mtp_prefix"] if agg else None); break
            except Exception as e:
                for q in (p, p + ".ok"):
                    if os.path.exists(q): os.remove(q)
                err = e
        else:
            raise err
        if agg is None: agg = one
        else:
            for k in agg["totals"]: agg["totals"][k] = [a + b for a, b in zip(agg["totals"][k], one["totals"][k])]
            for k, v in one["types"].items():
                agg["types"].setdefault(k, [0, 0]); agg["types"][k] = [a + b for a, b in zip(agg["types"][k], v)]
            agg["tensors"] += one["tensors"]
    agg["file_bytes"] = sum(sizes[f] for f in files); agg["files"] = files
    res[name] = agg
    t = agg["totals"]["text"]
    print(f"{name:12s} file {agg['file_bytes']/2**30:6.2f} GiB | MTP in file: {bool(agg['nextn_layers'])} | text weights {t[1]/2**30:6.2f} GiB, "
          f"{t[0]/1e9:.3f}B params, {8*t[1]/t[0]:.2f} bits | token table {agg['totals']['token_embd'][1]/2**30:.2f} GiB")
json.dump(res, open(os.path.join(OUT, "tally.json"), "w"), indent=1)
