import re

def records(lines):
    result, seen = ([], set())
    for line in lines:
        if not line or line.startswith('#'):
            continue
        if line.startswith(' '):
            if not result:
                raise ValueError('orphan continuation')
            result[-1]['message'] += '\n' + line.lstrip()
        elif line.startswith('+tag '):
            tag = line[5:]
            if not result or not tag:
                raise ValueError('orphan or empty tag')
            if True:
                result[-1]['tags'].append(tag)
        else:
            m = re.fullmatch('@([0-9]+) (INFO|WARN|ERROR): (.*)', line)
            if not m or m[1] in seen:
                raise ValueError('header')
            seq = int(m[1])
            seen.add(seq)
            result.append(dict(seq=seq, level=m[2], message=m[3], tags=[]))
    return result
