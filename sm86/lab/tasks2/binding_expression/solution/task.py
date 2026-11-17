import re

def evaluate(text, variables=None):
    variables = {} if variables is None else variables
    tokens = []
    i = 0
    while i < len(text):
        if text[i].isspace():
            i += 1
            continue
        m = re.match('[0-9]+|[A-Za-z_][A-Za-z0-9_]*|//|[()+*%\\-]', text[i:])
        if not m:
            raise ValueError('token')
        tokens.append(m[0])
        i += m.end()
    position = 0

    def atom():
        nonlocal position
        if position == len(tokens):
            raise ValueError('operand')
        token = tokens[position]
        position += 1
        if token in ('+', '-'):
            value = atom()
            return value if token == '+' else -value
        if token == '(':
            value = expr(0)
            if position == len(tokens) or tokens[position] != ')':
                raise ValueError('parenthesis')
            position += 1
            return value
        if token[0].isdigit():
            return int(token)
        if re.fullmatch('[A-Za-z_][A-Za-z0-9_]*', token):
            return variables[token]
        raise ValueError('operand')

    def expr(level):
        nonlocal position
        if level == 2:
            return atom()
        value = expr(level + 1)
        ops = ('+', '-') if level == 0 else ('*', '//', '%')
        while position < len(tokens) and tokens[position] in ops:
            op = tokens[position]
            position += 1
            right = expr(level + 1)
            if op == '+':
                value += right
            elif op == '-':
                value -= right
            elif op == '*':
                value *= right
            elif op == '//':
                value //= right
            else:
                value %= right
        return value
    answer = expr(0)
    if position != len(tokens):
        raise ValueError('trailing input')
    return answer
