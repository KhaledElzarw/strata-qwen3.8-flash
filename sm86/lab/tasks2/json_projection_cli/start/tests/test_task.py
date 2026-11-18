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
