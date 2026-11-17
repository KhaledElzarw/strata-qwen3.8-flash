class Bus:

    def __init__(self):
        self.handlers = {}

    def _add(self, topic, callback, once):
        handlers = self.handlers.setdefault(topic, [])
        if any((cb is callback for cb, _ in handlers)):
            return False
        handlers.append((callback, once))
        return True

    def subscribe(self, topic, callback):
        return self._add(topic, callback, False)

    def once(self, topic, callback):
        return self._add(topic, callback, True)

    def unsubscribe(self, topic, callback):
        handlers = self.handlers.get(topic, [])
        for i, (cb, _) in enumerate(handlers):
            if cb is callback:
                del handlers[i]
                return True
        return False

    def emit(self, topic, value):
        result = []
        for callback, once in list(self.handlers.get(topic, [])):
            if once:
                self.unsubscribe(topic, callback)
            result.append(callback(value))
        return result

    def clear(self, topic=None):
        if topic is None:
            count = sum((len(handlers) for handlers in self.handlers.values()))
            self.handlers.clear()
            return count
        return len(self.handlers.pop(topic, []))

    def subscribers(self, topic):
        return [callback for callback, _ in self.handlers.get(topic, [])]
default_bus = Bus()

def subscribe(topic, callback):
    return default_bus.subscribe(topic, callback)

def unsubscribe(topic, callback):
    return default_bus.unsubscribe(topic, callback)

def emit(topic, value):
    return default_bus.emit(topic, value)

def once(topic, callback):
    return default_bus.once(topic, callback)

def clear(topic=None):
    return default_bus.clear(topic)

def subscribers(topic):
    return default_bus.subscribers(topic)
