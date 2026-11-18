"""Prove the mechanical fairness contract in isolated, disposable folders."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent
FIELDS = {"id", "family", "level", "kind", "timeout_s"}


def inventory(task):
    for name in ("TASK.md", "meta.json"):
        if not (task / name).is_file():
            raise ValueError(f"missing {name}")
    for name in ("start", "start/tests", "hidden", "solution"):
        if not (task / name).is_dir():
            raise ValueError(f"missing {name}/")
    for name in ("start/tests", "hidden"):
        if not list((task / name).rglob("test_*.py")):
            raise ValueError(f"no pytest files in {name}")
    meta = json.loads((task / "meta.json").read_text(encoding="utf-8"))
    if set(meta) != FIELDS or meta["id"] != task.name:
        raise ValueError("invalid metadata fields or id")
    if not isinstance(meta["family"], str) or not meta["family"]:
        raise ValueError("invalid family")
    if type(meta["level"]) is not int or meta["level"] not in (2, 3, 4):
        raise ValueError("invalid level")
    if meta["kind"] not in ("implement", "fix", "extend"):
        raise ValueError("invalid kind")
    if type(meta["timeout_s"]) not in (int, float) or not 0 < meta["timeout_s"] < 10:
        raise ValueError("timeout must be positive and below 10 seconds")
    overlay = list((task / "solution").rglob("*.py"))
    if not overlay or any(p.relative_to(task / "solution").parts[0] == "tests" for p in overlay):
        raise ValueError("empty solution or solution changes tests")
    return meta


def run(folder, timeout):
    env = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PYTHONDONTWRITEBYTECODE="1",
               PYTHONHASHSEED="0", PYTHONIOENCODING="utf-8")
    # Do not inherit a repository PYTHONPATH or pytest configuration from the caller.
    env.pop("PYTHONPATH", None)
    env.pop("PYTEST_ADDOPTS", None)
    before = time.perf_counter()
    result = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=folder,
                            capture_output=True, text=True, encoding="utf-8", env=env, timeout=timeout)
    return result.returncode, time.perf_counter() - before, result.stdout + result.stderr


MIN_NEW_LINES = 12


def new_lines(task):
    """Non-blank solution lines that are not already somewhere in the matching start/ file: an implement or extend
    task whose start/ holds the answer behind a `raise` or as dead code scores low here."""
    count = 0
    for src in (task / "solution").rglob("*.py"):
        base = task / "start" / src.relative_to(task / "solution")
        have = {ln.strip() for ln in base.read_text(encoding="utf-8").splitlines()} if base.is_file() else set()
        count += sum(1 for ln in src.read_text(encoding="utf-8").splitlines() if ln.strip() and ln.strip() not in have)
    return count


def check(task, meta):
    with tempfile.TemporaryDirectory(prefix="strata-tasks2-") as tmp:
        work = Path(tmp) / "work"
        shutil.copytree(task / "start", work)
        shutil.rmtree(work / "tests")
        shutil.copytree(task / "hidden", work / "tests")
        initial, t0, log0 = run(work, meta["timeout_s"])
        # pytest exit 1 is assertion failure; collection errors/no tests are not proof.
        if initial != 1 or "failed" not in log0 or "ERROR collecting" in log0:
            raise ValueError(f"start must fail executed tests (exit {initial}):\n{log0}")
        for src in (task / "solution").rglob("*"):
            if src.is_file():
                dst = work / src.relative_to(task / "solution")
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
        solved, t1, log1 = run(work, meta["timeout_s"])
        if solved != 0:
            raise ValueError(f"reference hidden failed (exit {solved}):\n{log1}")
        shutil.rmtree(work / "tests")
        shutil.copytree(task / "start/tests", work / "tests")
        visible, t2, log2 = run(work, meta["timeout_s"])
        if visible != 0:
            raise ValueError(f"reference visible failed (exit {visible}):\n{log2}")
        new = new_lines(task)
        if meta["kind"] in ("implement", "extend") and new < MIN_NEW_LINES:
            raise ValueError(f"leak: only {new} solution lines are not already in start/ (need {MIN_NEW_LINES})")
        return f"start FAIL; reference hidden PASS; reference visible PASS ({t0:.2f}/{t1:.2f}/{t2:.2f}s); {new} new lines"


def main():
    """validate.py [ROOT] [--prune]: ROOT defaults to this folder; --prune deletes the tasks that fail instead of failing."""
    args = [x for x in sys.argv[1:] if x != "--prune"]
    prune = "--prune" in sys.argv[1:]
    root = Path(args[0]).resolve() if args else ROOT
    tasks = sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith(("_", ".")))
    if prune:
        # only a generated task folder may be pruned: every entry must look like a task, and this audited set is never pruned
        if root == ROOT or not tasks or any(not (p / "meta.json").is_file() for p in tasks):
            print("--prune refused: " + ("this folder is the audited set" if root == ROOT else
                                         "not every subfolder is a task (meta.json missing)"))
            return 2
    failures, metadata, kept_broken = [], [], []
    for task in tasks:
        try:
            meta = inventory(task)
            metadata.append(meta)
            print(f"{task.name}: {check(task, meta)}", flush=True)
        except (ValueError, OSError, subprocess.TimeoutExpired, TypeError) as exc:
            failures.append(task.name)
            print(f"{task.name}: BROKEN: {str(exc).splitlines()[0][:160]}", flush=True)
            if prune and isinstance(exc, ValueError):   # unfair by the rules; a timeout or an I/O error is not a verdict
                shutil.rmtree(task)
            elif prune:
                kept_broken.append(task.name)
    if failures and prune:
        if kept_broken:
            print(f"NOT PRUNED (timeout or I/O error, run again): " + ", ".join(kept_broken))
            return 1
        print(f"PRUNED {len(failures)}: " + ", ".join(failures))
        print(f"ALL {len(tasks) - len(failures)} TASKS FAIR")
        return 0
    if failures:
        print("FAILURES: " + ", ".join(failures))
        return 1
    print(f"ALL {len(tasks)} TASKS FAIR")
    return 0


if __name__ == "__main__":
    sys.exit(main())
