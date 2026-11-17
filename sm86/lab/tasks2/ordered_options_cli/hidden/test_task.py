import pytest
from copy import deepcopy
import io
import json
import subprocess
import sys
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr
from task import main


def run(args, text=''):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = main(args, io.StringIO(text))
        except SystemExit as exc:
            code = exc.code
    return code, out.getvalue(), err.getvalue()


def external(args, text=''):
    tool = Path(__file__).resolve().parents[1] / 'task.py'
    result = subprocess.run([sys.executable, str(tool), *args], input=text.encode('utf-8'),
                            capture_output=True, timeout=3)
    result.stdout = result.stdout.decode('utf-8').replace(chr(13) + chr(10), chr(10))
    result.stderr = result.stderr.decode('utf-8').replace(chr(13) + chr(10), chr(10))
    return result


def test_case_00():
    assert run(['--set', 'x=1'])[1] == '{"x":1}\n'


def test_case_01():
    assert run(['--unset', 'x'], '{"x":1}')[1] == '{}\n'


def test_case_02():
    assert run(['--append', 'x=1', '--append', 'x=2'])[1] == '{"x":[1,2]}\n'


def test_case_03():
    args = ['--set', 'x=[]', '--append', 'x=1', '--unset', 'x', '--append', 'x=2']
    assert run(args)[1] == '{"x":[2]}\n'


def test_case_04():
    assert run(['--append', 'a.b=[1,2]'])[1] == '{"a":{"b":[[1,2]]}}\n'
    assert run(['--unset', 'missing.path'])[1] == '{}\n'


def test_case_05():
    for args in [['--set', 'a..b=1'], ['--set', 'x=no'], ['--unset', 'x=1'], ['--append'], ['--bad']]:
        assert run(args)[0] == 2


def test_case_06():
    for args, text in [([], '[]'), ([], 'bad'), (['--set', 'x.y=1'], '{"x":2}'), (['--append', 'x=1'], '{"x":2}'), (['--unset', 'x.y'], '{"x":2}')]:
        assert run(args, text) == (1, '', 'error: data\n')


def test_case_07():
    assert run(['--pretty'], '{"b":2,"a":1}')[1] == '{\n  "a": 1,\n  "b": 2\n}\n'
    assert run([], '{"é":1}')[1] == '{"é":1}\n'


def test_case_08():
    r = external(['--set', 'x=3'])
    assert (r.returncode, r.stdout, r.stderr) == (0, '{"x":3}\n', '')
    assert run([], '  ')[1] == '{}\n'
