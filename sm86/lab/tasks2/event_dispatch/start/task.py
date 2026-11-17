_handlers = {}

def subscribe(topic, callback):
    handlers = _handlers.setdefault(topic, [])
    if any((cb is callback for cb in handlers)):
        return False
    handlers.append(callback)
    return True

def unsubscribe(topic, callback):
    handlers = _handlers.get(topic, [])
    for i, cb in enumerate(handlers):
        if cb is callback:
            del handlers[i]
            return True
    return False

def emit(topic, value):
    return [cb(value) for cb in list(_handlers.get(topic, []))]

class Bus:

    def __init__(self):
        self.handlers = {}
    subscribe = staticmethod(subscribe)
    unsubscribe = staticmethod(unsubscribe)
    emit = staticmethod(emit)

    def once(self, topic, callback):
        raise NotImplementedError('one-shot')
default_bus = Bus()

def once(topic, callback):
    return default_bus.once(topic, callback)
