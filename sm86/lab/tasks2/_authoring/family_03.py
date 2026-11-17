from common import emit

emit('binding_expression', 'expressions', 2, 'implement', '''
# Integer expressions with bindings
Implement `evaluate(text, variables=None)`. Grammar has ASCII nonnegative integer
literals, identifiers `[A-Za-z_][A-Za-z0-9_]*`, parentheses, binary + - * // %,
and unary + -. Whitespace is ignored between tokens, never inside a token.
Unary signs bind tighter than multiplication; multiplication, floor division and
modulo bind tighter than addition/subtraction. Binary operators associate left.
Variables maps identifiers to integers; missing names raise KeyError. Python
integer // and % rules apply, including negative operands; zero divisors raise
ZeroDivisionError. Reject empty input, unknown characters, adjacent operands,
unmatched parentheses and trailing tokens with ValueError. Consume all input;
do not use eval or exec. Do not modify variables.
''', r'''
import re


def evaluate(text, variables=None):
    variables = {} if variables is None else variables
    tokens = []
    i = 0
    while i < len(text):
        if text[i].isspace():
            i += 1
            continue
        m = re.match(r'[0-9]+|[A-Za-z_][A-Za-z0-9_]*|//|[()+*%\-]', text[i:])
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
        if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', token):
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
            if op == '+': value += right
            elif op == '-': value -= right
            elif op == '*': value *= right
            elif op == '//': value //= right
            else: value %= right
        return value

    answer = expr(0)
    if position != len(tokens):
        raise ValueError('trailing input')
    return answer
''', [
"assert evaluate('2 + 3 * 4') == 14",
"assert evaluate('-(x + 2)', {'x': 3}) == -5",
"assert evaluate('20 // 3 % 4') == 2",
"assert evaluate('10-3-2') == 5\nassert evaluate('--2 * -3') == -6",
"assert evaluate('-7//3') == -3\nassert evaluate('-7%3') == 2",
"for s in ['', '1 2', '(1', '1)', '1/', '2**3', '()', 'a.b']:\n    with pytest.raises(ValueError): evaluate(s)",
"with pytest.raises(KeyError): evaluate('absent')\nwith pytest.raises(ZeroDivisionError): evaluate('1//0')\nwith pytest.raises(ZeroDivisionError): evaluate('1%0')",
"v = {'_a1': 7}\nassert evaluate(' + _a1 * (2 + 1) ', v) == 21\nassert v == {'_a1': 7}",
"assert evaluate('1+-2*-3') == 7\nassert evaluate('100//5//2') == 10\nassert evaluate('9%4*3') == 3",
])

emit('postfix_machine', 'expressions', 3, 'fix', '''
# Repair the transactional postfix machine
Fix `Machine` with `stack` (list of integers) and `variables` (dict). `run(tokens)`
accepts an iterable of strings and returns a fresh copy of the final stack.
Integer tokens match `-?[0-9]+`; `+ - * /` pop right then left (/ truncates toward
zero without float conversion). `dup` duplicates the top; `swap` swaps top two;
`drop` removes top. `$name` pushes a variable and `=name` pops into a variable;
name matches `[A-Za-z_][A-Za-z0-9_]*`. Missing variables raise KeyError. Stack
underflow or bad tokens raise ValueError; zero divisor raises ZeroDivisionError.
A failed run rolls back BOTH stack and variables to their pre-call contents.
Success commits them, and independent Machine instances share nothing. Inputs
are never modified. No arithmetic size limit is imposed on Python integers.
''', r'''
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
            if re.fullmatch(r'-?[0-9]+', token):
                stack.append(int(token))
            elif token in ('+', '-', '*', '/'):
                right, left = pop(), pop()
                if token == '+': value = left + right
                elif token == '-': value = left - right
                elif token == '*': value = left * right
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
                right, left = pop(), pop()
                stack.extend([right, left])
            elif token == 'drop':
                pop()
            elif re.fullmatch(r'[$=][A-Za-z_][A-Za-z0-9_]*', token):
                if token[0] == '$':
                    stack.append(variables[token[1:]])
                else:
                    variables[token[1:]] = pop()
            else:
                raise ValueError('token')
        self.stack = stack
        self.variables = variables
        return list(stack)
''', [
"assert Machine().run(['8', '3', '-']) == [5]",
"m = Machine()\nassert m.run(['4', '=x', '$x', 'dup', '*']) == [16]",
"assert Machine().run(['1', '2', 'swap', 'drop']) == [2]",
"assert Machine().run(['-7', '3', '/']) == [-2]",
"m = Machine()\nm.run(['9', '=x', '5'])\nwith pytest.raises(ValueError): m.run(['2', '=x', 'drop', 'drop'])\nassert m.stack == [5] and m.variables == {'x': 9}",
"for tokens in [['$missing'], ['=bad-name'], ['wat'], ['dup'], ['swap'], ['1', '0', '/']]:\n    m = Machine()\n    with pytest.raises((ValueError, KeyError, ZeroDivisionError)): m.run(tokens)\n    assert m.stack == [] and m.variables == {}",
"n = 10**100\nassert Machine().run([str(n), '3', '/']) == [n//3]",
"m = Machine()\na = m.run(['1'])\na.append(2)\nassert m.stack == [1]\nassert Machine().stack == []",
"m = Machine()\ntokens = ['3', '=a', '$a', '2', '+']\nassert m.run(iter(tokens)) == [5]\nassert tokens[-1] == '+'\nassert m.run(['-2', '*']) == [-10]",
], start=[('task.py', 'stack = list(self.stack)', 'stack = self.stack'), ('task.py', 'variables = dict(self.variables)', 'variables = self.variables'), ('task.py', 'value = abs(left) // abs(right)', 'value = left // right')])

emit('lazy_formula', 'expressions', 4, 'extend', '''
# Lazy formula evaluation
Extend `evaluate(node, env)` in `task.py`. Nodes are integers, strings (variable
names), or tuples `(operator, ...)`. Existing eager binary add/sub/mul/eq/lt
return integers (comparisons return 0 or 1). Add lazy `if(cond, yes, no)`,
`and(left, right)`, `or(left, right)`, and `let(name, value, body)`. For and/or,
return 0 or 1 using integer truth; skip the right branch when determined.
For if evaluate only the chosen branch. let evaluates value in the outer scope,
then body with a shadowing local binding; outer env must stay unchanged.
Missing names raise KeyError. Unknown operators, wrong arities, noninteger
nonstring nontuple nodes and nonstring let names raise ValueError when visited.
Booleans are invalid nodes even though Python treats them as ints. Validation
is lazy too: unreachable invalid nodes or missing names must not fail. Tuples
must be nonempty with a string operator. No mutation of nodes or env.
''', '''
def evaluate(node, env):
    if type(node) is int:
        return node
    if isinstance(node, str):
        return env[node]
    if not isinstance(node, tuple) or not node or not isinstance(node[0], str):
        raise ValueError('node')
    op, *args = node
    sizes = {'add': 2, 'sub': 2, 'mul': 2, 'eq': 2, 'lt': 2,
             'if': 3, 'and': 2, 'or': 2, 'let': 3}
    if op not in sizes or len(args) != sizes[op]:
        raise ValueError('operator or arity')
    if op == 'if':
        cond = evaluate(args[0], env)
        return evaluate(args[1] if cond else args[2], env)
    if op == 'and':
        return int(bool(evaluate(args[0], env)) and bool(evaluate(args[1], env)))
    if op == 'or':
        return int(bool(evaluate(args[0], env)) or bool(evaluate(args[1], env)))
    if op == 'let':
        name, value, body = args
        if not isinstance(name, str):
            raise ValueError('binding name')
        local = dict(env)
        local[name] = evaluate(value, env)
        return evaluate(body, local)
    left, right = (evaluate(arg, env) for arg in args)
    if op == 'add': return left + right
    if op == 'sub': return left - right
    if op == 'mul': return left * right
    if op == 'eq': return int(left == right)
    return int(left < right)
''', [
"assert evaluate(('add', 2, ('mul', 3, 4)), {}) == 14",
"assert evaluate(('if', 0, 'missing', 7), {}) == 7",
"assert evaluate(('let', 'x', 3, ('add', 'x', 1)), {'x': 9}) == 4",
"assert evaluate(('and', 0, ('bad',)), {}) == 0\nassert evaluate(('or', 2, None), {}) == 1",
"assert evaluate(('and', -2, 3), {}) == 1\nassert evaluate(('or', 0, 0), {}) == 0",
"env = {'x': 4}\nn = ('let', 'x', ('add', 'x', 1), ('let', 'x', ('mul', 'x', 2), 'x'))\nassert evaluate(n, env) == 10\nassert env == {'x': 4}",
"for n in [True, [], (), ('add', 1), ('bad', 1), ('let', 1, 2, 3), (1, 2)]:\n    with pytest.raises(ValueError): evaluate(n, {})",
"with pytest.raises(KeyError): evaluate(('and', 1, 'missing'), {})\nwith pytest.raises(KeyError): evaluate(('let', 'x', 'x', 1), {})",
"assert evaluate(('if', ('eq', 2, 2), ('lt', 1, 3), ('bad',)), {}) == 1\nassert evaluate(('sub', 9, 4), {}) == 5",
], start=[('task.py', "if op == 'if':", "if op in ('if', 'and', 'or', 'let'):\n        raise ValueError('extension operator')\n    if op == 'if':")])

emit('template_blocks', 'expressions', 4, 'implement', '''
# Nested conditional templates
Implement `render(template, values)` in `task.py`. Literal text is copied.
`{{name}}` inserts `str(values[name])`; name is stripped and matches
`[A-Za-z_][A-Za-z0-9_]*`. Blocks are `{% if name %}...{% else %}...{% end %}`;
else is optional. Nesting is allowed. Choose with bool(values[name]); only
chosen branch substitutions and conditions are evaluated. Missing evaluated
names raise KeyError. All template syntax, including unchosen branches, must be
validated: unmatched braces/tags, duplicate else, unknown directives and invalid
names raise ValueError. A literal `{` is allowed unless followed by `{` or `%`;
unmatched `}}` or `%}` is invalid. Tags allow arbitrary whitespace around their
words but no expressions. Empty templates and empty branches work. Do not modify
values. Do not use eval or exec. Syntax errors take precedence over missing names.
''', r'''
import re

NAME = re.compile(r'[A-Za-z_][A-Za-z0-9_]*')


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
            elif words == ['else'] and stack and not stack[-1][2]:
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
            if node[0] == 'text': result.append(node[1])
            elif node[0] == 'value': result.append(str(values[node[1]]))
            else: result.append(output(node[2] if values[node[1]] else node[3]))
        return ''.join(result)
    return output(root)
''', [
"assert render('hello {{ who }}!', {'who': 'Ada'}) == 'hello Ada!'",
"assert render('{% if ok %}yes{% else %}no{% end %}', {'ok': 0}) == 'no'",
"assert render('', {}) == ''\nassert render('a { b', {}) == 'a { b'",
"s = '{% if a %}A{% if b %}B{% else %}C{% end %}{% else %}D{% end %}'\nassert render(s, {'a': 1, 'b': 0}) == 'AC'",
"assert render('{% if x %}{{missing}}{% if absent %}bad{% end %}{% end %}', {'x': 0}) == ''",
"for s in ['{{x', '{{}}', '{% if x %}', '{% else %}', '{% what %}', 'x}}', '%}', '{% if x %}{% else %}{% else %}{% end %}']:\n    with pytest.raises(ValueError): render(s, {'x': 0})",
"with pytest.raises(ValueError): render('{{missing}}{% bad %}', {})\nwith pytest.raises(ValueError): render('{% if x %}ok{% else %}{{a.b}}{% end %}', {'x': 1})",
"with pytest.raises(KeyError): render('{{x}}', {})\nwith pytest.raises(KeyError): render('{% if x %}a{% end %}', {})",
"v = {'x': [], 'n': None}\nassert render('{%  if   x  %}a{%else%}{{n}}{%end%}', v) == 'None'\nassert v == {'x': [], 'n': None}",
])
