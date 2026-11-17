"""Private suite authoring helpers; never copy this directory to an agent."""
import ast
import json
import textwrap
from pathlib import Path
from enrich import enrich, readable

ROOT = Path(__file__).resolve().parents[1]
FOOT = ("\n\nRun `python -m pytest -q` in this folder to check your work, and keep going until every test passes. "
        "Do not change anything under `tests/`. Use only the Python standard library.\n")


def clean(text):
    return textwrap.dedent(text).strip() + "\n"


def stub(source):
    class Stub(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            node.body = [ast.Raise(exc=ast.Call(func=ast.Name(id="NotImplementedError", ctx=ast.Load()),
                                              args=[], keywords=[]), cause=None)]
            return node
    return ast.unparse(ast.fix_missing_locations(Stub().visit(ast.parse(source)))) + "\n"


def emit(ident, family, level, kind, spec, solution, checks, *, start=None, imports="from task import *"):
    spec, solution, checks = enrich(ident, spec, solution, checks)
    assert len(checks) >= 9, ident
    solution = {k: clean(v) for k, v in (solution if isinstance(solution, dict) else {"task.py": solution}).items()}
    if start is None:
        assert kind == "implement", ident
        start = {k: stub(v) for k, v in solution.items()}
    elif isinstance(start, list):
        base = dict(solution)
        for path, old, new in start:
            assert old in base[path], (ident, old)
            base[path] = base[path].replace(old, new, 1)
        start = base
    else:
        start = {k: clean(v) for k, v in start.items()}
    assert any(start.get(k) != v for k, v in solution.items()), ident
    task = ROOT / ident
    files = {"TASK.md": clean(spec).rstrip() + FOOT,
             "meta.json": json.dumps(dict(id=ident, family=family, level=level, kind=kind, timeout_s=9), indent=2) + "\n"}
    header = "import pytest\nfrom copy import deepcopy\n" + imports + "\n\n"
    tests = [f"def test_case_{i:02d}():\n" + textwrap.indent(clean(check), "    ") for i, check in enumerate(checks)]
    files["start/tests/test_task.py"] = header + "\n\n".join(tests[:max(3, len(tests) // 3)])
    files["hidden/test_task.py"] = header + "\n\n".join(tests)
    files.update({"start/" + k: readable(v, ident) for k, v in start.items()})
    files.update({"solution/" + k: readable(v, ident) for k, v in solution.items() if v != start.get(k)})
    for name, content in files.items():
        dst = task / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    import runpy
    for path in sorted(Path(__file__).parent.glob("family_*.py")):
        runpy.run_path(str(path))
