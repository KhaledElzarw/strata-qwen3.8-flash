import re
KEY = re.compile('[A-Za-z_][A-Za-z0-9_]*')

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
                if not child or any((c.isspace() for c in child)):
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
    result, resolving = ({}, set())

    def resolve(key):
        if key in result:
            return result[key]
        if key in resolving:
            raise ValueError('reference cycle')
        text = raw[key]
        resolving.add(key)
        out, i = ([], 0)
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
