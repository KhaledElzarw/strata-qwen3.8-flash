"""Regression checks for the validator itself; private authoring infrastructure."""
import importlib.util
import json
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[1] / 'validate.py'
spec = importlib.util.spec_from_file_location('tasks2_validator', MODULE)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def fixture_task(tmp_path):
    task = tmp_path / 'example'
    for name in ['start/tests', 'hidden', 'solution']:
        (task / name).mkdir(parents=True)
    (task / 'TASK.md').write_text('Implement answer.', encoding='utf-8')
    meta = dict(id='example', family='test', level=2, kind='implement', timeout_s=9)
    (task / 'meta.json').write_text(json.dumps(meta), encoding='utf-8')
    (task / 'start/task.py').write_text('def answer(): return 0\n', encoding='utf-8')
    (task / 'solution/task.py').write_text('def answer(): return 42\n', encoding='utf-8')
    test = 'from task import answer\n\ndef test_answer(): assert answer() == 42\n'
    (task / 'start/tests/test_task.py').write_text(test, encoding='utf-8')
    (task / 'hidden/test_task.py').write_text(test, encoding='utf-8')
    return task, meta


def test_fair_task_and_source_isolation(tmp_path, monkeypatch):
    task, meta = fixture_task(tmp_path)
    monkeypatch.setenv('PYTHONPATH', str(tmp_path / 'not-a-module-dir'))
    monkeypatch.setenv('PYTEST_ADDOPTS', '--option-that-does-not-exist')
    assert validator.inventory(task) == meta
    assert 'reference visible PASS' in validator.check(task, meta)
    assert 'return 0' in (task / 'start/task.py').read_text()
    assert not list(task.rglob('__pycache__'))


@pytest.mark.parametrize('field,value', [
    ('id', 'wrong'), ('level', True), ('level', 1), ('kind', 'other'),
    ('timeout_s', 10), ('timeout_s', 0), ('timeout_s', True), ('family', ''),
])
def test_invalid_metadata(tmp_path, field, value):
    task, meta = fixture_task(tmp_path)
    meta[field] = value
    (task / 'meta.json').write_text(json.dumps(meta), encoding='utf-8')
    with pytest.raises(ValueError):
        validator.inventory(task)


def test_missing_structure(tmp_path):
    task, _ = fixture_task(tmp_path)
    (task / 'TASK.md').unlink()
    with pytest.raises(ValueError, match='missing TASK.md'):
        validator.inventory(task)


def test_solution_cannot_change_tests(tmp_path):
    task, _ = fixture_task(tmp_path)
    (task / 'solution/tests').mkdir()
    (task / 'solution/tests/test_bad.py').write_text('pass', encoding='utf-8')
    with pytest.raises(ValueError, match='solution changes tests'):
        validator.inventory(task)


def test_passing_start_is_not_fair(tmp_path):
    task, meta = fixture_task(tmp_path)
    (task / 'start/task.py').write_text('def answer(): return 42\n', encoding='utf-8')
    with pytest.raises(ValueError, match='start must fail'):
        validator.check(task, meta)


def test_collection_error_is_not_a_fair_failure(tmp_path):
    task, meta = fixture_task(tmp_path)
    (task / 'start/task.py').write_text('not valid python !', encoding='utf-8')
    with pytest.raises(ValueError, match='start must fail'):
        validator.check(task, meta)


def test_failed_reference_is_rejected(tmp_path):
    task, meta = fixture_task(tmp_path)
    (task / 'solution/task.py').write_text('def answer(): return 3\n', encoding='utf-8')
    with pytest.raises(ValueError, match='reference hidden failed'):
        validator.check(task, meta)


def test_visible_tests_are_checked_separately(tmp_path):
    task, meta = fixture_task(tmp_path)
    (task / 'start/tests/test_task.py').write_text('def test_visible(): assert False\n', encoding='utf-8')
    with pytest.raises(ValueError, match='reference visible failed'):
        validator.check(task, meta)


def test_timeout_is_enforced(tmp_path, monkeypatch):
    seen = {}
    def expired(command, **kwargs):
        seen.update(kwargs)
        raise validator.subprocess.TimeoutExpired(command, kwargs['timeout'])
    monkeypatch.setattr(validator.subprocess, 'run', expired)
    with pytest.raises(validator.subprocess.TimeoutExpired):
        validator.run(tmp_path, 0.25)
    assert seen['timeout'] == 0.25
