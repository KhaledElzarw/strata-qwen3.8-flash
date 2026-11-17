from common import emit

emit('header_parameters', 'parsers', 2, 'implement', '''
# Header parameter parser
Implement `parse(text)` returning `(main, parameters)` for one header value.
The main value is the text before the first semicolon, stripped and lowercased;
it must be nonempty. Parameters are `; name = value`, with optional ASCII spaces
or tabs around punctuation. Names match `[A-Za-z][A-Za-z0-9_-]*` and are lowercased;
duplicate names are errors. An unquoted value is a nonempty run of characters
other than semicolon, quote, backslash, space or tab. Quoted values use double
quotes and can be empty; backslash quotes exactly the next character (including
semicolon or backslash). Spaces inside quotes are preserved. Reject CR/LF
anywhere, trailing semicolons, malformed parameters, dangling escapes and
unclosed quotes with ValueError. Return parameters as a dict of decoded strings.
''', r'''
import re


def parse(text):
    if '\r' in text or '\n' in text:
        raise ValueError('newline')
    parts = text.split(';', 1)
    main = parts[0].strip(' \t').lower()
    if not main:
        raise ValueError('main')
    if len(parts) == 1:
        return main, {}
    tail = parts[1]
    i, params = 0, {}
    while True:
        while i < len(tail) and tail[i] in ' \t':
            i += 1
        match = re.match(r'([A-Za-z][A-Za-z0-9_-]*)[ \t]*=[ \t]*', tail[i:])
        if not match:
            raise ValueError('parameter')
        name = match[1].lower()
        i += match.end()
        if i < len(tail) and tail[i] == '"':
            i += 1
            value = []
            while i < len(tail) and tail[i] != '"':
                if tail[i] == '\\':
                    i += 1
                    if i == len(tail):
                        raise ValueError('escape')
                value.append(tail[i])
                i += 1
            if i == len(tail):
                raise ValueError('quote')
            i += 1
            value = ''.join(value)
        else:
            match = re.match(r'[^;"\\ \t]+', tail[i:])
            if not match:
                raise ValueError('value')
            value = match[0]
            i += match.end()
        if name in params:
            raise ValueError('duplicate')
        params[name] = value
        while i < len(tail) and tail[i] in ' \t':
            i += 1
        if i == len(tail):
            return main, params
        if tail[i] != ';':
            raise ValueError('separator')
        i += 1
''', [
"assert parse(' Text/Plain ; Charset = utf-8') == ('text/plain', {'charset': 'utf-8'})",
"assert parse('X; a=\"b;c\"') == ('x', {'a': 'b;c'})",
"assert parse('A') == ('a', {})",
"assert parse('X;a=\"\";b=\" a \"') == ('x', {'a': '', 'b': ' a '})",
 r'''assert parse(r'X; a="say \"yes\""; b="c\\d"') == ('x', {'a': 'say "yes"', 'b': 'c\\d'})''',
"for s in ['X;a=1;A=2', 'X;a=', 'X;', ';a=1', 'X;1a=b']:\n    with pytest.raises(ValueError): parse(s)",
"for s in ['X;a=\"x', 'X;a=\"x\"z', 'X;a=two words']:\n    with pytest.raises(ValueError): parse(s)",
"for s in ['X\\na=1', 'X;a=\"x\\ry\"']:\n    with pytest.raises(ValueError): parse(s)",
"assert parse('X\t; Ab_C-2\t=\t123 \t') == ('x', {'ab_c-2': '123'})",
])

emit('folded_records', 'parsers', 3, 'fix', '''
# Repair folded log records
Fix `records(lines)` in `task.py`. Input is an iterable of strings without line
terminators. A header matches exactly `@DIGITS LEVEL: MESSAGE`, where DIGITS is
one or more ASCII digits, LEVEL is INFO/WARN/ERROR, and MESSAGE may be empty.
Output is a list of dicts with `seq` (integer), `level`, `message`, `tags` (list).
A line starting with one space continues the last record: remove exactly that
one space and append a newline plus the rest to its message. A line starting
`+tag ` attaches the remaining nonempty string as a tag, once per record in
first-seen order. Tags and continuations without a preceding header are errors.
A blank line or line starting `#` is ignored and does not clear the last record.
All other lines raise ValueError, including duplicate sequence numbers and
invalid headers. Records retain input order; returned objects never share tags.
''', r'''
import re


def records(lines):
    result, seen = [], set()
    for line in lines:
        if not line or line.startswith('#'):
            continue
        if line.startswith(' '):
            if not result:
                raise ValueError('orphan continuation')
            result[-1]['message'] += '\n' + line[1:]
        elif line.startswith('+tag '):
            tag = line[5:]
            if not result or not tag:
                raise ValueError('orphan or empty tag')
            if tag not in result[-1]['tags']:
                result[-1]['tags'].append(tag)
        else:
            m = re.fullmatch(r'@([0-9]+) (INFO|WARN|ERROR): (.*)', line)
            if not m or int(m[1]) in seen:
                raise ValueError('header')
            seq = int(m[1])
            seen.add(seq)
            result.append(dict(seq=seq, level=m[2], message=m[3], tags=[]))
    return result
''', [
"assert records(['@1 INFO: ok']) == [dict(seq=1, level='INFO', message='ok', tags=[])]",
"assert records(['@2 WARN: x', ' y'])[0]['message'] == 'x\\ny'",
"assert records(['@0 ERROR: ', '+tag red'])[0]['tags'] == ['red']",
"assert records(['@1 INFO: x', '  y'])[0]['message'] == 'x\\n y'",
"assert records(['@1 INFO: x', '+tag a', '+tag a', '+tag b'])[0]['tags'] == ['a', 'b']",
"r = records(['@1 INFO: a', '@2 INFO: b', '+tag b'])\nassert r[0]['tags'] == []\nassert r[1]['tags'] == ['b']",
"for lines in [[' bad'], ['+tag x'], ['@1 INFO: x', '+tag '], ['@1 INFO: x', '@01 WARN: y']]:\n    with pytest.raises(ValueError): records(lines)",
"for line in ['@1 DEBUG: x', '@x INFO: x', '@1 INFO:x', '@١ INFO: x', 'unknown']:\n    with pytest.raises(ValueError): records([line])",
"r = records(iter(['#x', '', '@3 INFO: a', '', '# gap', ' b', '@1 WARN: c']))\nassert [v['seq'] for v in r] == [3, 1]\nassert r[0]['message'] == 'a\\nb'",
], start=[('task.py', "line[1:]", "line.lstrip()"), ('task.py', "if tag not in result[-1]['tags']:", 'if True:'), ('task.py', 'int(m[1]) in seen', 'm[1] in seen')])

emit('delimited_stream', 'parsers', 3, 'extend', '''
# Streaming delimited records
Extend `Reader(separator=',')` with quoted fields across arbitrary `feed(chunk)`
boundaries. Separator is one character other than quote, CR or LF; otherwise
ValueError. `feed` returns complete records as lists of strings; `finish()`
returns the final unterminated record if there is one, then closes the reader.
Records end at LF or CRLF outside quotes; bare CR outside quotes is invalid.
CRLF may straddle chunks. Fields may be wholly double-quoted, doubled quotes
inside them mean one quote, and all characters (including CR/LF) inside quotes
are literal. A closing quote must be followed by separator, record end or EOF.
Quotes inside unquoted fields are invalid. Keep whitespace exactly. A blank
record is ['']; trailing separators give empty fields. Empty input gives no
records and a final record terminator creates no extra record. `finish` rejects
open quotes or pending bare CR. Calls after finish raise ValueError, including
empty feed and repeated finish. No recovery is required after invalid input.
''', r'''
class Reader:
    def __init__(self, separator=','):
        if len(separator) != 1 or separator in '"\r\n':
            raise ValueError('separator')
        self.sep = separator
        self.state = 'start'
        self.field = ''
        self.row = []
        self.pending = False
        self.closed = False

    def _end_field(self):
        self.row.append(self.field)
        self.field = ''
        self.state = 'start'

    def feed(self, chunk):
        if self.closed:
            raise ValueError('closed')
        out = []
        for ch in chunk:
            if self.pending:
                if ch != '\n':
                    raise ValueError('bare CR')
                self.pending = False
                continue
            if self.state == 'quoted':
                if ch == '"':
                    self.state = 'after'
                else:
                    self.field += ch
                continue
            if self.state == 'after' and ch == '"':
                self.field += '"'
                self.state = 'quoted'
                continue
            if ch == self.sep:
                self._end_field()
            elif ch in '\r\n':
                self._end_field()
                out.append(self.row)
                self.row = []
                self.pending = ch == '\r'
            elif ch == '"' and self.state == 'start':
                self.state = 'quoted'
            elif ch == '"' or self.state == 'after':
                raise ValueError('quote placement')
            else:
                self.field += ch
                self.state = 'plain'
        return out

    def finish(self):
        if self.closed:
            raise ValueError('closed')
        self.closed = True
        if self.pending or self.state == 'quoted':
            raise ValueError('incomplete record')
        if self.row or self.field or self.state == 'after':
            self._end_field()
            return [self.row]
        return []
''', [
"r = Reader()\nassert r.feed('a,b\\nc,d') == [['a', 'b']]\nassert r.finish() == [['c', 'd']]",
"r = Reader()\nassert r.feed('\"a,b\",x\\n') == [['a,b', 'x']]\nassert r.finish() == []",
"r = Reader(';')\nassert r.feed('a;;\\n') == [['a', '', '']]",
"r = Reader()\nout = []\nfor c in '\"a\"\"b\\nc\",z\\r\\n': out.extend(r.feed(c))\nout.extend(r.finish())\nassert out == [['a\"b\\nc', 'z']]",
"r = Reader()\nassert r.feed('\\n\\n') == [[''], ['']]\nassert r.finish() == []\nassert Reader().finish() == []",
"for s in ['a\"b', '\"a\"z', 'a\\rb']:\n    with pytest.raises(ValueError): Reader().feed(s)",
"for s in ['\"open', 'a\\r']:\n    r = Reader()\n    r.feed(s)\n    with pytest.raises(ValueError): r.finish()",
"r = Reader()\nassert r.feed('\"\"') == []\nassert r.finish() == [['']]\nwith pytest.raises(ValueError): r.feed('')\nwith pytest.raises(ValueError): r.finish()",
"for sep in ['', 'xx', '\\n', '\\r', '\"']:\n    with pytest.raises(ValueError): Reader(sep)\nr = Reader()\nassert r.feed(' a ,\"b\\rc\"') == []\nassert r.finish() == [[' a ', 'b\\rc']]",
], start=[('task.py', "self.state = 'quoted'\n            elif ch", "raise ValueError('quoted fields not supported yet')\n            elif ch")])

emit('include_config', 'parsers', 4, 'implement', '''
# Configuration includes and deferred references
Implement `load(files, entry)` in `task.py`; files maps names to text, with no
filesystem access. Each stripped nonblank line is either `#` comment, `@include NAME`
(NAME is a nonempty string without whitespace), or `KEY = VALUE`. KEY matches
`[A-Za-z_][A-Za-z0-9_]*`. VALUE is stripped text, possibly empty; # inside a value
is literal. Includes expand at their position; later definitions overwrite earlier
ones globally, including across files. Missing files raise KeyError. An include
cycle raises ValueError, but including the same file again off the active stack
is allowed. Validate every expanded line even if a later line overwrites it.
After all definitions are collected, expand `${KEY}` references against FINAL
values, recursively. Forward references work. Missing referenced keys raise
KeyError; reference cycles raise ValueError. `$$` emits a literal dollar and
prevents that dollar from starting a reference. Other dollars are literal unless
followed by `{`; malformed `${...}` raises ValueError (key grammar as above).
Return a new dict of strings; do not modify files. Only surviving final values
are expanded. Implement both include and reference cycle detection.
''', r'''
import re

KEY = re.compile(r'[A-Za-z_][A-Za-z0-9_]*')


def load(files, entry):
    raw = {}
    active = set()

    def visit(name):
        if name in active:
            raise ValueError('include cycle')
        text = files[name]
        active.add(name)
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('@include '):
                child = line[9:].strip()
                if not child or any(c.isspace() for c in child):
                    raise ValueError('include name')
                visit(child)
            else:
                key, sep, value = line.partition('=')
                key = key.strip()
                if not sep or not KEY.fullmatch(key):
                    raise ValueError('assignment')
                raw[key] = value.strip()
        active.remove(name)

    visit(entry)
    result, resolving = {}, set()

    def resolve(key):
        if key in result:
            return result[key]
        if key in resolving:
            raise ValueError('reference cycle')
        text = raw[key]
        resolving.add(key)
        out, i = [], 0
        while i < len(text):
            if text.startswith('$$', i):
                out.append('$')
                i += 2
            elif text.startswith('${', i):
                end = text.find('}', i + 2)
                name = text[i + 2:end]
                if end < 0 or not KEY.fullmatch(name):
                    raise ValueError('reference')
                out.append(resolve(name))
                i = end + 1
            else:
                out.append(text[i])
                i += 1
        resolving.remove(key)
        result[key] = ''.join(out)
        return result[key]

    for key in raw:
        resolve(key)
    return result
''', [
"assert load({'a': 'x=1\\ny= ${x}/2'}, 'a') == {'x': '1', 'y': '1/2'}",
"assert load({'a': 'x=old\\n@include b\\nx=new', 'b': 'y=${x}'}, 'a') == {'x': 'new', 'y': 'new'}",
"assert load({'a': '# comment\\nx =  # literal'}, 'a') == {'x': '# literal'}",
"assert load({'a': 'x=$${missing} $$ $z'}, 'a') == {'x': '${missing} $ $z'}",
"for files in [{'a': '@include b', 'b': '@include a'}, {'a': 'x=${y}\\ny=${x}'}]:\n    with pytest.raises(ValueError): load(files, 'a')",
"with pytest.raises(KeyError): load({'a': '@include missing'}, 'a')\nwith pytest.raises(KeyError): load({'a': 'x=${missing}'}, 'a')",
"for text in ['bad', '1x=ok', 'x=${}', 'x=${a', '@include b c', 'x=${bad-key}']:\n    with pytest.raises(ValueError): load({'a': text}, 'a')",
"f = {'a': '@include b\\nx=changed\\n@include b', 'b': 'x=base\\ny=${x}'}\nold = deepcopy(f)\nassert load(f, 'a') == {'x': 'base', 'y': 'base'}\nassert f == old",
"assert load({'a': 'x=${absent}\\nx=\\ny=${z}\\nz=done'}, 'a') == {'x': '', 'y': 'done', 'z': 'done'}\nwith pytest.raises(ValueError): load({'a': 'bad\\nx=ok'}, 'a')",
])

