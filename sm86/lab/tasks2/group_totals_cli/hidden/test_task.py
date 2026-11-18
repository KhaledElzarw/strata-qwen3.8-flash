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
    assert run([], 'a\t2\na\t3\nb\t1')[1] == 'a\t5\nb\t1\n'


def test_case_01():
    assert run(['--sort', 'name'], 'b\t5\na\t1')[1] == 'a\t1\nb\t5\n'


def test_case_02():
    assert run(['--top', '1'], 'a\t1\nb\t3')[1] == 'b\t3\n'


def test_case_03():
    assert run([], 'b\t2\na\t2')[1] == 'a\t2\nb\t2\n'


def test_case_04():
    assert run(['--min-total', '3'], 'a\t2\na\t2\nb\t5\nb\t-3')[1] == 'a\t4\n'


def test_case_05():
    assert run(['--min-total', '3'], 'a\t3')[1] == 'a\t3\n'
    assert run(['--top', '1', '--min-total', '0'], 'a\t-1\nb\t2')[1] == 'b\t2\n'
    assert run([], 'a\t-2\nb\t0')[1] == 'b\t0\na\t-2\n'


def test_case_06():
    for args in [['--top', '0'], ['--top', '-1'], ['--top', 'x'], ['--sort', 'bad'], ['--min-total', 'x']]:
        assert run(args)[0] == 2


def test_case_07():
    for bad in ['bad', 'a\t1\t2', '\t1', 'a\t 1', 'a\t+1']:
        assert run([], 'ok\t1\n\n' + bad) == (1, '', 'error: line 3\n')


def test_case_08():
    r = external([], 'a\t2\n')
    assert (r.returncode, r.stdout, r.stderr) == (0, 'a\t2\n', '')
    assert run([], '') == (0, '', '')
