"""Run the harder task suite (sm86/lab/tasks2) through an agent harness and score it.

    python suite2.py run --name base --reps 3 [--tasks id,id | --tasks-file FILE] [--agent hermes] [--timeout 900]
    python suite2.py table runs/suite2/base.jsonl [...]            pass rate per task, and which tasks sit at 20-80%
    python suite2.py compare runs/suite2/base.jsonl runs/suite2/cand.jsonl [--tasks-file FILE]

A task is plain files (tasks2/<id>/: TASK.md, start/, hidden/, meta.json), so any harness can run it: the agent gets a
fresh copy of start/ and the text of TASK.md; scoring replaces the copy's tests/ with hidden/ and runs pytest there.
`run` appends one JSON line per (task, repetition) and skips the ones already in the file, so it can be resumed.

Agents: "hermes" (Hermes Agent, one-shot; HERMES_EXE and HERMES_HOME say where it lives) or --agent-cmd, a command
template with {prompt} (the prompt file) and {work} (the working folder), for any other harness.
`compare` pairs the two files by task: the difference in pass rate with a bootstrap interval over tasks.
"""
import argparse
import json
import os
import random
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

LAB = Path(__file__).resolve().parent
ROOTS = [LAB / "tasks2", LAB / "tasks_ex"]      # the home-made tasks and the Exercism ones (exercism_tasks.py)
RUNS = LAB / "runs" / "suite2"
MODEL = "qwen3.8-flash-next-iq3_xxs"
BASE_URL = os.environ.get("SUITE2_BASE_URL", "http://127.0.0.1:19100/v1")


def task_ids(a):
    if a.tasks_file:
        return [x for x in Path(a.tasks_file).read_text(encoding="utf-8").split() if x]
    if a.tasks:
        return a.tasks.split(",")
    return sorted(p.name for r in ROOTS if r.is_dir() for p in r.iterdir() if (p / "meta.json").is_file())


def task_dir(tid):
    for r in ROOTS:
        if (r / tid / "meta.json").is_file():
            return r / tid
    raise SystemExit(f"no task {tid}")


def fresh_copy(tid, root):
    work = root / f"{tid}-{int(time.time() * 1000)}"
    shutil.copytree(task_dir(tid) / "start", work)
    shutil.copy2(task_dir(tid) / "TASK.md", work / "TASK.md")
    for args in (["init", "-q"], ["add", "-A"], ["-c", "user.name=suite2", "-c", "user.email=suite2@local", "commit", "-q", "-m", "task start"]):
        subprocess.run(["git", *args], cwd=work, capture_output=True)
    return work


PYTEST_CONFIGS = ("pytest.ini", "tox.ini", "setup.cfg", "pyproject.toml", "conftest.py")


def grade(tid, work, timeout):
    """tasks2/README.md's scoring contract: a fresh copy of the agent's folder, its tests/ replaced by hidden/, a clean pytest.
    Nothing the agent added can steer the run: pytest config files, conftest.py and test files that the task did not ship
    are removed, pytest gets an empty config of its own and is pointed at tests/ only."""
    import tempfile
    start = task_dir(tid) / "start"
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTEST_ADDOPTS")}
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    with tempfile.TemporaryDirectory(prefix="suite2-", ignore_cleanup_errors=True) as tmp:
        copy = Path(tmp) / "w"
        shutil.copytree(work, copy, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
        shutil.rmtree(copy / "tests", ignore_errors=True)
        for p in list(copy.rglob("*")):
            rel = p.relative_to(copy)
            added = not (start / rel).exists()
            if p.is_file() and added and (p.name in PYTEST_CONFIGS or p.name.startswith("test_") or p.name.endswith("_test.py")):
                p.unlink()
        shutil.copytree(task_dir(tid) / "hidden", copy / "tests")
        (copy / "suite2-pytest.ini").write_text("[pytest]\n", encoding="utf-8")
        try:
            r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-c", "suite2-pytest.ini", "tests"],
                               cwd=copy, capture_output=True, text=True, timeout=timeout, env=env)
            return {"pass": r.returncode == 0, "pytest": (r.stdout.strip().splitlines() or [""])[-1][:200]}
        except subprocess.TimeoutExpired:
            return {"pass": False, "pytest": "pytest timed out"}


def engine_up():
    """The engine answers at BASE_URL: a run with the engine down would record every task as a failure."""
    import urllib.request
    try:
        with urllib.request.urlopen(BASE_URL + "/models", timeout=10) as r:
            return r.status == 200
    except OSError:
        return False


def run_agent(cmd, work, env, timeout):
    """Runs the agent with its output in files, not pipes (a grandchild that keeps a pipe open would hang the wait after
    a timeout), and stops its whole process tree when the time is up.  Returns (exit code or "timeout", stderr tail)."""
    out, err = work / ".agent-stdout.txt", work / ".agent-stderr.txt"
    with open(out, "wb") as fo, open(err, "wb") as fe:
        p = subprocess.Popen(cmd, cwd=work, env=env, stdout=fo, stderr=fe, stdin=subprocess.DEVNULL)
        try:
            rc = p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            if os.name == "nt":
                subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
            else:
                p.kill()
            try:
                p.wait(timeout=30)
            except subprocess.TimeoutExpired:
                pass
            rc = "timeout"
    tail = err.read_bytes()[-300:].decode("utf-8", "replace") if rc != "timeout" else "agent timed out"
    for f in (out, err):
        f.unlink(missing_ok=True)
    return rc, tail


def agent_cmd(a, prompt, work):
    if a.agent_cmd:
        return [x.format(prompt=str(prompt), work=str(work)) for x in shlex.split(a.agent_cmd, posix=False)]
    exe = os.environ.get("HERMES_EXE") or str(Path(os.environ.get("LOCALAPPDATA", "")) / "hermes" / "bin" / "hermes.exe")
    return [exe, "--safe-mode", "chat", "--query-file", str(prompt), "--oneshot", "-Q", "--provider", "custom", "--base-url", BASE_URL,
            "--api-key", "strata-local", "-m", MODEL, "-t", "file,terminal", "--max-turns", str(a.max_turns), "--source", "tool"]


def run(a):
    RUNS.mkdir(parents=True, exist_ok=True)
    out = RUNS / f"{a.name}.jsonl"
    done = set()
    if out.is_file():
        done = {(r["task"], r["rep"]) for r in map(json.loads, out.read_text(encoding="utf-8").splitlines())}
    # The working folders stay OUTSIDE this repository by default: the agent has file and terminal tools, and inside the
    # lab tree it could reach tasks2/<id>/hidden and solution.
    import tempfile
    root = Path(os.environ.get("SUITE2_WORK", str(Path(tempfile.gettempdir()) / "suite2-work"))) / a.name
    root.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    if os.environ.get("HERMES_HOME"):
        env["HERMES_HOME"] = os.environ["HERMES_HOME"]
    ids = task_ids(a)
    deadline = None
    if a.deadline:                                      # HH:MM, its next occurrence: no task starts after it
        hh, mm = (int(x) for x in a.deadline.split(":"))
        now = time.localtime()
        deadline = time.mktime((now.tm_year, now.tm_mon, now.tm_mday, hh, mm, 0, 0, 0, -1))
        if deadline <= time.time():
            deadline += 86400
    reps = range(a.first_rep, a.first_rep + a.reps)
    for rep in reps:
        order = ids[:]
        random.Random(1000 + rep).shuffle(order)          # the same order for every arm
        for tid in order:
            if (tid, rep) in done:
                continue
            if deadline is not None and time.time() >= deadline:
                print(f"deadline {a.deadline} reached: stopping", flush=True)
                return 3
            if (LAB / "runs" / "THERMAL_STOP").exists():
                print("THERMAL_STOP present: stopping", flush=True)
                return 2
            if not engine_up():                             # nothing is recorded: the run resumes where it stopped
                print(f"the engine does not answer at {BASE_URL}: stopping", flush=True)
                return 4
            meta = json.loads((task_dir(tid) / "meta.json").read_text(encoding="utf-8"))
            work = fresh_copy(tid, root)
            prompt = work / ".task-prompt.md"
            prompt.write_text(f"You are working in the folder {work}. Everything you need is in it.\n\n"
                              + (task_dir(tid) / "TASK.md").read_text(encoding="utf-8"), encoding="utf-8")
            t0 = time.time()
            try:
                rc, tail = run_agent(agent_cmd(a, prompt, work), work, env, a.timeout)
            except OSError as e:                            # the harness itself could not start: not a task result
                print(f"the agent harness did not start ({e}): stopping", flush=True)
                shutil.rmtree(work, ignore_errors=True)
                return 4
            wall = round(time.time() - t0, 1)
            prompt.unlink(missing_ok=True)
            rec = {"task": tid, "rep": rep, "arm": a.name, "level": meta.get("level"), "family": meta.get("family"), "wall_s": wall,
                   "harness_rc": rc, "detail": tail, "t": int(t0), **grade(tid, work, int(meta.get("timeout_s", 60)) + 60)}
            with open(out, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec) + "\n")
            print(f"{a.name} rep {rep} {tid}: {'PASS' if rec['pass'] else 'fail'} {wall}s rc={rc} {rec['pytest']}", flush=True)
            if not a.keep:
                shutil.rmtree(work, ignore_errors=True)
            time.sleep(a.gap)
    return 0


def load(path):
    per = {}
    for r in map(json.loads, Path(path).read_text(encoding="utf-8").splitlines()):
        per.setdefault(r["task"], []).append(1 if r["pass"] else 0)
    return per


def table(a):
    for path in a.files:
        per = load(path)
        runs = sum(len(v) for v in per.values())
        rate = sum(sum(v) for v in per.values()) / max(1, runs)
        mid = sorted(t for t, v in per.items() if 0.2 <= sum(v) / len(v) <= 0.8)
        print(f"{path}: {len(per)} tasks, {runs} runs, pass rate {rate:.1%}; {len(mid)} tasks at 20-80%")
        for t in sorted(per):
            print(f"  {t:40s} {sum(per[t])}/{len(per[t])}")
        if a.write_mid:
            Path(a.write_mid).write_text("\n".join(mid) + "\n", encoding="utf-8")
            print(f"wrote {a.write_mid}: {len(mid)} task ids")
    return 0


def compare(a):
    A, B = load(a.base), load(a.cand)
    keep = set(Path(a.tasks_file).read_text(encoding="utf-8").split()) if a.tasks_file else None
    ids = sorted(t for t in A if t in B and (keep is None or t in keep))
    if not ids:
        sys.exit("no common tasks")
    d = [sum(B[t]) / len(B[t]) - sum(A[t]) / len(A[t]) for t in ids]
    ra = sum(sum(A[t]) / len(A[t]) for t in ids) / len(ids)
    rb = sum(sum(B[t]) / len(B[t]) for t in ids) / len(ids)
    rng = random.Random(7)
    boots = sorted(sum(rng.choice(d) for _ in ids) / len(ids) for _ in range(10000))
    lo, hi = boots[249], boots[9749]
    print(f"{len(ids)} tasks; base {ra:.1%} ({min(len(A[t]) for t in ids)}+ runs a task), candidate {rb:.1%} "
          f"({min(len(B[t]) for t in ids)}+ runs a task); "
          f"difference {100 * (rb - ra):+.1f} points, 95% interval {100 * lo:+.1f} to {100 * hi:+.1f} (paired by task)")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--name", required=True)
    r.add_argument("--reps", type=int, default=3)
    r.add_argument("--tasks")
    r.add_argument("--tasks-file")
    r.add_argument("--agent-cmd")
    r.add_argument("--timeout", type=int, default=900)
    r.add_argument("--max-turns", type=int, default=80, help="the agent's turn limit (hermes): a low limit is a stricter test, few tries")
    r.add_argument("--gap", type=float, default=2.0)
    r.add_argument("--deadline", help="HH:MM (local): start no task after this time")
    r.add_argument("--first-rep", type=int, default=0, help="number of the first repetition (to add one block at a time)")
    r.add_argument("--keep", action="store_true", help="keep each working folder")
    t = sub.add_parser("table")
    t.add_argument("files", nargs="+")
    t.add_argument("--write-mid", help="write the ids of the tasks at 20-80% here")
    c = sub.add_parser("compare")
    c.add_argument("base")
    c.add_argument("cand")
    c.add_argument("--tasks-file")
    a = ap.parse_args()
    return {"run": run, "table": table, "compare": compare}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
