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
    assert run(['a'], '{"a":1}\n') == (0, '1\n', '')


def test_case_01():
    assert run(['a', '--missing', 'null'], '{}\n')[1] == 'null\n'


def test_case_02():
    assert run(['a', '--where', 'b=2'], '{"a":1,"b":2}\n{"a":3,"b":1}')[1] == '1\n'


def test_case_03():
    r = run(['x'], '{"x":1}\n\nnot-json')
    assert r == (1, '', 'error: line 3\n')


def test_case_04():
    assert run(['a'], '{}')[1] == ''
    assert run(['a', '--missing', 'error'], '{}') == (1, '', 'error: line 1\n')


def test_case_05():
    assert run(['a.b'], '{"a":{"b":[1,2]}}')[1] == '[1,2]\n'
    assert run(['a'], '{"a":"é"}')[1] == '"é"\n'


def test_case_06():
    for args in [[], ['a..b'], ['a', '--where', 'bad'], ['a', '--where', 'x=no'], ['a', '--missing', 'bad']]:
        assert run(args)[0] == 2


def test_case_07():
    assert run(['x', '--where', 'v=1'], '{"x":3,"v":true}')[1] == ''
    assert run(['x', '--where', 'v=null'], '{"x":3}')[1] == ''
    assert run(['x'], '[]')[0] == 1


def test_case_08():
    r = external(['x'], '{"x":2}\n')
    assert (r.returncode, r.stdout, r.stderr) == (0, '2\n', '')
    assert run(['x'], '') == (0, '', '')
