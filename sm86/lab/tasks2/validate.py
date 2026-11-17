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
        return f"start FAIL; reference hidden PASS; reference visible PASS ({t0:.2f}/{t1:.2f}/{t2:.2f}s)"


def main():
    tasks = sorted(p for p in ROOT.iterdir() if p.is_dir() and not p.name.startswith(("_", ".")))
    failures, metadata = [], []
    for task in tasks:
        try:
            meta = inventory(task)
            metadata.append(meta)
            print(f"{task.name}: {check(task, meta)}", flush=True)
        except (ValueError, OSError, subprocess.TimeoutExpired, TypeError) as exc:
            failures.append(task.name)
            print(f"{task.name}: BROKEN: {exc}", flush=True)
    from collections import Counter
    families = Counter(m["family"] for m in metadata)
    if len(tasks) != 48 or len(families) != 12 or set(families.values()) != {4}:
        failures.append("suite must contain 12 families of 4 tasks")
    levels = Counter(m["level"] for m in metadata)
    kinds = Counter(m["kind"] for m in metadata)
    if levels != {2: 16, 3: 16, 4: 16} or kinds["fix"] < 12 or kinds["extend"] < 8:
        failures.append(f"suite distribution: levels={dict(levels)}, kinds={dict(kinds)}")
    if failures:
        print("FAILURES: " + ", ".join(failures))
        return 1
    print(f"ALL {len(tasks)} TASKS FAIR")
    return 0


if __name__ == "__main__":
    sys.exit(main())
