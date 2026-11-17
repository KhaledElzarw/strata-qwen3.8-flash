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
    assert run(['2-3'], 'a\nb\nc\nd')[1] == 'b\nc\n'


def test_case_01():
    assert run(['1,3', '--invert'], 'a\nb\nc')[1] == 'b\n'


def test_case_02():
    assert run(['1-', '--number'], 'a\nb')[1] == '1:a\n2:b\n'


def test_case_03():
    assert run(['3,1-2,2-4'], 'a\nb\nc\nd')[1] == 'a\nb\nc\nd\n'


def test_case_04():
    assert run(['--', '-2'], 'a\nb\nc')[1] == 'a\nb\n'
    assert run(['5-'], 'a\nb')[1] == ''


def test_case_05():
    assert run(['1-', '--unique', '--number'], 'a\nb\na\nb\nc')[1] == '1:a\n2:b\n5:c\n'


def test_case_06():
    assert run(['1', '--invert', '--unique', '--number'], 'a\na\nb\na')[1] == '2:a\n3:b\n'


def test_case_07():
    for s in ['', '0', '01', '3-2', '-', '1,,2', ' 1', '1-2-3']:
        assert run(['--', s])[0] == 2
    assert run(['1'], '') == (0, '', '')


def test_case_08():
    r = external(['1-', '--number'], 'a\r\n\r\nb')
    assert (r.returncode, r.stdout, r.stderr) == (0, '1:a\n2:\n3:b\n', '')
    assert run(['1-'], '\n')[1] == '\n'
