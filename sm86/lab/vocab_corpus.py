"""Assemble a broad English + code corpus for the draft vocabulary (issue #37).

    python vocab_corpus.py OUTDIR
    python ../../tools/draft_vocab.py --gguf <model shard 1> --base ../../data/draft_vocab_en.bin \n        --corpus OUTDIR/corpus/*.txt --coverage 1.0 --out ../../data/draft_vocab_en_code.bin

data/draft_vocab_en_code.bin (55,034 ids) was built this way on 2026-11-17: the shipped 106,299-id list is 62% Han,
kana and hangul, and 3.0% of the tokens of held-out agent turns were outside it; with this list 0.22% are.

Sources: this repo's tracked source and docs, Python's standard library, unified diffs from git history,
synthetic agent tool calls (Hermes-style and Anthropic-style JSON) built from real repo paths and lines, and
the recorded agent turns (first half only; the second half is held out to test coverage).
"""
import json
import pathlib
import random
import subprocess
import sys
import sysconfig

REPO = pathlib.Path(__file__).resolve().parents[2]
if len(sys.argv) != 2:
    sys.exit(__doc__)
OUT = pathlib.Path(sys.argv[1]) / "corpus"
OUT.mkdir(parents=True, exist_ok=True)
rng = random.Random(7)


def put(name, text):
    (OUT / name).write_text(text, encoding="utf-8", newline="\n")
    print(f"{name}: {len(text) / 1e6:.2f} MB", flush=True)


def read(p, cap=200_000):
    try:
        return p.read_text(encoding="utf-8")[:cap]
    except (UnicodeDecodeError, OSError):
        return ""


def ascii_mostly(t):
    return t and sum(1 for c in t if ord(c) < 128) / len(t) > 0.97


files = subprocess.run(["git", "-C", str(REPO), "ls-files"], capture_output=True, text=True, encoding="utf-8").stdout.split("\n")
by_ext = {}
for f in files:
    ext = pathlib.PurePosixPath(f).suffix.lower()
    if "third_party/" in f or "/runs/" in f or f.endswith(".min.js"):
        continue
    by_ext.setdefault(ext, []).append(f)

GROUPS = {
    "repo_cpp.txt": ([".cpp", ".h", ".hpp", ".cu", ".cuh", ".inl", ".c"], 6_000_000),
    "repo_py.txt": ([".py"], 5_000_000),
    "repo_docs.txt": ([".md", ".txt"], 3_000_000),
    "repo_cfg.txt": ([".json", ".toml", ".yml", ".yaml", ".cmake", ".sh", ".ps1", ".bat", ".nix"], 1_500_000),
    "repo_web.txt": ([".js", ".ts", ".tsx", ".html", ".css", ".mjs"], 2_500_000),
}
lines_pool, paths_pool = [], []
for name, (exts, cap) in GROUPS.items():
    fs = [f for e in exts for f in by_ext.get(e, [])]
    rng.shuffle(fs)
    buf, n = [], 0
    for f in fs:
        t = read(REPO / f)
        if not ascii_mostly(t):
            continue
        buf.append(t)
        n += len(t)
        paths_pool.append(f)
        ls = [ln for ln in t.split("\n") if 12 < len(ln) < 140]
        lines_pool.extend(rng.sample(ls, min(len(ls), 6)))
        if n >= cap:
            break
    put(name, "\n".join(buf))

std = pathlib.Path(sysconfig.get_paths()["stdlib"])
fs = sorted(p for p in std.glob("*.py")) + sorted(p for p in std.glob("*/*.py") if "test" not in p.parts and "site-packages" not in p.parts)
rng.shuffle(fs)
buf, n = [], 0
for p in fs:
    t = read(p)
    if ascii_mostly(t):
        buf.append(t)
        n += len(t)
    if n >= 5_000_000:
        break
put("py_stdlib.txt", "\n".join(buf))

d = subprocess.run(["git", "-C", str(REPO), "log", "-p", "-120", "--no-color", "--", "src", "tools", "serve", "strata_control", "sm86/lab/*.py"],
                   capture_output=True, text=True, encoding="utf-8", errors="ignore").stdout
put("git_diffs.txt", "\n".join(ln for ln in d.split("\n") if not ln.startswith(("Author:", "Date:", "commit ")))[:3_000_000])

# synthetic tool calls: Hermes-style <tool_call> JSON and Anthropic-style tool_use inputs, generic paths only
cmds = ["git status", "git diff --stat", "python -m pytest -q", "ls -la", "npm test", "cargo build", "make -j8", "pip install -e .",
        "grep -rn \"TODO\" src", "python -m pytest -q tests/test_{}.py", "cat {}", "sed -n '1,80p' {}", "git log --oneline -5", "node {}",
        "python {}", "rg -n \"def \" {}", "cmake --build build --config Release", "go test ./...", "uv run pytest -x", "npx tsc --noEmit"]
buf = []
for _ in range(9000):
    p = rng.choice(paths_pool)
    full = rng.choice(["/home/user/project/", "/workspace/", "C:\\\\work\\\\project\\\\", "./", "/tmp/task/"]) + p
    a, b = rng.choice(lines_pool), rng.choice(lines_pool)
    kind = rng.randrange(8)
    if kind == 0:
        o = {"name": "Read", "input": {"file_path": full, "offset": rng.randrange(1, 400), "limit": rng.choice([50, 100, 200, 2000])}}
    elif kind == 1:
        o = {"name": "Edit", "input": {"file_path": full, "old_string": a, "new_string": b, "replace_all": False}}
    elif kind == 2:
        o = {"name": "Bash", "input": {"command": rng.choice(cmds).format(p), "description": "Run the tests", "timeout": 120000}}
    elif kind == 3:
        o = {"name": "Grep", "input": {"pattern": a.strip().split("(")[0][:30], "path": full, "output_mode": "content", "-n": True}}
    elif kind == 4:
        o = {"name": "Write", "input": {"file_path": full, "content": a + "\n" + b + "\n"}}
    elif kind == 5:
        o = {"name": "terminal", "arguments": {"command": rng.choice(cmds).format(p), "timeout": 60}}
    elif kind == 6:
        o = {"name": "patch", "arguments": {"path": p, "old_string": a, "new_string": b}}
    else:
        o = {"name": "read_file", "arguments": {"path": p, "offset": 1, "limit": 200}}
    s = json.dumps(o)
    buf.append(f"<tool_call>\n{s}\n</tool_call>" if "arguments" in o else s)
    if rng.random() < 0.3:
        buf.append(rng.choice(["Let me check the failing test first.", "I'll read the file and then fix the bug.", "The tests pass now.",
                               "Now I need to update the function to handle the edge case.", "Let me run the tests again.",
                               "Done. All tests pass.", "I'll start by looking at the current implementation.",
                               "Wait, that's not right. Let me re-read the specification.", "Hmm, the error says the key is missing."]))
put("tool_calls.txt", "\n".join(buf))

# recorded agent turns: outputs of the first half go into the corpus, the second half is the held-out test
import glob
rows = [json.loads(l) for l in open(REPO / "sm86/lab/runs/replay/bundle1-g41s8-r0.jsonl", encoding="utf-8") if l.strip()]
print("turn record keys:", sorted(rows[0].keys()), flush=True)


def turn_text(r):
    parts = []
    for k in ("reasoning", "content", "text"):
        v = r.get(k)
        if isinstance(v, str):
            parts.append(v)
    for tc in r.get("tool_calls") or []:
        parts.append(json.dumps(tc) if not isinstance(tc, str) else tc)
    return "\n".join(parts)


texts = [turn_text(r) for r in rows]
print("turns with text:", sum(1 for t in texts if t), "of", len(texts), flush=True)
half = len(texts) // 2
put("turns_train.txt", "\n".join(texts[:half]))
(OUT.parent / "turns_heldout.txt").write_text("\n".join(texts[half:]), encoding="utf-8", newline="\n")
print("held-out chars:", sum(len(t) for t in texts[half:]))
