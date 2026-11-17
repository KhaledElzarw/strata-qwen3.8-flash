from common import emit

emit('bounded_apportion', 'numeric', 2, 'implement', '''
# Capped proportional allocation
Implement `allocate(total, weights, caps=None)` returning dict name -> integer
allocation. total is nonnegative integer; weights maps string names to positive
integer weights. caps optionally maps names to nonnegative integer upper bounds;
unspecified caps mean total. Unknown cap keys or insufficient aggregate capacity
raise ValueError; bool/noninteger/invalid total, weight or cap also raise ValueError.
For nonzero total and no names raise ValueError; zero total returns all zeros.
Algorithm: repeatedly compute exact weighted quotas of REMAINING units over
remaining names. Simultaneously fix every name whose quota >= its remaining cap
to that cap, remove them, and recompute. Once no cap binds, floor all quotas then
give the remaining units to largest fractional remainders, ties lexical name.
Use integer/rational arithmetic, never floats. Return all names, including zeros.
Inputs are unchanged and input dictionary insertion order must not affect ties.
''', '''
from fractions import Fraction


def _integer(value, minimum):
    if type(value) is not int or value < minimum:
        raise ValueError('integer bound')


def allocate(total, weights, caps=None):
    _integer(total, 0)
    caps = {} if caps is None else dict(caps)
    if caps.keys() - weights.keys():
        raise ValueError('unknown cap')
    for weight in weights.values():
        _integer(weight, 1)
    for cap in caps.values():
        _integer(cap, 0)
    limits = {name: caps.get(name, total) for name in weights}
    if sum(limits.values()) < total:
        raise ValueError('capacity')
    result = dict.fromkeys(weights, 0)
    active = set(weights)
    remaining = total
    while remaining and active:
        denominator = sum(weights[name] for name in active)
        quota = {name: Fraction(remaining * weights[name], denominator) for name in active}
        bound = [name for name in active if quota[name] >= limits[name]]
        if bound:
            for name in bound:
                result[name] = limits[name]
                remaining -= limits[name]
                active.remove(name)
            continue
        for name in active:
            result[name] = quota[name].numerator // quota[name].denominator
        extras = remaining - sum(result[name] for name in active)
        order = sorted(active, key=lambda name: (-(quota[name] - result[name]), name))
        for name in order[:extras]:
            result[name] += 1
        remaining = 0
    return result
''', [
"assert allocate(5, {'a': 1, 'b': 1}) == {'a': 3, 'b': 2}",
"assert allocate(10, {'a': 9, 'b': 1}, {'a': 2}) == {'a': 2, 'b': 8}",
"assert allocate(0, {'a': 1}) == {'a': 0}\nassert allocate(0, {}) == {}",
"assert allocate(9, {'a': 8, 'b': 1, 'c': 1}, {'a': 2, 'b': 2}) == {'a': 2, 'b': 2, 'c': 5}",
"assert allocate(2, {'c': 1, 'b': 1, 'a': 1}) == {'a': 1, 'b': 1, 'c': 0}",
"assert allocate(2, {'a': 1, 'b': 1}, {'a': 0}) == {'a': 0, 'b': 2}\nwith pytest.raises(ValueError): allocate(3, {'a': 1}, {'a': 2})",
"for total, w, caps in [(True, {'a': 1}, {}), (1, {'a': 0}, {}), (1, {'a': 1}, {'x': 1}), (1, {}, {}), (1, {'a': 1}, {'a': -1})]:\n    with pytest.raises(ValueError): allocate(total, w, caps)",
"n = 10**30\nassert allocate(3, {'b': n, 'a': n+1}) == {'a': 2, 'b': 1}",
"w, c = {'a': 2, 'b': 1}, {'a': 3}\nold = deepcopy((w, c))\nassert allocate(5, w, c) == {'a': 3, 'b': 2}\nassert (w, c) == old",
])

emit('decimal_display', 'numeric', 2, 'fix', '''
# Repair decimal display rules
Fix `format_number(text, places=2, mode='even', grouping=False)` for finite
Decimal-compatible strings. places is an integer 0..12, bool invalid; mode is
'even' (half to even), 'away' (half away from zero), or 'zero' (truncate toward
zero). Invalid values raise ValueError. Round exactly using Decimal independent
of caller precision/rounding; tested inputs have <= 50 significant digits and
absolute exponent <= 100. Always print fixed point with exactly places digits.
Normalize any rounded negative zero to positive zero. grouping inserts commas
every three INTEGER digits only. No leading '+'; preserve negative sign for
nonzero results. `parse_display(text)` accepts only this grouped or ungrouped
fixed-point output syntax: optional '-', integer 0 or nonzero-leading digits,
optional '.' with one or more digits; grouped integer must have first group
1..3 digits with no leading zero then groups of exactly three. Reject commas
in fractional part, spaces, exponent form, plus signs and negative zero.
Return Decimal; parse_display also works on unrounded fixed point strings.
''', r'''
from decimal import Decimal, InvalidOperation, localcontext, ROUND_HALF_EVEN, ROUND_HALF_UP, ROUND_DOWN
import re


def format_number(text, places=2, mode='even', grouping=False):
    modes = {'even': ROUND_HALF_EVEN, 'away': ROUND_HALF_UP, 'zero': ROUND_DOWN}
    if type(places) is not int or not 0 <= places <= 12 or mode not in modes:
        raise ValueError('format option')
    try:
        value = Decimal(text)
    except (ValueError, TypeError, InvalidOperation):
        raise ValueError('number') from None
    if not value.is_finite(): raise ValueError('finite')
    with localcontext() as ctx:
        ctx.prec = 250
        value = value.quantize(Decimal(1).scaleb(-places), rounding=modes[mode])
        if not value: value = abs(value)
        return format(value, (',' if grouping else '') + f'.{places}f')


def parse_display(text):
    integer = r'(?:0|[1-9][0-9]*|[1-9][0-9]{0,2}(?:,[0-9]{3})+)'
    if not re.fullmatch(r'-?' + integer + r'(?:\.[0-9]+)?', text):
        raise ValueError('syntax')
    value = Decimal(text.replace(',', ''))
    if value == 0 and text.startswith('-'): raise ValueError('negative zero')
    return value
''', [
"assert format_number('1234.567', grouping=True) == '1,234.57'",
"assert format_number('2.345') == '2.34'\nassert format_number('2.345', mode='away') == '2.35'",
"assert parse_display('1,234.50') == parse_display('1234.50')\nassert parse_display('1,234,567.50') == parse_display('1234567.50')",
"assert format_number('-0.004') == '0.00'\nassert format_number('-2.345', mode='away') == '-2.35'",
"assert format_number('-2.999', 0, 'zero') == '-2'\nassert format_number('999.999', 2, grouping=True) == '1,000.00'",
"for text in ['01', '1,23', '0,000', '+1', ' 1', '1e2', '-0.00', '1.2,3', '1.']:\n    with pytest.raises(ValueError): parse_display(text)",
"for text, places, mode in [('NaN', 2, 'even'), ('Infinity', 2, 'even'), ('x', 2, 'even'), ('1', True, 'even'), ('1', 13, 'even'), ('1', 2, 'up')]:\n    with pytest.raises(ValueError): format_number(text, places, mode)",
"from decimal import localcontext\nwith localcontext() as ctx:\n    ctx.prec = 3\n    assert format_number('1234567890.125', 2) == '1234567890.12'",
"assert format_number('1e-20', 12) == '0.000000000000'\nassert format_number('1e20', 0, grouping=True) == '100,000,000,000,000,000,000'\nassert str(parse_display('-123.450')) == '-123.450'",
], start=[('task.py', "if not value: value = abs(value)", 'if False: value = abs(value)'), ('task.py', "rounding=modes[mode]", 'rounding=ROUND_HALF_UP'), ('task.py', "text.replace(',', '')", 'text.replace(",", "", 1)')])

emit('unit_quantities', 'numeric', 3, 'extend', '''
# Exact unit quantities and compound input
Extend `parse(text)` returning Fraction bytes. Existing grammar is one decimal
number with a unit. Add a sum of signed terms separated by '+' or '-' (unary sign
allowed only on first term). Each term is a nonnegative decimal with at least
one digit on both sides of an optional decimal point, then optional whitespace,
then case-sensitive unit B/KB/MB/GB (powers 1000) or KiB/MiB/GiB (powers 1024).
Whitespace allowed around terms/operators. Empty, exponent notation, unknown
units, missing units, adjacent terms and repeated signs raise ValueError.
Add `format_bytes(value, unit='B', places=2)` where value is Fraction or int
(bool invalid), unit from same set, places integer 0..6 (bool invalid). Round
exactly half away from zero, fixed point places, append single space and unit;
negative rounded zero displays positive zero. Invalid inputs raise ValueError.
Do not use binary float or ambient Decimal context. Parsing may return negative
or fractional bytes. Existing single-term parsing stays exact.
''', r'''
from fractions import Fraction
import re

UNITS = {'B': 1, 'KB': 1000, 'MB': 1000**2, 'GB': 1000**3,
         'KiB': 1024, 'MiB': 1024**2, 'GiB': 1024**3}


def parse(text):
    i, total, first = 0, Fraction(0), True
    while True:
        while i < len(text) and text[i].isspace(): i += 1
        if i == len(text):
            if first: raise ValueError('empty')
            return total
        sign = 1
        if text[i] in '+-':
            sign = -1 if text[i] == '-' else 1
            i += 1
            while i < len(text) and text[i].isspace(): i += 1
        elif not first:
            raise ValueError('operator')
        m = re.match(r'([0-9]+(?:\.[0-9]+)?)\s*([A-Za-z]+)', text[i:])
        if not m or m[2] not in UNITS: raise ValueError('term')
        total += sign * Fraction(m[1]) * UNITS[m[2]]
        i += m.end()
        first = False


def format_bytes(value, unit='B', places=2):
    if (type(value) is not int and not isinstance(value, Fraction)) or type(value) is bool:
        raise ValueError('value')
    if unit not in UNITS or type(places) is not int or not 0 <= places <= 6:
        raise ValueError('format')
    scaled = Fraction(value) / UNITS[unit] * 10**places
    magnitude = abs(scaled)
    rounded = (2*magnitude.numerator + magnitude.denominator) // (2*magnitude.denominator)
    sign = '-' if scaled < 0 and rounded else ''
    digits = str(rounded).zfill(places + 1)
    if places: digits = digits[:-places] + '.' + digits[-places:]
    return sign + digits + ' ' + unit
''', [
"assert parse('1.5 KiB') == 1536",
"assert parse('1 KB + 24 B') == 1024",
"assert format_bytes(1536, 'KiB', 2) == '1.50 KiB'",
"assert parse('-1 KiB + 2 KB - 1.5 B') == parse('974.5 B')",
"for s in ['', '1', '.5 B', '1. B', '1e3 B', '1 kb', '1 B 2 B', '1 B + -2 B', '1 B +']:\n    with pytest.raises(ValueError): parse(s)",
"from fractions import Fraction\nassert parse('0.1 B') == Fraction(1, 10)\nassert format_bytes(Fraction(-1, 2), 'B', 0) == '-1 B'\nassert format_bytes(Fraction(-1, 1000), 'B', 2) == '0.00 B'",
"for value, unit, places in [(1.0, 'B', 2), (True, 'B', 2), (1, 'bad', 2), (1, 'B', True), (1, 'B', 7)]:\n    with pytest.raises(ValueError): format_bytes(value, unit, places)",
"assert parse('1GiB-1GB') == 73741824\nassert format_bytes(10**30, 'GB', 0) == '1000000000000000000000 GB'",
"assert parse(' + 1 B \\t + 0.25B ') == parse('1.25 B')\nassert format_bytes(-1500, 'KB', 0) == '-2 KB'",
], start=[('task.py', 'i, total, first = 0, Fraction(0), True', "m = re.fullmatch(r'\\s*([0-9]+(?:\\.[0-9]+)?)\\s*([A-Za-z]+)\\s*', text)\n    if not m or m[2] not in UNITS: raise ValueError('single term only')\n    return Fraction(m[1]) * UNITS[m[2]]\n    i, total, first = 0, Fraction(0), True"), ('task.py', "if (type(value) is not int and not isinstance(value, Fraction)) or type(value) is bool:", "raise NotImplementedError('formatter')\n    if (type(value) is not int and not isinstance(value, Fraction)) or type(value) is bool:")])

emit('balanced_rounding', 'numeric', 3, 'implement', '''
# Balanced row rounding
Implement `round_rows(rows, places=2)` for a list of rows of finite decimal
strings. Return lists of fixed-point strings. Each row must round as a whole:
round its exact sum half to even to the target number of places. Start each
cell at its floor (toward negative infinity) at that precision; distribute the
remaining quantum units to cells by decreasing fractional remainder, breaking
ties by smaller column index. Consequently each output cell is either its floor
or ceiling, and the output row sum equals its rounded exact sum. Empty rows stay
empty. places is integer 0..6, bool invalid; invalid options or nonfinite/invalid
numbers raise ValueError. Negative zero prints positive. No caller mutation,
no binary floats, and caller Decimal context must not affect results. Tested
inputs have <=30 digits and absolute exponent <=30. Rows round independently.
''', '''
from decimal import Decimal, InvalidOperation, localcontext, ROUND_HALF_EVEN, ROUND_FLOOR


def round_rows(rows, places=2):
    if type(places) is not int or not 0 <= places <= 6:
        raise ValueError('places')
    result = []
    with localcontext() as ctx:
        ctx.prec = 100
        quantum = Decimal(1).scaleb(-places)
        for row in rows:
            try:
                values = [Decimal(value) / quantum for value in row]
            except (InvalidOperation, ValueError, TypeError):
                raise ValueError('number') from None
            if any(not v.is_finite() for v in values): raise ValueError('finite')
            floors = [int(v.to_integral_value(rounding=ROUND_FLOOR)) for v in values]
            target = int(sum(values, Decimal(0)).to_integral_value(rounding=ROUND_HALF_EVEN))
            count = target - sum(floors)
            order = sorted(range(len(values)), key=lambda i: (-(values[i] - floors[i]), i))
            for i in order[:count]: floors[i] += 1
            result.append([format(Decimal(n) * quantum if n else Decimal(0), f'.{places}f') for n in floors])
    return result
''', [
"assert round_rows([['.333', '.333', '.334']]) == [['0.33', '0.33', '0.34']]",
"assert round_rows([['.005', '.005']]) == [['0.01', '0.00']]",
"assert round_rows([[], ['1']]) == [[], ['1.00']]",
"assert round_rows([['-.005', '-.005']]) == [['0.00', '-0.01']]",
"assert round_rows([['2.5'], ['3.5']], 0) == [['2'], ['4']]",
"assert round_rows([['-1.2', '1.2']], 0) == [['-1', '1']]",
"for rows, p in [([['NaN']], 2), ([['Infinity']], 2), ([['bad']], 2), ([], True), ([], -1), ([], 7)]:\n    with pytest.raises(ValueError): round_rows(rows, p)",
"from decimal import localcontext\nwith localcontext() as c:\n    c.prec = 3\n    assert round_rows([['1234567890.005', '.005']]) == [['1234567890.01', '0.00']]",
"a = [['.125', '.125', '.125', '.125']]\nold = deepcopy(a)\nassert round_rows(a) == [['0.13', '0.13', '0.12', '0.12']]\nassert a == old\nassert round_rows([]) == []",
])
