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

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
