"""Static integrity audit for private suite authoring."""
import ast
from collections import Counter, defaultdict
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    tasks = sorted(ROOT.glob('*/meta.json'))
    counts = defaultdict(Counter)
    visible = hidden = 0
    for meta_path in tasks:
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
        task = meta_path.parent
        counts[meta['family']]['tasks'] += 1
        counts[meta['family']]['level' + str(meta['level'])] += 1
        counts[meta['family']]['files'] += sum(p.is_file() for p in task.rglob('*'))
        source = (task/'solution/task.py').read_text(encoding='utf-8')
        if meta['level'] == 2:
            assert 60 <= len(source.splitlines()) <= 100, task
        for item in (task/'solution').rglob('*'):
            if item.is_file():
                original = task/'start'/item.relative_to(task/'solution')
                assert not original.exists() or original.read_bytes() != item.read_bytes(), item
        text = (task/'TASK.md').read_text(encoding='utf-8')
        assert '\r' not in text and '\t' not in text, task
        for directory in ['start/tests', 'hidden']:
            tree = ast.parse((task/directory/'test_task.py').read_text(encoding='utf-8'))
            n = sum(isinstance(node, ast.FunctionDef) and node.name.startswith('test_') for node in tree.body)
            if directory == 'hidden':
                hidden += n
                assert n >= 9, task
            else:
                visible += n
                assert n in (3, 4), task
        for path in task.rglob('*.py'):
            compile(path.read_text(encoding='utf-8'), str(path), 'exec')
            tree = ast.parse(path.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = [n.name.split('.')[0] for n in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [(node.module or '').split('.')[0]]
                else:
                    continue
                assert not set(names) & {'requests', 'httpx', 'socket', 'random', 'time', 'datetime'}, path
    for path in ROOT.rglob('*'):
        if path.is_file() and path.suffix in {'.py', '.md', '.json'}:
            text = path.read_text(encoding='utf-8-sig')
            assert all(line == line.rstrip() for line in text.splitlines()), path
    assert len(tasks) == 48
    for family, count in sorted(counts.items()):
        print(f"{family}: {dict(count)}")
    print(f"CHECKED: 48 layouts, changed-only overlays, level-2 sizes, imports, syntax, whitespace; "
          f"{visible} visible / {hidden} full scoring groups")


if __name__ == '__main__':
    main()
