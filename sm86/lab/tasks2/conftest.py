"""Task fixtures are tested only in isolated copies by validate.py.

Avoid importing mutually independent task.py modules during repository-wide
pytest discovery. This file is never part of an agent's working folder.
"""
collect_ignore_glob = ["*/start", "*/hidden", "*/solution"]
