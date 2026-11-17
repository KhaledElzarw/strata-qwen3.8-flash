class Reader:

    def __init__(self, separator=','):
        if len(separator) != 1 or separator in '"\r\n':
            raise ValueError('separator')
        self.sep = separator
        self.state = 'start'
        self.field = ''
        self.row = []
        self.pending = False
        self.closed = False

    def _end_field(self):
        self.row.append(self.field)
        self.field = ''
        self.state = 'start'

    def feed(self, chunk):
        if self.closed:
            raise ValueError('closed')
        out = []
        for ch in chunk:
            if self.pending:
                if ch != '\n':
                    raise ValueError('bare CR')
                self.pending = False
                continue
            if self.state == 'quoted':
                if ch == '"':
                    self.state = 'after'
                else:
                    self.field += ch
                continue
            if self.state == 'after' and ch == '"':
                self.field += '"'
                self.state = 'quoted'
                continue
            if ch == self.sep:
                self._end_field()
            elif ch in '\r\n':
                self._end_field()
                out.append(self.row)
                self.row = []
                self.pending = ch == '\r'
            elif ch == '"' and self.state == 'start':
                self.state = 'quoted'
            elif ch == '"' or self.state == 'after':
                raise ValueError('quote placement')
            else:
                self.field += ch
                self.state = 'plain'
        return out

    def finish(self):
        if self.closed:
            raise ValueError('closed')
        self.closed = True
        if self.pending or self.state == 'quoted':
            raise ValueError('incomplete record')
        if self.row or self.field or self.state == 'after':
            self._end_field()
            return [self.row]
        return []
