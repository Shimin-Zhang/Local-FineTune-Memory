#!/usr/bin/env python3
"""Measure GPU memory of llama.cpp (b10443) 4-bit inference on an RTX 4090.

Usage: python3 measure/llamacpp_inference.py [--only main|search|mmproj|repeat|all]
Runs ONE llama-server at a time on port 8099, with --parallel 1, -ngl all, --fit off
(so the requested context is never silently shrunk and a failure is a real failure),
-lv 4 (so llama.cpp prints its memory lines). Writes results/inference_llamacpp.json
(records are merged by run tag, so partial re-runs are fine) and results/logs/*.log.
Only kills the server PID it started itself.
"""
import argparse, json, os, re, signal, subprocess, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
LOGS = os.path.join(RES, "logs")
OUT = os.path.join(RES, "inference_llamacpp.json")
BIN = "/home/shimin/ai/llama.cpp/build/bin/llama-server"
PORT = 8099
M = "/home/shimin/ai/models"
MODELS = {
    "qwen3.8-27b": f"{M}/qwen3.8-27b/Qwen3.8-27B-UD-Q4_K_XL.gguf",
    "qwen3.6-35b-a3b": f"{M}/qwen3.6-35b-a3b/Qwen3.6-35B-A3B-UD-Q4_K_M.gguf",
    "gemma-4-26b-a4b": f"{M}/gemma-4-26b-a4b/gemma-4-26B-A4B-it-qat-UD-Q4_K_XL.gguf",
}
PRIMARY = "qwen3.8-27b"
MMPROJ = f"{M}/qwen3.8-27b/mmproj-F16.gguf"


def gpu_used():
    o = subprocess.check_output(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"], text=True)
    return int(o.strip().splitlines()[0])


def proc_mem(pid):
    o = subprocess.check_output(["nvidia-smi", "--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"], text=True)
    for line in o.strip().splitlines():
        p, m = [x.strip() for x in line.split(",")]
        if int(p) == pid:
            return int(m)
    return None


def http(path, data=None, timeout=600):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}",
                                 data=None if data is None else json.dumps(data).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def make_prompt(target=2000):
    base = ("The quick brown fox jumps over the lazy dog while the committee reviews quarterly "
            "figures for the northern region. ")
    n = 1
    while True:
        text = base * n + "\nSummarize the passage above in one sentence."
        t = len(http("/tokenize", {"content": text})["tokens"])
        if t >= target or n > 400:
            return text, t
        n = max(n + 1, int(n * target / max(t, 1)))


def parse_log(path):
    lines = [l.rstrip("\n") for l in open(path, errors="replace")]
    keep, d = [], dict(model=0.0, cpu_model=0.0, kv=0.0, other=0.0, compute=[], layers=None, total=None, ctx=None, slot_ctx=None, kv_seen=False, other_seen=False, model_seen=False)
    pats = re.compile(r"buffer size|offloaded \d+/\d+|offloading|llama_context: n_ctx|n_ctx_seq|new slot|llama_kv_cache: size|llama_memory_recurrent: size|memory breakdown|common_memory_breakdown|CUDA0 \(|Host \(|clip_model_loader.*(size|offload)|mtmd|failed to|out of memory|cudaMalloc|error", re.I)
    for l in lines:
        if "unused tensor" in l:
            continue
        if not pats.search(l):
            continue
        keep.append(l)
        mib = re.search(r"=\s*([\d.]+)\s*MiB", l)
        if "model buffer size" in l and mib:
            if "CUDA0" in l:
                d["model"] += float(mib.group(1)); d["model_seen"] = True
            else:
                d["cpu_model"] += float(mib.group(1))
        elif "KV buffer size" in l and "CUDA0" in l and mib:
            d["kv"] += float(mib.group(1)); d["kv_seen"] = True
        elif re.search(r"(RS|state) buffer size", l) and "CUDA0" in l and mib:
            d["other"] += float(mib.group(1)); d["other_seen"] = True
        elif "CUDA0 compute buffer size" in l and "sched_reserve" in l and mib:
            d["compute"].append(float(mib.group(1)))
        m = re.search(r"offloaded (\d+)/(\d+) layers", l)
        if m:
            d["layers"], d["total"] = int(m.group(1)), int(m.group(2))
        m = re.search(r"llama_context: n_ctx\s+= (\d+)", l)
        if m: d["ctx"] = int(m.group(1))
        m = re.search(r"new slot, n_ctx = (\d+)", l)
        if m: d["slot_ctx"] = int(m.group(1))
    return keep, d


def wait_idle(base0, limit=180):
    t0 = time.time(); last = None
    while time.time() - t0 < limit:
        u = gpu_used()
        if u <= base0 + 100 and last is not None and abs(u - last) <= 30:
            return u, True
        last = u; time.sleep(3)
    return gpu_used(), False


def run_one(model, ctx, base0, mmproj=False, tag=None):
    path = MODELS[model]
    suffix = f"{ctx}" + ("_mmproj" if mmproj else "") + (f"_{tag}" if tag else "")
    log = os.path.join(LOGS, f"llamacpp_{model}_{suffix}.log")
    cmd = [BIN, "-m", path, "-c", str(ctx), "--parallel", "1", "-ngl", "all", "--fit", "off", "-lv", "4",
           "--host", "127.0.0.1", "--port", str(PORT)]
    if mmproj:
        cmd += ["--mmproj", MMPROJ]
    rec = dict(model_file=path, file_bytes=os.path.getsize(path), ctx_requested=ctx, ctx_used=None, with_mmproj=mmproj,
               status=None, gpu_baseline_mib=gpu_used(), gpu_used_after_load_mib=None, process_mib_after_load=None,
               gpu_used_after_request_mib=None, process_mib_after_request=None, log_model_buffer_mib=None,
               log_kv_buffer_mib=None, log_other_state_mib=None, log_compute_buffer_mib=None, layers_offloaded=None,
               layers_total=None, raw_log_lines=[], command=" ".join(cmd), notes=[], run_tag=suffix, log_file=log,
               log_cpu_model_buffer_mib=None, prompt_tokens=None, generated_tokens=None)
    print(f"== {suffix} {model} baseline={rec['gpu_baseline_mib']}", flush=True)
    with open(log, "w") as lf:
        p = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT, start_new_session=True)
    pid = p.pid
    try:
        t0 = time.time(); ready = False
        while time.time() - t0 < 300:
            if p.poll() is not None:
                break
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health", timeout=3) as r:
                    if r.status == 200:
                        ready = True; break
            except Exception:
                pass
            time.sleep(2)
        rec["load_seconds"] = round(time.time() - t0, 1)
        if not ready:
            rec["status"] = "failed"
            rc = p.poll()
            rec["notes"].append(f"server not ready; exit code {rc}" if rc is not None else "timeout 300s waiting for /health")
        else:
            time.sleep(2)
            rec["status"] = "ok"
            rec["gpu_used_after_load_mib"] = gpu_used()
            rec["process_mib_after_load"] = proc_mem(pid)
            try:
                text, nt = make_prompt()
                r = http("/completion", {"prompt": text, "n_predict": 64, "temperature": 0, "cache_prompt": False})
                rec["prompt_tokens"] = r.get("tokens_evaluated"); rec["generated_tokens"] = r.get("tokens_predicted")
            except Exception as e:
                rec["notes"].append(f"request failed: {e!r}")
            time.sleep(2)
            rec["gpu_used_after_request_mib"] = gpu_used()
            rec["process_mib_after_request"] = proc_mem(pid)
    finally:
        try:
            os.killpg(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            p.wait(timeout=60)
        except subprocess.TimeoutExpired:
            os.killpg(pid, signal.SIGKILL); p.wait()
    keep, d = parse_log(log)
    rec["raw_log_lines"] = keep if len(keep) < 80 else keep[:80]
    rec["ctx_used"] = d["ctx"]
    if d["slot_ctx"] and d["slot_ctx"] != d["ctx"]:
        rec["notes"].append(f"slot n_ctx={d['slot_ctx']} differs from llama_context n_ctx={d['ctx']}")
    if d["model_seen"]: rec["log_model_buffer_mib"] = round(d["model"], 2)
    if d["cpu_model"]: rec["log_cpu_model_buffer_mib"] = round(d["cpu_model"], 2)
    if d["kv_seen"]: rec["log_kv_buffer_mib"] = round(d["kv"], 2)
    if d["other_seen"]: rec["log_other_state_mib"] = round(d["other"], 2)
    if d["compute"]:
        rec["log_compute_buffer_mib"] = max(d["compute"])
        if len(d["compute"]) > 1: rec["notes"].append(f"multiple CUDA0 compute lines {d['compute']}; max recorded")
    rec["layers_offloaded"], rec["layers_total"] = d["layers"], d["total"]
    if rec["status"] == "ok":
        if d["layers"] is None or d["layers"] != d["total"]:
            rec["notes"].append("WARNING: not all layers offloaded to GPU (or not printed)")
        if rec["log_cpu_model_buffer_mib"]:
            rec["notes"].append(f"{rec['log_cpu_model_buffer_mib']} MiB of weights are in a CPU_Mapped buffer (not on GPU) even though all layers offloaded")
    else:
        bad = [l for l in open(log, errors="replace") if re.search(r"out of memory|failed|error|cudaMalloc", l, re.I) and "unused tensor" not in l]
        rec["notes"].append("failure log lines: " + " | ".join(l.strip()[:300] for l in bad[-6:]))
    end, ok = wait_idle(base0)
    rec["gpu_after_cleanup_mib"] = end
    if not ok: rec["notes"].append(f"GPU did not return within 100 MiB of start baseline {base0} (now {end})")
    print(f"   {rec['status']} proc={rec['process_mib_after_load']} cleanup={end}", flush=True)
    return rec


def load():
    return json.load(open(OUT)) if os.path.exists(OUT) else []


def save(recs):
    json.dump(recs, open(OUT, "w"), indent=1)


def add(recs, r):
    recs[:] = [x for x in recs if x["run_tag"] != r["run_tag"] or x["model_file"] != r["model_file"]] + [r]
    save(recs)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--only", default="all"); a = ap.parse_args()
    os.makedirs(LOGS, exist_ok=True)
    if subprocess.run(["curl", "-sf", f"http://127.0.0.1:{PORT}/health"], capture_output=True).returncode == 0:
        sys.exit("something already listens on 8099; refusing")
    recs = load(); base0 = gpu_used()
    print("start baseline", base0)
    if a.only in ("all", "main"):
        for c in (4096, 8192, 32768, 65536, 131072):
            add(recs, run_one(PRIMARY, c, base0))
        for m in ("qwen3.6-35b-a3b", "gemma-4-26b-a4b"):
            for c in (8192, 32768):
                add(recs, run_one(m, c, base0))
    if a.only in ("all", "search"):
        ok = max(r["ctx_requested"] for r in recs if r["model_file"] == MODELS[PRIMARY] and r["status"] == "ok" and not r["with_mmproj"] and not r.get("run_tag", "").endswith("_rep2"))
        fail = min([r["ctx_requested"] for r in recs if r["model_file"] == MODELS[PRIMARY] and r["status"] == "failed" and not r["with_mmproj"] and r["ctx_requested"] > ok] or [None])
        if fail:
            lo, hi = ok, fail  # lo loads, hi fails; step 8192
            while hi - lo > 8192:
                mid = (lo + hi) // 2 // 8192 * 8192
                if mid <= lo: break
                r = run_one(PRIMARY, mid, base0); add(recs, r)
                if r["status"] == "ok": lo = mid
                else: hi = mid
            print("largest ok:", lo, "smallest fail:", hi)
    if a.only in ("all", "mmproj"):
        add(recs, run_one(PRIMARY, 8192, base0, mmproj=True))
    if a.only in ("all", "repeat"):
        add(recs, run_one(PRIMARY, 8192, base0, tag="rep2"))
    print("final GPU used", gpu_used())


if __name__ == "__main__":
    main()
