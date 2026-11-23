"""Ask a local GGUF model (llama.cpp server) to write a Blender script for each request.

Usage: python blender_task/generate.py <items.json> <out dir> [--conditions bare,rules] [--gguf PATH] [--lora ADAPTER.gguf]
                                       [--seeds 0,1,2] [--parallel 6] [--max-tokens 4096]
items.json is a list of {"id", "prompt"} (or a dict of such lists). For each condition (a system prompt in
system_prompts.json) it writes <out>/<condition>/<id>.py (the code block from the reply), <id>.txt (the whole reply)
and appends to generation.jsonl. With more than one seed (or --name-seeds) the files are named <id>__s<seed>. Files that exist are
skipped, so a stopped run can be started again. Starts its own server on port 8099 (never 8080), thinking off, and
stops it afterwards. --lora loads a trained adapter on top of the same model file.
"""
import argparse, json, os, re, socket, subprocess, sys, threading, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

BIN = "/home/shimin/ai/llama.cpp/build/bin/llama-server"
PORT = 8099
HERE = os.path.dirname(os.path.abspath(__file__))


def post(path, body, timeout=900):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", json.dumps(body).encode(), {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=timeout))


def code_of(text):
    m = re.findall(r"```(?:python|py)?[ \t]*\n(.*?)```", text, re.S)
    if m:
        return max(m, key=len)
    m = re.search(r"```(?:python|py)?[ \t]*\n(.*)", text, re.S)  # block never closed (ran out of tokens)
    return m.group(1) if m else text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("items"); ap.add_argument("out")
    ap.add_argument("--conditions", default="bare,rules")
    ap.add_argument("--gguf", default="/home/shimin/ai/models/qwen3.8-27b/Qwen3.8-27B-UD-Q4_K_XL.gguf")
    ap.add_argument("--max-tokens", type=int, default=4096)
    ap.add_argument("--lora"); ap.add_argument("--seeds", default="0"); ap.add_argument("--parallel", type=int, default=1)
    ap.add_argument("--ctx-per-slot", type=int, default=0, help="default: room for the prompt and --max-tokens")
    ap.add_argument("--name-seeds", action="store_true", help="name files <id>__s<seed> even with a single seed")
    a = ap.parse_args()
    items = json.load(open(a.items))
    if isinstance(items, dict):
        items = [it for group in items.values() for it in group]
    seeds = [int(x) for x in a.seeds.split(",")]
    ctx = a.ctx_per_slot or a.max_tokens + 768
    systems = json.load(open(os.path.join(HERE, "system_prompts.json")))
    with socket.socket() as s:
        if s.connect_ex(("127.0.0.1", PORT)) == 0:
            sys.exit(f"something already listens on {PORT}; refusing")
    os.makedirs(a.out, exist_ok=True)
    log = open(os.path.join(a.out, "server.log"), "w")
    srv = subprocess.Popen([BIN, "-m", a.gguf, "-c", str(ctx * a.parallel), "--parallel", str(a.parallel), "-ngl", "all", "--fit", "off",
                            "--host", "127.0.0.1", "--port", str(PORT), "--reasoning", "off"] + (["--lora", a.lora] if a.lora else []),
                           stdout=log, stderr=log)
    try:
        t0 = time.time()
        while True:
            if srv.poll() is not None:
                sys.exit("server exited; see server.log")
            try:
                if json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health", timeout=2)).get("status") == "ok":
                    break
            except Exception:
                pass
            if time.time() - t0 > 300:
                sys.exit("server did not come up in 300 s")
            time.sleep(2)
        print(f"server ready after {time.time() - t0:.0f}s", flush=True)
        gl, lock = open(os.path.join(a.out, "generation.jsonl"), "a"), threading.Lock()
        jobs = []
        for cond in a.conditions.split(","):
            os.makedirs(os.path.join(a.out, cond), exist_ok=True)
            for it in items:
                for seed in seeds:
                    base = os.path.join(a.out, cond, it["id"] + (f"__s{seed}" if len(seeds) > 1 or a.name_seeds else ""))
                    if not os.path.exists(base + ".py"):
                        jobs.append((cond, it, seed, base))
        print(f"{len(jobs)} to generate", flush=True)

        def one(job):
            cond, it, seed, base = job
            t = time.time()
            try:
                r = post("/v1/chat/completions", {
                    "messages": [{"role": "system", "content": systems[cond]}, {"role": "user", "content": it["prompt"]}],
                    "temperature": 0.7, "top_p": 0.8, "top_k": 20, "seed": seed, "max_tokens": a.max_tokens}, timeout=3600)
            except Exception as e:  # left for the next run
                print(f"{cond:6s} {os.path.basename(base):26s} failed: {type(e).__name__}: {str(e)[:100]}", flush=True)
                return
            msg = r["choices"][0]["message"]
            text = msg.get("content") or ""
            rec = {"id": it["id"], "seed": seed, "file": os.path.basename(base), "condition": cond, "prompt": it["prompt"],
                   "seconds": round(time.time() - t, 1), "finish_reason": r["choices"][0].get("finish_reason"), "usage": r.get("usage"),
                   "had_reasoning": bool(msg.get("reasoning_content")), "model": os.path.basename(a.gguf),
                   "lora": os.path.basename(a.lora) if a.lora else None}
            with lock:
                open(base + ".txt", "w").write(text)
                open(base + ".py", "w").write(code_of(text))
                gl.write(json.dumps(rec) + "\n"); gl.flush()
                print(f"{cond:6s} {os.path.basename(base):26s} {rec['seconds']:6.1f}s {(rec['usage'] or {}).get('completion_tokens')} tokens {rec['finish_reason']}", flush=True)

        t_all = time.time()
        with ThreadPoolExecutor(a.parallel) as ex:
            list(ex.map(one, jobs))
        gl.close()
        print(f"done in {time.time() - t_all:.0f}s", flush=True)
    finally:
        srv.terminate()
        try:
            srv.wait(timeout=30)
        except subprocess.TimeoutExpired:
            srv.kill()


if __name__ == "__main__":
    main()
