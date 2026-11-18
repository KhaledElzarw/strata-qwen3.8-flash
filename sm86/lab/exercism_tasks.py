"""Turn the Exercism Python track's practice exercises (MIT, github.com/exercism/python) into suite tasks.

    python exercism_tasks.py --src <checkout of exercism/python> [--polyglot <checkout of Aider-AI/polyglot-benchmark>]
                             [--out tasks_ex] [--commit SHA]

A published benchmark as the judge instead of home-made tasks: Aider's polyglot benchmark is the hard subset of these
exercises (its Python picks are marked in tasks_ex/index.json when --polyglot is given; only the names are taken from
that repository).  The exercises are not copied into this repository: run this against a checkout to build
sm86/lab/tasks_ex (git-ignored), then `python tasks2/validate.py tasks_ex --prune` drops the ones that are not a fair
task here (the stub already passes, the reference fails, or the solution is under 12 lines).

Each exercise becomes  <out>/ex_<slug>/  in the suite's layout (tasks2/README.md):
  TASK.md      the exercise's instructions (.docs/introduction.md, instructions.md, instructions.append.md) and what to edit
  start/       the stub file(s) and tests/test_<name>.py (Exercism shows its tests, as Aider does)
  hidden/      the same test file; scoring puts a pristine copy back, so an agent cannot pass by editing tests
  solution/    .meta/example.py under the stub's name
  meta.json    id, family "exercism", level (difficulty 1-2 -> 2, 3-4 -> 3, 5+ -> 4), kind "implement", timeout_s
"""
import argparse
import json
import shutil
from pathlib import Path

FOOT = ("\n\nImplement it in `{files}`. Run `python -m pytest -q` in this folder to check your work, and keep going until every "
        "test passes. Do not change anything under `tests/`. Use only the Python standard library.\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True)
    ap.add_argument("--polyglot")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "tasks_ex"))
    ap.add_argument("--commit", default="")
    a = ap.parse_args()
    src, out = Path(a.src), Path(a.out)
    track = json.loads((src / "config.json").read_text(encoding="utf-8"))["exercises"]["practice"]
    hard = set()
    if a.polyglot:
        hard = {p.name for p in (Path(a.polyglot) / "python" / "exercises" / "practice").iterdir() if p.is_dir()}
    if out.exists():
        if any(out.iterdir()) and not (out / "index.json").is_file():
            raise SystemExit(f"{out} exists and is not an earlier output of this tool (no index.json): not deleting it")
        shutil.rmtree(out)
    out.mkdir(parents=True)
    index, skipped = [], []
    for ex in track:
        slug = ex["slug"]
        d = src / "exercises" / "practice" / slug
        if ex.get("status") == "deprecated" or not (d / ".meta" / "config.json").is_file():
            skipped.append(slug)
            continue
        files = json.loads((d / ".meta" / "config.json").read_text(encoding="utf-8"))["files"]
        sol, tests, example = files.get("solution", []), files.get("test", []), files.get("example", [])
        if len(sol) != 1 or len(tests) != 1 or len(example) != 1 or not (d / sol[0]).is_file() or not (d / example[0]).is_file():
            skipped.append(slug)
            continue
        tid = "ex_" + slug.replace("-", "_")
        t = out / tid
        (t / "start" / "tests").mkdir(parents=True)
        (t / "hidden").mkdir()
        (t / "solution").mkdir()
        docs = [d / ".docs" / n for n in ("introduction.md", "instructions.md", "instructions.append.md")]
        text = "\n\n".join(p.read_text(encoding="utf-8").strip() for p in docs if p.is_file())
        (t / "TASK.md").write_text(f"# {ex['name']}\n\n{text}" + FOOT.format(files=sol[0]), encoding="utf-8", newline="\n")
        for p in d.iterdir():                                   # the stub and any helper file the exercise ships
            if p.is_file() and p.name not in tests and not p.name.startswith("."):
                shutil.copyfile(p, t / "start" / p.name)
        test_name = "test_" + Path(tests[0]).name.replace("_test.py", ".py")
        for dst in (t / "start" / "tests" / test_name, t / "hidden" / test_name):
            shutil.copyfile(d / tests[0], dst)
        shutil.copyfile(d / example[0], t / "solution" / sol[0])
        level = 2 if ex["difficulty"] <= 2 else 3 if ex["difficulty"] <= 4 else 4
        (t / "meta.json").write_text(json.dumps({"id": tid, "family": "exercism", "level": level, "kind": "implement", "timeout_s": 9}),
                                     encoding="utf-8")
        index.append({"id": tid, "slug": slug, "difficulty": ex["difficulty"], "polyglot": slug in hard})
    (out / "index.json").write_text(json.dumps({"source": "github.com/exercism/python", "commit": a.commit, "licence": "MIT",
                                                "tasks": index}, indent=1), encoding="utf-8")
    print(f"{out}: {len(index)} tasks ({sum(1 for i in index if i['polyglot'])} in Aider's polyglot set), skipped {len(skipped)}: "
          f"{', '.join(skipped[:20])}")


if __name__ == "__main__":
    main()
