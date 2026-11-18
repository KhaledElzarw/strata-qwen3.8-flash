"""Half-open coverage arithmetic.

Counts describe regions between distinct endpoints.
Zero-length inputs never create coverage."""
from collections import defaultdict

def bands(intervals, minimum=1):
    """Split the covered line at changes in multiplicity.

Batch equal endpoints before considering the next region.
Coalesce adjacent regions whose counts agree."""
    if minimum <= 0:
        raise ValueError('minimum')
    events = defaultdict(int)
    for start, end in intervals:
        if start > end:
            raise ValueError('reversed')
        if start != end:
            events[start] += 1
            events[end] -= 1
    result = []
    count = 0
    previous = None
    for point in sorted(events):
        if previous is not None and previous < point and (count >= minimum):
            if result and result[-1][1] == previous and (result[-1][2] == count):
                result[-1] = (result[-1][0], point, count)
            else:
                result.append((previous, point, count))
        count += events[point]
        previous = point
    return result

def peak(intervals):
    """Find the largest coverage and its first coordinate.

The normalized bands are chronological.
No nonempty coverage has no peak coordinate."""
    spans = bands(intervals)
    if not spans:
        return (0, None)
    best = max((count for _, _, count in spans))
    return (best, next((start for start, _, count in spans if count == best)))

def first_window(intervals, length, minimum=1):
    """Find the first continuous stretch meeting a threshold.

Adjacent eligible bands remain one stretch across count changes.
A gap resets the candidate start."""
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
