"""Let a local model (llama.cpp server) build a scene over many runs: it writes code, sees the result and a picture
of the scene, and writes more, until its context is full.

Usage: python blender_task/agent_loop.py <items.json> <out dir> [--lora ADAPTER.gguf] [--ctx 32768] [--parallel 2]
                                         [--only id,id] [--max-reply 8192] [--max-turns 80]
items.json is a list of {"id", "prompt"} (or a dict of such lists). One session per item, in <out>/<id>/:
  steps/step_NN.txt   the model's whole reply           steps/step_NN.py          the code block in it
  steps/step_NN.png   the scene after that run          steps/step_NN.result.json what the run did
  final.png           the scene at the end, larger      session.json              the numbers; transcript.jsonl the messages
  work/               the only folder the sandbox can write: the scene (state.blend) as the last run left it
A session that has a session.json is skipped, so a stopped run can be started again.

Each turn the model replies with one Python code block. It runs in a sandboxed Blender (bubblewrap: read-only
filesystem except work/, no network) that opens the scene the last run left: the scene is kept between runs, Python
variables are not, as with a live Blender behind a "run this Python" tool. The model then gets the error or "ran",
what was printed, a count of what the scene holds, a picture of the scene (through its own camera if it has set one
up; 768 pixels a side, about 600 tokens), and how much room is left. The session ends when the next reply would not fit in the context (--ctx tokens for
each session; everything stays in the context, pictures included). A reply cut off by the end of the context is not run.
Starts its own server on port 8099 (never 8080), thinking off, with the model's vision part, and stops it afterwards.
"""
import argparse, base64, json, os, queue, shutil, signal, socket, subprocess, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from generate import BIN, PORT, HERE, post, code_of

BLENDER = os.path.realpath(os.path.expanduser("~/.local/bin/blender"))
STEP = os.path.join(HERE, "session_step.py")
SYSTEM = (json.load(open(os.path.join(HERE, "system_prompts.json")))["bare"] +          # the words the adapter was trained with, then the loop
          " After each run you are shown the result and a picture of the scene, and you reply with another code block that fixes or adds to it."
          " The scene is kept between runs; Python variables and functions are not.")
DETAIL = " Be detailed: build every part of the scene, and keep adding and refining detail for as long as you can."


def run_step(sdir, n, timeout, final=False, size=768):
    """Run steps/step_NN.py on the session's scene in the sandbox (final: only render it, larger). Returns the result
    (a dict of checked fields) and the picture's path outside the sandbox's reach, or None."""
    work, steps = os.path.join(sdir, "work"), os.path.join(sdir, "steps")
    state, name = os.path.join(work, "state.blend"), "final" if final else f"step_{n:02d}"
    png, res = os.path.join(work, name + ".png"), os.path.join(work, name + ".result.json")
    for f in (png, res):
        if os.path.lexists(f):
            os.remove(f)
    cmd = ["bwrap", "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc", "--tmpfs", "/tmp", "--bind", work, work,
           "--unshare-net", "--unshare-pid", "--unshare-ipc", "--die-with-parent", "--new-session",
           "--dir", "/tmp/home", "--setenv", "HOME", "/tmp/home", "--chdir", work,
           BLENDER, "--background", "--factory-startup", "--disable-autoexec"] + ([state] if os.path.isfile(state) and not os.path.islink(state) else []) + \
          ["--python", STEP, "--", "-" if final else os.path.join(steps, name + ".py"), png, res, state, f"size={size}", "samples=96" if final else "samples=48"]
    t = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        status = f"exit {p.returncode}"
    except subprocess.TimeoutExpired:
        status = "timeout"
    raw = {}
    if os.path.isfile(res) and not os.path.islink(res) and os.path.getsize(res) < 1_000_000:   # written inside the sandbox: take only what is expected
        try:
            raw = json.load(open(res))
        except Exception:
            raw = {}
    text = lambda k, n_: (str(raw.get(k))[:n_] if raw.get(k) else None)
    num = lambda k: (int(raw[k]) if isinstance(raw.get(k), (int, float)) else None)
    out = {"process": status, "seconds": round(time.time() - t, 1), "error": text("error", 320), "error_line": text("error_line", 200),
           "printed": text("printed", 600), "state_saved": raw.get("state_saved") is True, "n_objects": num("n_objects"), "n_lights": num("n_lights"),
           "n_materials": num("n_materials"), "own_camera": raw.get("own_camera") is True, "render_error": text("render_error", 200)}
    kept = None
    if os.path.isfile(png) and not os.path.islink(png):
        try:                                                  # decode and write again, so only a picture leaves the sandbox folder
            im = Image.open(png).convert("RGB")
            kept = os.path.join(sdir if final else steps, name + ".png")
            im.save(kept)
        except Exception:
            kept = None
    if not final:
        json.dump(out, open(os.path.join(steps, name + ".result.json"), "w"), indent=1)
    return out, kept


def tokens_of(text):
    try:
        return len(post("/tokenize", {"content": text}, timeout=60)["tokens"])
    except Exception:
        return len(text) // 3


def session(it, slot, a):
    sdir = os.path.join(a.out, it["id"])
    if os.path.exists(os.path.join(sdir, "session.json")):
        return
    shutil.rmtree(sdir, ignore_errors=True)                  # a session that stopped half-way starts over
    os.makedirs(os.path.join(sdir, "steps")); os.makedirs(os.path.join(sdir, "work"))
    ask = it["prompt"] + DETAIL
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": ask}]
    tr = open(os.path.join(sdir, "transcript.jsonl"), "w")
    for m in messages:
        tr.write(json.dumps(m) + "\n")
    turns, stop, t0 = [], None, time.time()
    used, next_prompt, picture_cost, last = 0, tokens_of(SYSTEM + ask) + 40, a.picture_tokens, None
    while stop is None:
        n = len(turns) + 1
        room = a.ctx - next_prompt - 48
        if n > a.max_turns:
            stop = "turn limit"; break
        if room < a.min_reply:
            stop = "out of context"; break
        cap = min(a.max_reply, room)
        t = time.time()
        try:
            r = post("/v1/chat/completions", {"messages": messages, "temperature": 0.7, "top_p": 0.8, "top_k": 20, "seed": a.seed,
                                              "max_tokens": cap, "id_slot": slot, "cache_prompt": True}, timeout=7200)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:300]
            if e.code == 400 and "context" in body.lower():
                stop = "out of context"
                break
            raise RuntimeError(f"server error {e.code}: {body}")   # the session is left without a session.json and runs again next time
        text, finish, usage = r["choices"][0]["message"].get("content") or "", r["choices"][0].get("finish_reason"), r.get("usage") or {}
        if last is not None and usage.get("prompt_tokens"):   # what the last result message really cost, picture included
            measured = usage["prompt_tokens"] - used - last["text_tokens"]
            if last["with_picture"] and 0 < measured < 6000:
                picture_cost = measured + 32
        used = usage.get("prompt_tokens", next_prompt) + usage.get("completion_tokens", 0)
        base = os.path.join(sdir, "steps", f"step_{n:02d}")
        open(base + ".txt", "w").write(text)
        open(base + ".py", "w").write(code_of(text))
        turn = {"turn": n, "prompt_tokens": usage.get("prompt_tokens"), "completion_tokens": usage.get("completion_tokens"), "finish_reason": finish,
                "reply_seconds": round(time.time() - t, 1), "tokens_per_second": (r.get("timings") or {}).get("predicted_per_second"),
                "prompt_tokens_processed": (r.get("timings") or {}).get("prompt_n"), "cap": cap}
        tr.write(json.dumps({"role": "assistant", "content": text}) + "\n"); tr.flush()
        messages.append({"role": "assistant", "content": text})
        if finish == "length" and cap < a.max_reply:         # the context ran out in the middle of the reply
            turn["run"] = None
            turns.append(turn)
            stop = "out of context (the last reply was cut off and not run)"
            break
        picture = None
        if finish == "length":
            res, head = None, f"Your reply was cut off at {cap} tokens before the code block ended, so nothing was run. Write a shorter step."
        else:
            res, picture = run_step(sdir, n, a.timeout, size=a.picture_size)
            if res["process"] == "timeout":
                head = f"Run {n}: stopped after {a.timeout} seconds without finishing. The scene is as it was before this run."
            elif not res["state_saved"]:
                head = f"Run {n}: Blender crashed" + (f" ({res['error']})" if res["error"] else "") + ". The scene is as it was before this run."
            elif res["error"]:
                head = f"Run {n}: error: {res['error']}" + (f"\n  at: {res['error_line']}" if res["error_line"] else "") + "\nWhatever ran before the error is in the scene."
            else:
                head = f"Run {n}: ran without error."
            if res["printed"]:
                head += f"\nPrinted: {res['printed']}"
            if res["n_objects"] is not None:
                head += f"\nThe scene holds {res['n_objects']} objects and {res['n_lights']} lights."
            if picture:
                head += " The picture shows it " + ("through its camera." if res["own_camera"] else "from a default view, because no camera has been set up.")
            elif res["process"] == "exit 0":
                head += " No picture could be rendered."
        turn["run"] = res
        turns.append(turn)
        body_tokens = tokens_of(head) + 60
        left = a.ctx - used - body_tokens - (picture_cost if picture else 0) - 48
        head += f"\nCarry on: fix what is wrong and add more detail. Reply with one Python code block; it runs in the same scene. Room left: about {max(left, 0) // 100 * 100} tokens."
        content = [{"type": "text", "text": head}]
        if picture:
            content.append({"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(open(picture, "rb").read()).decode()}})
        messages.append({"role": "user", "content": content})
        tr.write(json.dumps({"role": "user", "content": head, "picture": os.path.relpath(picture, sdir) if picture else None}) + "\n"); tr.flush()
        last = {"text_tokens": body_tokens, "with_picture": bool(picture)}
        next_prompt = used + body_tokens + (picture_cost if picture else 0)
        print(f"{it['id']:28s} turn {n:2d}  {turn['completion_tokens']} tokens  {turn['reply_seconds']:6.1f}s  "
              f"{'cut off' if res is None else res['error'][:60] if res['error'] else res['process'] if res['process'] != 'exit 0' else 'ran' if res['state_saved'] else 'crashed'}  "
              f"objects={res and res['n_objects']}  used {used}/{a.ctx}", flush=True)
    tr.close()
    fin, fpng = run_step(sdir, 0, a.timeout * 2, final=True, size=a.picture_size) if os.path.isfile(os.path.join(sdir, "work", "state.blend")) else ({}, None)
    ran = [t_ for t_ in turns if t_.get("run")]
    json.dump({"id": it["id"], "prompt": ask, "system": SYSTEM, "lora": os.path.basename(a.lora) if a.lora else None, "model": os.path.basename(a.gguf),
               "context": a.ctx, "stop": stop, "turns": len(turns), "runs": len(ran), "runs_with_error": sum(bool(t_["run"]["error"]) or t_["run"]["process"] != "exit 0" for t_ in ran),
               "tokens_written": sum(t_["completion_tokens"] or 0 for t_ in turns), "tokens_used": used, "picture_tokens": picture_cost,
               "minutes": round((time.time() - t0) / 60, 1), "final_objects": fin.get("n_objects"), "final_lights": fin.get("n_lights"),
               "final_own_camera": fin.get("own_camera"), "final_picture": bool(fpng), "turn_list": turns}, open(os.path.join(sdir, "session.json"), "w"), indent=1)
    print(f"{it['id']:28s} done: {stop}; {len(turns)} turns, {len(ran)} runs, {fin.get('n_objects')} objects, {(time.time() - t0) / 60:.1f} min", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("items"); ap.add_argument("out")
    ap.add_argument("--gguf", default="/home/shimin/ai/models/qwen3.8-27b/Qwen3.8-27B-UD-Q4_K_XL.gguf")
    ap.add_argument("--mmproj", default="/home/shimin/ai/models/qwen3.8-27b/mmproj-F16.gguf")
    ap.add_argument("--lora"); ap.add_argument("--ctx", type=int, default=32768, help="context for each session, in tokens")
    ap.add_argument("--parallel", type=int, default=2); ap.add_argument("--only", default="")
    ap.add_argument("--max-reply", type=int, default=8192, help="most tokens in one reply")
    ap.add_argument("--min-reply", type=int, default=700, help="stop when less room than this is left for a reply")
    ap.add_argument("--max-turns", type=int, default=80); ap.add_argument("--timeout", type=int, default=240, help="seconds for one run in Blender, as in the single-script tests")
    ap.add_argument("--picture-tokens", type=int, default=1200, help="first guess at what a picture costs; measured after the first one")
    ap.add_argument("--picture-size", type=int, default=768, help="pixels a side of the picture the model is shown")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    items = json.load(open(a.items))
    if isinstance(items, dict):
        items = [it for group in items.values() for it in group]
    if a.only:
        items = [it for it in items if it["id"] in a.only.split(",")]
    with socket.socket() as s:
        if s.connect_ex(("127.0.0.1", PORT)) == 0:
            sys.exit(f"something already listens on {PORT}; refusing")
    a.out = os.path.abspath(a.out)                            # the sandbox needs absolute paths
    os.makedirs(a.out, exist_ok=True)
    signal.signal(signal.SIGTERM, lambda *_: sys.exit("stopped"))   # so the server is stopped too
    log = open(os.path.join(a.out, "server.log"), "w")
    srv = subprocess.Popen([BIN, "-m", a.gguf, "--mmproj", a.mmproj, "-c", str(a.ctx * a.parallel), "--parallel", str(a.parallel), "-ngl", "all", "--fit", "off",
                            "--no-context-shift", "--host", "127.0.0.1", "--port", str(PORT), "--reasoning", "off"] + (["--lora", a.lora] if a.lora else []),
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
        print(f"server ready after {time.time() - t0:.0f}s; {len(items)} sessions, {a.ctx} tokens each, {a.parallel} at a time", flush=True)
        slots = queue.Queue()
        for k in range(a.parallel):
            slots.put(k)

        def one(it):
            if srv.poll() is not None:                        # the server is gone: leave the rest for the next start
                return
            slot = slots.get()
            try:
                session(it, slot, a)
            except Exception as e:
                print(f"{it['id']:28s} failed, to be run again: {type(e).__name__}: {str(e)[:200]}", flush=True)
            finally:
                slots.put(slot)

        t_all = time.time()
        with ThreadPoolExecutor(a.parallel) as ex:
            list(ex.map(one, items))
        print(f"done in {(time.time() - t_all) / 60:.0f} min", flush=True)
    finally:
        srv.terminate()
        try:
            srv.wait(timeout=30)
        except subprocess.TimeoutExpired:
            srv.kill()


if __name__ == "__main__":
    main()
