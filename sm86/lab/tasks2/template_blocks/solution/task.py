import re
NAME = re.compile('[A-Za-z_][A-Za-z0-9_]*')

def render(template, values):
    root = []
    current = root
    stack = []
    i = 0
    while i < len(template):
        if template.startswith(('}}', '%}'), i):
            raise ValueError('unexpected close')
        if template.startswith('{{', i):
            end = template.find('}}', i + 2)
            name = template[i + 2:end].strip()
            if end < 0 or not NAME.fullmatch(name):
                raise ValueError('substitution')
            current.append(('value', name))
            i = end + 2
        elif template.startswith('{%', i):
            end = template.find('%}', i + 2)
            if end < 0:
                raise ValueError('unclosed tag')
            words = template[i + 2:end].split()
            if len(words) == 2 and words[0] == 'if' and NAME.fullmatch(words[1]):
                node = ['if', words[1], [], []]
                current.append(node)
                stack.append((current, node, False))
                current = node[2]
            elif words == ['else'] and stack and (not stack[-1][2]):
                parent, node, _ = stack[-1]
                stack[-1] = (parent, node, True)
                current = node[3]
            elif words == ['end'] and stack:
                current, _, _ = stack.pop()
            else:
                raise ValueError('directive')
            i = end + 2
        else:
            current.append(('text', template[i]))
            i += 1
    if stack:
        raise ValueError('unclosed block')

    def output(nodes):
        result = []
        for node in nodes:
            if node[0] == 'text':
                result.append(node[1])
            elif node[0] == 'value':
                result.append(str(values[node[1]]))
            else:
                result.append(output(node[2] if values[node[1]] else node[3]))
        return ''.join(result)
    return output(root)
