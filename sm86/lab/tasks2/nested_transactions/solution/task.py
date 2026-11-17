"""Nested snapshots with independent mutable values.

Every public value boundary copies deeply.
History belongs to one Store instance."""
from contextlib import contextmanager
from copy import deepcopy

class Store:

    def __init__(self, initial=None):
        self.data = deepcopy({} if initial is None else initial)
        self.saved = []

    @property
    def depth(self):
        return len(self.saved)

    def begin(self):
        """Save the state visible at this nesting depth.

Inner commits keep their edits in current data.
The outer saved state remains available for rollback."""
        self.saved.append(deepcopy(self.data))

    def commit(self):
        """Discard only the innermost saved state.

Current values already contain the committed edits.
Committing without a transaction is an error."""
        if not self.saved:
            raise ValueError('no transaction')
        self.saved.pop()

    def rollback(self):
        if not self.saved:
            raise ValueError('no transaction')
        self.data = self.saved.pop()

    def set(self, key, value):
        self.data[key] = deepcopy(value)

    def get(self, key):
        return deepcopy(self.data[key])

    def delete(self, key):
        del self.data[key]

    def snapshot(self):
        return deepcopy(self.data)

    @contextmanager
    def transaction(self):
        """Pair a begin with exactly one closing operation.

Catch BaseException so interruptions also roll back.
Propagate failures after restoring the entry snapshot."""
        self.begin()
        try:
            yield self
        except BaseException:
            self.rollback()
            raise
        else:
            self.commit()
