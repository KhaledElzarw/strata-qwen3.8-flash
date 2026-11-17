import re

def parse(text):
    if '\r' in text or '\n' in text:
        raise ValueError('newline')
    parts = text.split(';', 1)
    main = parts[0].strip(' \t').lower()
    if not main:
        raise ValueError('main')
    if len(parts) == 1:
        return (main, {})
    tail = parts[1]
    i, params = (0, {})
    while True:
        while i < len(tail) and tail[i] in ' \t':
            i += 1
        match = re.match('([A-Za-z][A-Za-z0-9_-]*)[ \\t]*=[ \\t]*', tail[i:])
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
            match = re.match('[^;"\\\\ \\t]+', tail[i:])
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
            return (main, params)
        if tail[i] != ';':
            raise ValueError('separator')
        i += 1

def format_header(main, parameters):
    main = main.strip(' \t').lower()
    if not main or any((ch in main for ch in ';\r\n')):
        raise ValueError('main')
    normalized = {}
    for name, value in parameters.items():
        if not re.fullmatch('[A-Za-z][A-Za-z0-9_-]*', name):
            raise ValueError('name')
        name = name.lower()
        if name in normalized or '\r' in value or '\n' in value:
            raise ValueError('duplicate or newline')
        normalized[name] = value
    fields = [main]
    for name, value in sorted(normalized.items()):
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        fields.append(name + '="' + escaped + '"')
    return '; '.join(fields)
