"""Room reuse and overlap reporting for half-open bookings.

Room identifiers are allocated in deterministic order.
Empty bookings keep their identity without using a room."""
import heapq

def _read(bookings):
    """Materialize and validate the booking iterable once.

Repeated IDs are invalid even for empty ranges.
No caller-owned booking object is modified."""
    items = list(bookings)
    seen = set()
    for ident, start, end in items:
        if ident in seen or start > end:
            raise ValueError('booking')
        seen.add(ident)
    return items

def assign(bookings):
    """Release finished rooms before assigning each booking.

One heap tracks active ends and another tracks free room IDs.
The smallest free room always wins."""
    items = _read(bookings)
    active, free = ([], [])
    result = {i: None for i, s, e in items if s == e}
    rooms = 0
    for ident, start, end in sorted(items, key=lambda b: (b[1], b[2], b[0])):
        if start == end:
            continue
        while active and active[0][0] <= start:
            _, room = heapq.heappop(active)
            heapq.heappush(free, room)
        if free:
            room = heapq.heappop(free)
        else:
            room = rooms
            rooms += 1
        result[ident] = room
        heapq.heappush(active, (end, room))
    return result

def conflicts(bookings):
    """Report intersecting nonempty booking pairs.

Endpoints touching at one instant are compatible.
Sort each pair and then the full report."""
    items = _read(bookings)
    pairs = []
    for n, (a, s, e) in enumerate(items):
        for b, t, u in items[n + 1:]:
            if s < e and t < u and (max(s, t) < min(e, u)):
                pairs.append(tuple(sorted((a, b))))
    return sorted(pairs)

def utilization(bookings):
    """Total occupied duration for each assigned room.

Reuse the assignment policy rather than duplicating it.
Empty bookings do not contribute a room entry."""
    items = list(bookings)
    rooms = assign(items)
    totals = {}
    for ident, start, end in items:
        room = rooms[ident]
        if room is not None:
            totals[room] = totals.get(room, 0) + end - start
    return totals
