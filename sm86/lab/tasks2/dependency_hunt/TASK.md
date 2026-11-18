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

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
