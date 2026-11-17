import re

def _escape(text):
    return text.replace('\\', '\\\\').replace('\t', '\\t').replace('\n', '\\n').replace('\r', '\\r')

def _unescape(text):
    out, i = ([], 0)
    escapes = {'\\': '\\', 't': '\t', 'n': '\n', 'r': '\r'}
    while i < len(text):
        ch = text[i]
        if ch == '\\':
            i += 1
            if i == len(text) or text[i] not in escapes:
                raise ValueError('escape')
            ch = escapes[text[i]]
        out.append(ch)
        i += 1
    return ''.join(out)

class Codec:

    def __init__(self, schema):
        self.schema = tuple(schema)
        if any((t not in ('str', 'int', 'bool', 'nullable') for t in self.schema)):
            raise ValueError('schema')

    def _types(self, row):
        if self.schema and len(row) != len(self.schema):
            raise ValueError('width')
        return self.schema or ('str',) * len(row)

    def encode(self, rows):
        result = []
        for row in rows:
            fields = []
            for value, kind in zip(row, self._types(row)):
                if kind == 'nullable' and value is None:
                    fields.append('\\N')
                    continue
                if kind == 'int' and type(value) is int:
                    fields.append(str(value))
                    continue
                if kind == 'bool' and type(value) is bool:
                    fields.append(str(value).lower())
                    continue
                if kind in ('str', 'nullable') and isinstance(value, str):
                    fields.append(_escape(value))
                    continue
                raise ValueError('field')
            result.append('\t'.join(fields))
        return '\n'.join(result)

    def decode(self, text):
        result = []
        for line in text.split('\n') if text else []:
            row, fields = ([], line.split('\t'))
            for field, kind in zip(fields, self._types(fields)):
                if kind == 'nullable' and field == '\\N':
                    row.append(None)
                    continue
                value = _unescape(field)
                if kind == 'int':
                    if not re.fullmatch('0|-?[1-9][0-9]*', value):
                        raise ValueError('integer')
                    value = int(value)
                elif kind == 'bool':
                    if value not in ('true', 'false'):
                        raise ValueError('boolean')
                    value = value == 'true'
                row.append(value)
            result.append(row)
        return result
default_codec = Codec(())

def encode(rows):
    return default_codec.encode(rows)

def decode(text):
    return default_codec.decode(text)
