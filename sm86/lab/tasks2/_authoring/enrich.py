"""Additional level-two interactions, kept separate from task serialization."""
import ast
import textwrap


def enrich(ident, spec, solution, checks):
    if isinstance(solution, dict):
        return spec, solution, checks
    source = textwrap.dedent(solution).strip() + '\n'
    extra, rules, cases = '', '', []
    if ident == 'coverage_bands':
        rules = """
Also implement first_window(intervals, length, minimum=1): earliest integer
start of a length-long continuous span meeting minimum, or None. length must
be positive (ValueError). Coverage count changes do not break continuity when
both counts meet minimum. Accept one-shot iterables and validate as bands.
"""
        extra = '''
def first_window(intervals, length, minimum=1):
    if length <= 0:
        raise ValueError('length')
    ranges = bands(intervals, minimum)
    run_start = None
    run_end = None
    for start, end, _ in ranges:
        if run_end != start:
            run_start = start
        run_end = end
        if run_end - run_start >= length:
            return run_start
    return None
'''
        cases = ["assert first_window([(0, 4), (2, 6)], 5) == 0\nassert first_window([(0, 4), (2, 6)], 3, 2) is None",
                 "assert first_window(iter([(-3, 0), (0, 3)]), 6) == -3\nwith pytest.raises(ValueError): first_window([], 0)",
                 "assert first_window([(0, 1), (2, 5)], 2) == 2\nassert first_window([], 1) is None"]
    elif ident == 'header_parameters':
        rules = """
Add format_header(main, parameters): strip/lowercase nonempty main; reject
semicolon or CR/LF in main, invalid/duplicate case-insensitive parameter names,
or CR/LF in values with ValueError. Sort lowercase names lexically; quote every
value and escape backslash and quote. Join with semicolon and single space.
Values are strings. parse must round-trip this output.
"""
        extra = r'''
def format_header(main, parameters):
    main = main.strip(' \t').lower()
    if not main or any(ch in main for ch in ';\r\n'):
        raise ValueError('main')
    normalized = {}
    for name, value in parameters.items():
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', name):
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
'''
        cases = [r"""assert format_header(' X ', {'B': '2', 'A': ''}) == 'x; a=""; b="2"'""",
                 r"""params = {'Q': 'a"b\\c;d'}
assert parse(format_header('x', params)) == ('x', {'q': params['Q']})""",
                 """for main, params in [('x;y', {}), ('x', {'A': '1', 'a': '2'}), ('x', {'1x': 'a'}), ('x', {'a': '\\n'})]:
    with pytest.raises(ValueError): format_header(main, params)"""]
    elif ident == 'room_assignment':
        rules = """
Add utilization(bookings): return dict room -> sum of durations assigned to it
under assign's policy. Empty bookings contribute nothing; no rooms gives {}.
Consume the iterable once, validate identically and never change inputs.
"""
        extra = '''
def utilization(bookings):
    items = list(bookings)
    rooms = assign(items)
    totals = {}
    for ident, start, end in items:
        room = rooms[ident]
        if room is not None:
            totals[room] = totals.get(room, 0) + end - start
    return totals
'''
        cases = ["assert utilization(iter([('a', 0, 2), ('b', 2, 5), ('c', 1, 2)])) == {0: 5, 1: 1}",
                 "assert utilization([('e', 1, 1)]) == {}\nwith pytest.raises(ValueError): utilization([('x', 2, 1)])",
                 "assert utilization([('z', 0, 3), ('a', 0, 1), ('b', 3, 4)]) == {1: 3, 0: 2}"]
    elif ident == 'nested_transactions':
        source = 'from contextlib import contextmanager\n' + source
        rules = """
Add transaction() as a context manager yielding this Store: begin on entry,
commit on normal exit, rollback on any BaseException and re-raise it. Contexts
may nest, but their bodies do not manually begin/commit/rollback transactions.
"""
        source += '''
    @contextmanager
    def transaction(self):
        self.begin()
        try:
            yield self
        except BaseException:
            self.rollback()
            raise
        else:
            self.commit()
'''
        cases = ["s = Store()\nwith s.transaction() as same:\n    assert same is s\n    s.set('x', 1)\nassert s.snapshot() == {'x': 1} and s.depth == 0",
                 "s = Store({'x': 0})\nwith pytest.raises(RuntimeError):\n    with s.transaction():\n        s.set('x', 1)\n        raise RuntimeError()\nassert s.get('x') == 0 and s.depth == 0",
                 "s = Store()\nwith pytest.raises(KeyboardInterrupt):\n    with s.transaction():\n        with s.transaction(): s.set('x', 1)\n        raise KeyboardInterrupt()\nassert s.snapshot() == {}"]
    elif ident == 'prefix_catalog':
        source = 'from functools import lru_cache\n' + source
        rules = """
Add match(pattern, limit=5) returning words ranked as suggest, matching the
ENTIRE pattern: '?' matches one character, '*' zero or more, backslash escapes
the next character; dangling escape raises ValueError even for an empty catalog.
Consecutive stars allowed. Negative limit raises ValueError. Match Unicode by
Python character. Do not enumerate wildcard expansions.
"""
        source += r'''
    def match(self, pattern, limit=5):
        if limit < 0:
            raise ValueError('limit')
        tokens = []
        i = 0
        while i < len(pattern):
            ch = pattern[i]
            if ch == '\\':
                i += 1
                if i == len(pattern):
                    raise ValueError('escape')
                tokens.append(('literal', pattern[i]))
            else:
                tokens.append((ch if ch in '*?' else 'literal', ch))
            i += 1

        def accepts(word):
            @lru_cache(None)
            def visit(i, j):
                if i == len(tokens):
                    return j == len(word)
                kind, value = tokens[i]
                if kind == '*':
                    return visit(i + 1, j) or (j < len(word) and visit(i, j + 1))
                return (j < len(word) and (kind == '?' or value == word[j])
                        and visit(i + 1, j + 1))
            return visit(0, 0)
        return [w for w in self.suggest('', len(self)) if accepts(w)][:limit]
'''
        cases = ["c = Catalog()\nfor w, n in [('cat', 2), ('cart', 3), ('cut', 1), ('act', 5)]: c.put(w, n)\nassert c.match('c?t') == ['cat', 'cut']\nassert c.match('c*t') == ['cart', 'cat', 'cut']",
                 r"""c = Catalog()
c.put('a*b', 2)
c.put('axb', 3)
assert c.match(r'a\*b') == ['a*b']
with pytest.raises(ValueError): c.match(chr(92))""",
                 "c = Catalog()\nc.put('é', 0)\nassert c.match('?') == ['é']\nassert c.match('**', 0) == []\nwith pytest.raises(ValueError): c.match('*', -1)"]
    elif ident == 'overlay_delete':
        rules = """
Add explain(base, layers) returning (merged, history), where history is a list
per layer of sorted changed key-path tuples. Compare recursively, type-strictly:
if both values are dicts recurse; otherwise emit that path when changed.
Adding/removing a dict emits its parent path only. No-op layers give [].
Lists are atomic, including nested bool/int differences. No input mutation.
"""
        extra = '''
def _same(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_same(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    return a == b


def _changes(before, after, prefix=()):
    if isinstance(before, dict) and isinstance(after, dict):
        result = []
        for key in sorted(before.keys() | after.keys()):
            path = prefix + (key,)
            if key not in before or key not in after:
                result.append(path)
            else:
                result.extend(_changes(before[key], after[key], path))
        return result
    return [] if _same(before, after) else [prefix]


def explain(base, layers):
    current = merge(base, [])
    history = []
    for layer in layers:
        updated = merge(current, [layer])
        history.append(_changes(current, updated))
        current = updated
    return current, history
'''
        cases = ["assert explain({'a': {'b': 1}}, [{'a': {'b': 2}}, {'a': {'b': 2}}]) == ({'a': {'b': 2}}, [[('a', 'b')], []])",
                 "assert explain({}, [{'x': {'a': 1}}, {'x': {'$delete': True}}]) == ({}, [[('x',)], [('x',)]])",
                 "assert explain({'a': [True]}, [{'a': [1]}])[1] == [[('a',)]]"]
    elif ident == 'weighted_cache':
        rules = """
Add resize(budget): validate positive budget before mutation, purge once at the
injected current time, set budget, and evict LRU entries until weight fits.
Growing preserves recency and expiry. Read clock once; invalid resize does not.
"""
        source += '''
    def resize(self, budget):
        if budget <= 0:
            raise ValueError('budget')
        self._purge(self.clock())
        self.budget = budget
        total = sum(item[1] for item in self.entries.values())
        while total > budget:
            _, (_, removed, _) = self.entries.popitem(last=False)
            total -= removed
'''
        cases = ["c = Cache(5, lambda: 0)\nc.put('a', 1, 2)\nc.put('b', 2, 2)\nc.resize(2)\nassert c.keys() == ['b'] and c.weight == 2",
                 "c = Cache(2, lambda: 0)\nc.put('a', 1)\nwith pytest.raises(ValueError): c.resize(0)\nassert c.keys() == ['a']\nc.resize(4)\nassert c.keys() == ['a']",
                 "t = [0]\nc = Cache(3, lambda: t[0])\nc.put('a', 1, 2, ttl=1)\nc.put('b', 2)\nt[0] = 1\nc.resize(1)\nassert c.keys() == ['b']"]
    elif ident == 'escaped_frames':
        rules = """
Decoder exposes errors, initially 0: count each NONEMPTY body with invalid
checksum, or any dangling escape at delimiter. Empty delimiter runs are not
errors. reset() clears framing state but keeps errors. finish() discards an
unfinished nonempty frame or dangling escape, counting one error, then resets
framing. It returns None and may be repeated.
"""
        source = source.replace('self.inside = False', 'self.errors = 0\n        self.inside = False', 1)
        source = source.replace("self.inside = True\n                self.body.clear()", """if self.inside and (self.escaped or (self.body and sum(self.body[:-1]) % 256 != self.body[-1])):
                    self.errors += 1
                self.inside = True
                self.body.clear()""")
        source += '''
    def reset(self):
        self.inside = False
        self.escaped = False
        self.body.clear()

    def finish(self):
        if self.inside and (self.body or self.escaped):
            self.errors += 1
        self.reset()
'''
        cases = ["d = Decoder()\nd.feed(bytes([126, 1, 2, 126, 125, 126]))\nassert d.errors == 2\nd.feed(b'~~~')\nassert d.errors == 2",
                 "d = Decoder()\nd.feed(encode(b'x')[:-1])\nd.finish()\nd.finish()\nassert d.errors == 1\nassert d.feed(encode(b'y')) == [b'y']",
                 "d = Decoder()\nd.feed(bytes([126, 125]))\nd.reset()\nassert d.errors == 0\nassert d.feed(encode(b'')) == [b'']"]

    elif ident == 'event_dispatch':
        rules = """
Add clear(topic=None): remove all handlers of that topic, or all topics for
None, returning count removed. Dispatch already in progress keeps its snapshot.
Add subscribers(topic): fresh list of callbacks in subscription order. Both
methods belong to Bus and have module wrappers through default_bus.
"""
        extra = """
def _clear(self, topic=None):
    if topic is None:
        count = sum(len(handlers) for handlers in self.handlers.values())
        self.handlers.clear()
        return count
    return len(self.handlers.pop(topic, []))


def _subscribers(self, topic):
    return [callback for callback, _ in self.handlers.get(topic, [])]


Bus.clear = _clear
Bus.subscribers = _subscribers


def clear(topic=None):
    return default_bus.clear(topic)


def subscribers(topic):
    return default_bus.subscribers(topic)
"""
        # Put the methods into the class rather than leaving runtime patches.
        extra = extra.replace('Bus.clear = _clear\nBus.subscribers = _subscribers\n', '')
        methods = """    def clear(self, topic=None):
        if topic is None:
            count = sum(len(handlers) for handlers in self.handlers.values())
            self.handlers.clear()
            return count
        return len(self.handlers.pop(topic, []))

    def subscribers(self, topic):
        return [callback for callback, _ in self.handlers.get(topic, [])]

"""
        source = source.replace('default_bus = Bus()', methods + '\ndefault_bus = Bus()')
        extra = extra[extra.index('def clear(topic=None):'):]
        cases = ["b = Bus()\nf = lambda v: v\nb.subscribe('x', f)\nr = b.subscribers('x')\nr.clear()\nassert b.subscribers('x') == [f]\nassert b.clear('x') == 1\nassert b.clear('x') == 0",
                 "b = Bus()\nb.subscribe('x', lambda v: v)\nb.subscribe('y', lambda v: v)\nassert b.clear() == 2\nassert b.subscribers('y') == []",
                 "f = lambda v: v\nsubscribe('clear-legacy', f)\nassert subscribers('clear-legacy') == [f]\nassert clear('clear-legacy') == 1"]
    elif ident == 'bounded_apportion':
        rules = """
Add changes(total, weights, previous, caps=None): return sorted (name, delta)
pairs for nonzero differences from allocate's result. previous maps only known
names to nonnegative integers; missing names mean zero. Reject invalid/unknown
previous entries with ValueError even if total or cap is also invalid. Do not
mutate previous. This reports movement, not a new allocation algorithm.
"""
        extra = """
def changes(total, weights, previous, caps=None):
    if previous.keys() - weights.keys():
        raise ValueError('unknown previous name')
    for amount in previous.values():
        _integer(amount, 0)
    planned = allocate(total, weights, caps)
    result = []
    for name in sorted(weights):
        delta = planned[name] - previous.get(name, 0)
        if delta:
            result.append((name, delta))
    return result
"""
        cases = ["assert changes(4, {'a': 1, 'b': 1}, {'a': 4}) == [('a', -2), ('b', 2)]",
                 "for previous in [{'x': 0}, {'a': -1}, {'a': True}]:\n    with pytest.raises(ValueError): changes(1, {'a': 1}, previous)",
                 "previous = {'a': 2, 'b': 2}\nassert changes(4, {'a': 1, 'b': 1}, previous) == []\nassert previous == {'a': 2, 'b': 2}"]
    elif ident == 'decimal_display':
        rules = """
Add format_column(values, places=2, mode='even', grouping=False): apply
format_number to each value, then left-pad with spaces to the widest formatted
value's length. Return list of strings; [] for no values, but still validate
places/mode. Accept an iterable once. Never strip sign or grouping punctuation.
"""
        extra = """
def format_column(values, places=2, mode='even', grouping=False):
    format_number('0', places, mode, grouping)
    formatted = []
    for value in values:
        formatted.append(format_number(value, places, mode, grouping))
    if not formatted:
        return []
    width = max(len(value) for value in formatted)
    return [value.rjust(width) for value in formatted]
"""
        cases = ["assert format_column(['1.2', '-1234.5'], grouping=True) == ['     1.20', '-1,234.50']",
                 "assert format_column(iter(['2.345', '-0.001']), mode='away') == ['2.35', '0.00']",
                 "assert format_column([]) == []\nwith pytest.raises(ValueError): format_column([], places=-1)"]
    elif ident == 'ranked_routes':
        rules = """
Add routes(graph, start): return dict reachable node -> (cost, path), including
start, under exactly the same ties and validation. Compute all routes with one
shortest-path search, not repeated route calls.
"""
        extra = """
def routes(graph, start):
    _validate(graph, start)
    best = _search(graph, start)
    return {node: (cost, path) for node, (cost, hops, path) in best.items()}
"""
        # Share a complete search between both APIs.
        source = source.replace('def route(graph, start, goal):', 'def _validate(graph, start):')
        source = source.replace('    if goal not in graph: raise KeyError(goal)\n', '')
        source = source.replace('    initial = (0, 0, (start,))', '\n\ndef _search(graph, start):\n    initial = (0, 0, (start,))')
        source = source.replace('        if node == goal: return cost, path\n', '')
        source = source.replace('    return None\n', '    return best\n')
        source += """
def route(graph, start, goal):
    _validate(graph, start)
    if goal not in graph:
        raise KeyError(goal)
    best = _search(graph, start)
    if goal not in best:
        return None
    cost, hops, path = best[goal]
    return cost, path
"""
        cases = ["assert routes({'a': [('b', 1)], 'b': [], 'c': []}, 'a') == {'a': (0, ('a',)), 'b': (1, ('a', 'b'))}",
                 "g = {'s': [('b', 1), ('a', 1)], 'a': [('t', 1)], 'b': [('t', 1)], 't': []}\nassert routes(g, 's')['t'] == (2, ('s', 'a', 't'))",
                 "with pytest.raises(KeyError): routes({'a': [], 'z': [('bad', 0)]}, 'a')\nwith pytest.raises(KeyError): routes({}, 'a')"]

    if ident == 'decimal_display':
        begin = source.index('    try:\n        value = Decimal(text)')
        end = source.index('    with localcontext()', begin)
        parse_body = source[begin:end]
        source = source[:begin] + '    value = _number(text)\n' + source[end:]
        source += '\n\ndef _number(text):\n' + parse_body + '    return value\n'
    if ident == 'group_totals_cli':
        begin = source.index('    totals = {}')
        end = source.index('    rows = ', begin)
        parse_body = source[begin:end]
        parse_body = parse_body.replace('return 1', "raise ValueError(n)")
        parse_body = parse_body.replace("            print(f'error: line {n}', file=sys.stderr)\n", '')
        source = (source[:begin] +
                  "    try:\n        totals = _read_totals(sys.stdin if stdin is None else stdin)\n"
                  "    except ValueError as exc:\n        print(f'error: line {exc.args[0]}', file=sys.stderr)\n        return 1\n" +
                  source[end:])
        parse_body = parse_body.replace('sys.stdin if stdin is None else stdin', 'stream')
        source += '\n\ndef _read_totals(stream):\n' + parse_body + '    return totals\n'
    source += '\n' + textwrap.dedent(extra)
    return spec + rules, source, checks + cases


DOCS = {
    'coverage_bands': {
        None: ('Half-open coverage arithmetic.', 'Counts describe regions between distinct endpoints.', 'Zero-length inputs never create coverage.'),
        'bands': ('Split the covered line at changes in multiplicity.', 'Batch equal endpoints before considering the next region.', 'Coalesce adjacent regions whose counts agree.'),
        'peak': ('Find the largest coverage and its first coordinate.', 'The normalized bands are chronological.', 'No nonempty coverage has no peak coordinate.'),
        'first_window': ('Find the first continuous stretch meeting a threshold.', 'Adjacent eligible bands remain one stretch across count changes.', 'A gap resets the candidate start.')
    },
    'bounded_apportion': {
        None: ('Exact capped weighted apportionment.', 'Integer results conserve the requested total.', 'Remainders and ties are independent of mapping order.'),
        '_integer': ('Validate a nonboolean integer lower bound.', 'Use exact types because bool inherits from int.', 'Validation happens before allocation begins.'),
        'allocate': ('Freeze binding caps before distributing remainders.', 'Each pass removes all currently saturated names together.', 'Fraction preserves ordering for arbitrarily large weights.'),
        'changes': ('Compare a new allocation with the prior allocation.', 'Validate the prior mapping before computing the new plan.', 'Report only movements, in name order.')
    },
    'decimal_display': {
        None: ('Exact decimal display and aligned columns.', 'Formatting controls precision locally.', 'Parsing accepts only the documented display grammar.'),
        'format_number': ('Round and print a finite decimal in fixed point.', 'The rounding mode is explicit rather than ambient.', 'Normalize signed zero before applying grouping.'),
        'parse_display': ('Parse a canonical grouped or ungrouped display.', 'Validate separators before removing commas.', 'Negative zero is intentionally excluded.'),
        'format_column': ('Format a column before computing its common width.', 'Materializing once supports generator inputs.', 'An empty column still validates formatting options.'),
        '_number': ('Convert an input string to a nonnegative-or-negative finite value.', 'Conversion errors share the public ValueError contract.', 'No arithmetic is done in the caller context.')
    },
    'escaped_frames': {
        None: ('Incremental delimiter and escape framing.', 'Feed boundaries do not have protocol meaning.', 'Corrupt frames are counted and discarded.'),
        'encode': ('Construct one delimited checksum frame.', 'Escape reserved bytes in both payload and checksum.', 'Empty payloads still carry a checksum byte.'),
        'feed': ('Consume bytes while preserving partial frame state.', 'A delimiter closes and restarts the framing window.', 'Only complete checksum-valid bodies are delivered.'),
        'reset': ('Forget an unfinished frame without changing error history.', 'Returning outside the frame ignores subsequent noise.', 'The next delimiter begins a fresh body.')
    },
    'nested_transactions': {
        None: ('Nested snapshots with independent mutable values.', 'Every public value boundary copies deeply.', 'History belongs to one Store instance.'),
        'begin': ('Save the state visible at this nesting depth.', 'Inner commits keep their edits in current data.', 'The outer saved state remains available for rollback.'),
        'commit': ('Discard only the innermost saved state.', 'Current values already contain the committed edits.', 'Committing without a transaction is an error.'),
        'transaction': ('Pair a begin with exactly one closing operation.', 'Catch BaseException so interruptions also roll back.', 'Propagate failures after restoring the entry snapshot.')
    },
    'overlay_delete': {
        None: ('Layered object overlays with deletion and change histories.', 'Deletion markers are exact and type-sensitive.', 'List contents are data rather than overlay instructions.')
    },
    'ranked_routes': {
        None: ('Directed shortest routes with stable whole-path ties.', 'Search state includes cost, hops, and the entire path.', 'Validation includes disconnected graph components.'),
        '_validate': ('Check nodes and all edge weights before searching.', 'Unknown neighbor names cannot become implicit vertices.', 'Booleans are not accepted as integer weights.'),
        '_search': ('Compute the best rank of every reachable node.', 'Stale heap ranks cannot supersede a newer route.', 'An extra zero-cost cycle loses on hop count.'),
        'routes': ('Expose the complete reachable-node route mapping.', 'Project internal hop counts out of the public result.', 'One search handles every destination.'),
        'route': ('Return one destination using the shared search.', 'Unreachable destinations produce None.', 'The start route has cost zero and no edges.')
    },
    'room_assignment': {
        None: ('Room reuse and overlap reporting for half-open bookings.', 'Room identifiers are allocated in deterministic order.', 'Empty bookings keep their identity without using a room.'),
        '_read': ('Materialize and validate the booking iterable once.', 'Repeated IDs are invalid even for empty ranges.', 'No caller-owned booking object is modified.'),
        'assign': ('Release finished rooms before assigning each booking.', 'One heap tracks active ends and another tracks free room IDs.', 'The smallest free room always wins.'),
        'conflicts': ('Report intersecting nonempty booking pairs.', 'Endpoints touching at one instant are compatible.', 'Sort each pair and then the full report.'),
        'utilization': ('Total occupied duration for each assigned room.', 'Reuse the assignment policy rather than duplicating it.', 'Empty bookings do not contribute a room entry.')
    },
    'weighted_cache': {
        None: ('Weight-bounded recency with injected expiry time.', 'Each public operation uses one clock observation.', 'A live entry retains its insertion expiry on reads.')
    },
    'group_totals_cli': {
        None: ('Aggregate tab-separated totals before producing output.', 'Data failures leave standard output empty.', 'Argument parsing and data validation have separate statuses.'),
        '_positive': ('Parse a strictly positive command option.', 'Raise an argparse type error for invalid values.', 'This keeps usage failures at exit status two.'),
        'main': ('Validate all records, then filter, sort, and limit.', 'Thresholds apply to totals rather than individual lines.', 'Output begins only after the full input is accepted.'),
        '_read_totals': ('Read physical lines into exact integer totals.', 'Blank lines still count toward diagnostic positions.', 'Raise the failing position without printing partial results.')
    }
}


def readable(source, ident=None):
    tree = ast.parse(source)
    guards = [node for node in tree.body if isinstance(node, ast.If)
              and ast.unparse(node.test) == "__name__ == '__main__'"]
    tree.body = [node for node in tree.body if node not in guards] + guards
    docs = DOCS.get(ident, {})
    if None in docs:
        summary, detail, last = docs[None]
        tree.body.insert(0, ast.Expr(value=ast.Constant(summary + '\n\n' + detail + '\n' + last)))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in docs:
            summary, detail, last = docs[node.name]
            node.body.insert(0, ast.Expr(value=ast.Constant(summary + '\n\n' + detail + '\n' + last)))
    ast.fix_missing_locations(tree)
    return ast.unparse(tree) + '\n'
