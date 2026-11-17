import re

class Machine:

    def __init__(self):
        self.stack = []
        self.variables = {}

    def run(self, tokens):
        stack = list(self.stack)
        variables = dict(self.variables)

        def pop():
            if not stack:
                raise ValueError('underflow')
            return stack.pop()
        for token in tokens:
            if re.fullmatch('-?[0-9]+', token):
                stack.append(int(token))
            elif token in ('+', '-', '*', '/'):
                right, left = (pop(), pop())
                if token == '+':
                    value = left + right
                elif token == '-':
                    value = left - right
                elif token == '*':
                    value = left * right
                else:
                    if right == 0:
                        raise ZeroDivisionError()
                    value = abs(left) // abs(right)
                    if (left < 0) != (right < 0):
                        value = -value
                stack.append(value)
            elif token == 'dup':
                value = pop()
                stack.extend([value, value])
            elif token == 'swap':
                right, left = (pop(), pop())
                stack.extend([right, left])
            elif token == 'drop':
                pop()
            elif re.fullmatch('[$=][A-Za-z_][A-Za-z0-9_]*', token):
                if token[0] == '$':
                    stack.append(variables[token[1:]])
                else:
                    variables[token[1:]] = pop()
            else:
                raise ValueError('token')
        self.stack = stack
        self.variables = variables
        return list(stack)
