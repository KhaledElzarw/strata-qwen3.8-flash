class Registry:

    def __init__(self, parent=None):
        self.parent = parent
        self.local = {}

    def _name(self, name):
        if not isinstance(name, str) or not name:
            raise ValueError('name')

    def register(self, name, fn):
        self._name(name)
        if name in self.local or not callable(fn):
            raise ValueError('command')
        self.local[name] = ('function', fn)

    def alias(self, name, target):
        raise NotImplementedError('aliases')
        self._name(name)
        self._name(target)
        if name in self.local:
            raise ValueError('collision')
        self.local[name] = ('alias', target)

    def _lookup(self, name):
        if name in self.local:
            return self.local[name]
        raise KeyError(name)

    def invoke(self, name, *args, **kwargs):
        seen = set()
        while True:
            if name in seen:
                raise ValueError('alias cycle')
            seen.add(name)
            kind, value = self._lookup(name)
            if kind == 'function':
                return value(*args, **kwargs)
            name = value

    def names(self):
        inherited = self.parent.names() if self.parent is not None else []
        return sorted(set(inherited) | self.local.keys())

    def unregister(self, name):
        if name not in self.local:
            return False
        del self.local[name]
        return True
default_registry = Registry()

def register(name, fn):
    return default_registry.register(name, fn)

def invoke(name, *args, **kwargs):
    return default_registry.invoke(name, *args, **kwargs)

def names():
    return default_registry.names()

def alias(name, target):
    return default_registry.alias(name, target)

def unregister(name):
    return default_registry.unregister(name)
