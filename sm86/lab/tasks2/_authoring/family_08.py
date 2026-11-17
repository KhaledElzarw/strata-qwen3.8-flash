from common import emit

emit('inventory_hunt', 'bug_hunts', 4, 'fix', '''
# Warehouse bug hunt
Repair the existing three-module warehouse. `Warehouse(stock)` accepts dict
string SKU -> nonnegative integer quantity, rejecting negative quantities with
ValueError. `reserve(order, lines)` accepts a unique order string and dict SKU ->
positive integer quantity; unknown SKU raises KeyError, invalid quantity or
repeated order raises ValueError. All validation precedes mutation. Available
stock excludes reservations. Insufficient availability raises ValueError with no
change. `cancel(order)` restores reserved units, removing the order; unknown
order raises KeyError. `ship(order)` removes the reservation permanently without
restoring units; unknown order raises KeyError. `available(sku)` returns stock
left for new orders, unknown SKU raises KeyError. `orders()` returns a deep copy
of pending order mappings. Caller mappings and instances remain isolated.
Keep the public API across task.py, stock.py and validation.py.
''', {
'validation.py': '''
def quantities(lines, allow_zero=False):
    for value in lines.values():
        if type(value) is not int or value < (0 if allow_zero else 1):
            raise ValueError('quantity')
''',
'stock.py': '''
class Stock:
    def __init__(self, amounts):
        self.amounts = dict(amounts)

    def take(self, lines):
        for sku, amount in lines.items():
            if self.amounts[sku] < amount:
                raise ValueError('shortage')
        for sku, amount in lines.items():
            self.amounts[sku] -= amount

    def restore(self, lines):
        for sku, amount in lines.items():
            self.amounts[sku] += amount
''',
'task.py': '''
from copy import deepcopy
from stock import Stock
from validation import quantities


class Warehouse:
    def __init__(self, stock):
        quantities(stock, allow_zero=True)
        self.stock = Stock(stock)
        self.pending = {}

    def reserve(self, order, lines):
        if order in self.pending:
            raise ValueError('order exists')
        quantities(lines)
        self.stock.take(lines)
        self.pending[order] = dict(lines)

    def cancel(self, order):
        lines = self.pending.pop(order)
        self.stock.restore(lines)

    def ship(self, order):
        self.pending.pop(order)

    def available(self, sku):
        return self.stock.amounts[sku]

    def orders(self):
        return deepcopy(self.pending)
''',
}, [
"w = Warehouse({'a': 5})\nw.reserve('o', {'a': 2})\nassert w.available('a') == 3",
"w = Warehouse({'a': 5})\nw.reserve('o', {'a': 2})\nw.cancel('o')\nassert w.available('a') == 5 and w.orders() == {}",
"w = Warehouse({'a': 5})\nw.reserve('o', {'a': 2})\nw.ship('o')\nassert w.available('a') == 3",
"w = Warehouse({'a': 5, 'b': 1})\nwith pytest.raises(ValueError): w.reserve('o', {'a': 2, 'b': 2})\nassert w.available('a') == 5 and w.orders() == {}",
"w = Warehouse({'a': 5})\nwith pytest.raises(KeyError): w.reserve('o', {'a': 1, 'z': 1})\nassert w.available('a') == 5",
"s = {'a': 5}\nw = Warehouse(s)\nw.reserve('o', {'a': 1})\nassert s == {'a': 5}\nr = w.orders()\nr['o']['a'] = 99\nassert w.orders() == {'o': {'a': 1}}",
"w = Warehouse({'a': 2})\nw.reserve('o', {'a': 1})\nwith pytest.raises(ValueError): w.reserve('o', {'a': 1})\nassert w.available('a') == 1",
"for q in [-1, 0, True, 1.5]:\n    with pytest.raises(ValueError): Warehouse({'a': 3}).reserve('o', {'a': q})\nwith pytest.raises(ValueError): Warehouse({'a': -1})\nassert Warehouse({'a': 0}).available('a') == 0",
"w = Warehouse({'a': 1})\nfor f in [lambda: w.cancel('x'), lambda: w.ship('x'), lambda: w.available('x')]:\n    with pytest.raises(KeyError): f()\nassert Warehouse({'a': 2}).orders() == {}",
], start=[('validation.py', 'type(value) is not int', 'not isinstance(value, int)'), ('stock.py', 'for sku, amount in lines.items():\n            self.amounts[sku] -= amount', 'for sku, amount in lines.items():\n            self.amounts[sku] -= amount'), ('stock.py', 'if self.amounts[sku] < amount:', 'self.amounts[sku] -= amount\n            if self.amounts[sku] < 0:'), ('stock.py', 'self.amounts[sku] -= amount\n\n    def restore', 'self.amounts[sku] -= 0\n\n    def restore'), ('task.py', 'return deepcopy(self.pending)', 'return dict(self.pending)')])

emit('search_index_hunt', 'bug_hunts', 4, 'fix', '''
# Search index bug hunt
Repair task.py, words.py and postings.py. `Index.put(id, text)` inserts or
replaces a document. Tokenization is runs of Unicode alphabetic characters,
casefolded; digits, underscores and punctuation separate tokens. `remove(id)`
returns bool. `search(query)` ANDs the distinct query tokens: return document IDs
containing every token, sorted by decreasing total occurrence count of those
DISTINCT tokens, then lexical ID. Empty query tokens yield []. Replacing or
removing a document erases ALL its old postings, including terms still present
in others. Repeated query terms do not increase rank. IDs are strings, text/query
strings. `terms(id)` returns a fresh dict token -> count; missing raises KeyError.
Instances share nothing. Keep the public API and input data unchanged.
''', {
 'words.py': '''
from collections import Counter


def counts(text):
    words, current = [], []
    for ch in text:
        if ch.isalpha():
            current.append(ch)
        elif current:
            words.append(''.join(current).casefold())
            current = []
    if current:
        words.append(''.join(current).casefold())
    return Counter(words)
''',
 'postings.py': '''
def discard(postings, ident, terms):
    for term in terms:
        postings[term].pop(ident, None)
        if not postings[term]:
            del postings[term]


def rank(postings, words):
    words = set(words)
    if not words:
        return []
    groups = [set(postings.get(w, {})) for w in words]
    common = set.intersection(*groups)
    return sorted(common, key=lambda ident: (-sum(postings[w][ident] for w in words), ident))
''',
 'task.py': '''
from tokenize import counts
from postings import discard, rank


class Index:
    def __init__(self):
        self.docs = {}
        self.postings = {}

    def put(self, ident, text):
        self.remove(ident)
        terms = counts(text)
        self.docs[ident] = terms
        for term, count in terms.items():
            self.postings.setdefault(term, {})[ident] = count

    def remove(self, ident):
        if ident not in self.docs:
            return False
        discard(self.postings, ident, self.docs.pop(ident))
        return True

    def search(self, query):
        return rank(self.postings, counts(query))

    def terms(self, ident):
        return dict(self.docs[ident])
'''.replace('from tokenize import', 'from words import'),
}, [
"i = Index()\ni.put('a', 'red blue red')\nassert i.search('red') == ['a']\nassert i.terms('a') == {'red': 2, 'blue': 1}",
"i = Index()\ni.put('a', 'red')\ni.put('b', 'blue')\nassert i.search('red blue') == []",
"i = Index()\ni.put('a', 'x')\nassert i.remove('a')\nassert not i.remove('a')",
"i = Index()\ni.put('a', 'red red')\ni.put('b', 'red')\ni.put('a', 'blue')\nassert i.search('red') == ['b']\nassert i.search('blue') == ['a']",
"i = Index()\ni.put('a', 'x x y')\ni.put('b', 'x y y')\nassert i.search('x x y') == ['a', 'b']",
"i = Index()\ni.put('a', 'Straße STRASSE café_foo2bar')\nassert i.terms('a') == {'strasse': 2, 'café': 1, 'foo': 1, 'bar': 1}",
"i = Index()\ni.put('b', 'x')\ni.put('a', 'x')\ni.put('c', 'x x')\nassert i.search('x') == ['c', 'a', 'b']\nassert i.search('123') == []",
"i = Index()\ni.put('a', 'x')\ni.put('b', 'x')\ni.remove('a')\nassert i.search('x') == ['b']\nt = i.terms('b')\nt.clear()\nassert i.terms('b') == {'x': 1}",
"i = Index()\ni.put('a', '')\nassert i.terms('a') == {}\nassert Index().search('x') == []\nwith pytest.raises(KeyError): i.terms('missing')",
], start={'words.py': '''
from collections import Counter


def counts(text):
    words, current = [], []
    for ch in text:
        if ch.isalnum():
            current.append(ch)
        elif current:
            words.append(''.join(current).casefold())
            current = []
    if current:
        words.append(''.join(current).casefold())
    return Counter(words)
''', 'postings.py': '''
def discard(postings, ident, terms):
    for term in terms:
        postings[term].pop(ident, None)
        if not postings[term]:
            del postings[term]


def rank(postings, words):
    words = set(words)
    if not words:
        return []
    groups = [set(postings.get(w, {})) for w in words]
    common = set.union(*groups)
    return sorted(common, key=lambda ident: (-sum(postings.get(w, {}).get(ident, 0) for w in words), ident))
''', 'task.py': '''
from words import counts
from postings import discard, rank


class Index:
    def __init__(self):
        self.docs = {}
        self.postings = {}

    def put(self, ident, text):
        terms = counts(text)
        self.docs[ident] = terms
        for term, count in terms.items():
            self.postings.setdefault(term, {})[ident] = count

    def remove(self, ident):
        if ident not in self.docs:
            return False
        discard(self.postings, ident, self.docs.pop(ident))
        return True

    def search(self, query):
        return rank(self.postings, counts(query))

    def terms(self, ident):
        return dict(self.docs[ident])
'''.replace('tokenize', 'words')})

emit('invoice_hunt', 'bug_hunts', 4, 'fix', '''
# Invoice calculation bug hunt
Repair the three-module invoice calculator `invoice(lines, discount='0', tax='0')`.
Each line is dict with sku string, quantity positive integer (bool invalid),
and price a nonnegative finite Decimal-compatible string. discount and tax are
finite decimal strings: 0 <= discount <= 1 and tax >= 0. Invalid values raise
ValueError. Compute each extended price quantity*price, apply (1-discount), then
round EACH discounted line to cents with ROUND_HALF_UP. Subtotal is sum of these
rounded lines. Tax is subtotal*tax rounded once HALF_UP to cents. Return dict
`lines` (list `(sku, formatted_line_total)` in input order), `subtotal`, `tax`,
`total`, all money strings with exactly two fractional digits; total=subtotal+tax.
Use Decimal throughout, independent of caller Decimal precision/rounding context;
values tested have at most 30 significant digits. No input mutation; empty lines
are valid and still validate rates. Keep task.py, money.py and pricing.py API.
''', {
'money.py': '''
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def number(text):
    try:
        value = Decimal(text)
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError('decimal') from None
    if not value.is_finite() or value < 0:
        raise ValueError('amount')
    return value


def cents(value):
    return value.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)


def display(value):
    return format(value, '.2f')
''',
'pricing.py': '''
from money import number, cents


def line_total(line, discount):
    quantity = line['quantity']
    if type(quantity) is not int or quantity <= 0:
        raise ValueError('quantity')
    return cents(number(line['price']) * quantity * (1 - discount))
''',
'task.py': '''
from decimal import Decimal, localcontext
from money import number, cents, display
from pricing import line_total


def invoice(lines, discount='0', tax='0'):
    with localcontext() as ctx:
        ctx.prec = 100
        discount, tax = number(discount), number(tax)
        if discount > 1:
            raise ValueError('discount')
        totals = [(line['sku'], line_total(line, discount)) for line in lines]
        subtotal = sum((v for _, v in totals), Decimal(0))
        taxes = cents(subtotal * tax)
        return {'lines': [(sku, display(v)) for sku, v in totals],
                'subtotal': display(subtotal), 'tax': display(taxes),
                'total': display(subtotal + taxes)}
''',
}, [
"r = invoice([dict(sku='a', quantity=2, price='3')])\nassert r == {'lines': [('a', '6.00')], 'subtotal': '6.00', 'tax': '0.00', 'total': '6.00'}",
"assert invoice([], tax='.1')['total'] == '0.00'",
"assert invoice([dict(sku='a', quantity=1, price='10')], '.2', '.1')['total'] == '8.80'",
"assert invoice([dict(sku='a', quantity=1, price='1.005')])['subtotal'] == '1.01'",
"r = invoice([dict(sku='a', quantity=2, price='.335')], '.1')\nassert r['subtotal'] == '0.60'",
"r = invoice([dict(sku='a', quantity=1, price='.005')]*2, tax='.25')\nassert r['subtotal'] == '0.02' and r['tax'] == '0.01'",
"for v in ['NaN', 'Infinity', '-1', 'bad']:\n    with pytest.raises(ValueError): invoice([dict(sku='a', quantity=1, price=v)])\nfor q in [0, -1, True]:\n    with pytest.raises(ValueError): invoice([dict(sku='a', quantity=q, price='1')])",
"for d, t in [('1.1', '0'), ('0', '-1'), ('NaN', '0')]:\n    with pytest.raises(ValueError): invoice([], d, t)",
"from decimal import localcontext, ROUND_DOWN\na = [dict(sku='a', quantity=1, price='123456789012345678901234567.005')]\nwith localcontext() as ctx:\n    ctx.prec = 6\n    ctx.rounding = ROUND_DOWN\n    assert invoice(a)['total'] == '123456789012345678901234567.01'\nassert a[0]['price'].endswith('.005')",
], start=[('money.py', 'rounding=ROUND_HALF_UP', "rounding='ROUND_HALF_EVEN'"), ('pricing.py', "return cents(number(line['price']) * quantity * (1 - discount))", "return cents(number(line['price'])) * quantity * (1 - discount)"), ('task.py', 'ctx.prec = 100', 'ctx.prec = 28')])

emit('dependency_hunt', 'bug_hunts', 4, 'fix', '''
# Dependency resolver bug hunt
Repair `resolve(catalog, roots)` across task.py, versions.py and solver.py.
catalog maps package strings to dict integer version -> dependency dict package ->
minimum integer version. roots maps package -> minimum. Pick ONE version per
required package satisfying all minima, introducing selected-version dependencies
recursively. All versions/minima are positive integers; catalogs in tests are
well formed. Missing packages or unsatisfiable minima raise ValueError. Cyclic
dependencies are permitted if version constraints can be satisfied. Return a
version dict for exactly the transitive closure of selected roots. Among ALL
valid assignments minimize the sum of selected version numbers; ties minimize
the sorted tuple `(package, version)` of the assignment lexicographically.
Do not choose a highest version greedily. Do not retain constraints from versions
not selected. Do not mutate catalog or roots. Empty roots returns {}. Catalogs
have at most eight packages and four versions each; exhaustive search is allowed.
''', {
'versions.py': '''
def choices(catalog):
    return [(name, sorted(versions)) for name, versions in sorted(catalog.items())]
''',
'solver.py': '''
def valid(catalog, roots, candidate):
    required = dict(roots)
    pending = list(roots)
    visited = set()
    while pending:
        name = pending.pop()
        if name not in candidate or candidate[name] < required[name]:
            return False
        if name in visited:
            continue
        visited.add(name)
        for dep, minimum in catalog[name][candidate[name]].items():
            required[dep] = max(required.get(dep, 0), minimum)
            if dep not in candidate or candidate[dep] < required[dep]:
                return False
            pending.append(dep)
    return set(candidate) == visited


def score(candidate):
    return sum(candidate.values()), tuple(sorted(candidate.items()))
''',
'task.py': '''
from itertools import product
from versions import choices
from solver import valid, score


def resolve(catalog, roots):
    options = choices(catalog)
    result = None
    for picked in product(*[[None] + versions for _, versions in options]):
        candidate = {name: version for (name, _), version in zip(options, picked) if version is not None}
        if valid(catalog, roots, candidate):
            if result is None or score(candidate) < score(result):
                result = candidate
    if result is None:
        raise ValueError('unsatisfiable')
    return result
''',
}, [
"assert resolve({'a': {1: {}, 2: {}}}, {'a': 1}) == {'a': 1}",
"assert resolve({'a': {1: {'b': 2}}, 'b': {1: {}, 2: {}}}, {'a': 1}) == {'a': 1, 'b': 2}",
"assert resolve({'a': {1: {}}}, {}) == {}",
"c = {'a': {1: {'b': 3}, 2: {}}, 'b': {3: {}}}\nassert resolve(c, {'a': 1}) == {'a': 2}",
"c = {'a': {1: {'b': 2}, 2: {'b': 1}}, 'b': {1: {}, 2: {}}}\nassert resolve(c, {'a': 1}) == {'a': 1, 'b': 2}",
"c = {'a': {1: {'b': 1}}, 'b': {1: {'a': 1}}}\nassert resolve(c, {'a': 1}) == {'a': 1, 'b': 1}",
"for c, r in [({}, {'x': 1}), ({'a': {1: {}}}, {'a': 2}), ({'a': {1: {'x': 1}}}, {'a': 1})]:\n    with pytest.raises(ValueError): resolve(c, r)",
"c = {'a': {1: {'b': 1, 'c': 1}}, 'b': {1: {'d': 1}}, 'c': {1: {'d': 2}}, 'd': {1: {}, 2: {}}}\nold = deepcopy(c)\nassert resolve(c, {'a': 1}) == {'a': 1, 'b': 1, 'c': 1, 'd': 2}\nassert c == old",
"assert resolve({'a': {1: {}}, 'unused': {1: {'missing': 1}}}, {'a': 1}) == {'a': 1}\nassert resolve({'a': {1: {'b': 2}, 2: {}}, 'b': {1: {}}}, {'a': 1}) == {'a': 2}",
], start=[('solver.py', 'candidate[name] < required[name]', 'candidate[name] <= required[name]'), ('solver.py', 'return sum(candidate.values()), tuple(sorted(candidate.items()))', 'return -sum(candidate.values()), tuple(sorted(candidate.items()))'), ('solver.py', 'return set(candidate) == visited', 'return True')])
