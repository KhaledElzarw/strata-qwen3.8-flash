from copy import deepcopy
from stock import Stock
from validation import quantities

class Warehouse:

    def __init__(self, stock):
        quantities(stock, allow_zero=True)
        self.stock = Stock(stock)
        self.pending = {}

    def reserve(self, order, lines):
        if order in self.pending:
            raise ValueError('order exists')
        quantities(lines)
        self.stock.take(lines)
        self.pending[order] = dict(lines)

    def cancel(self, order):
        lines = self.pending.pop(order)
        self.stock.restore(lines)

    def ship(self, order):
        self.pending.pop(order)

    def available(self, sku):
        return self.stock.amounts[sku]

    def orders(self):
        return deepcopy(self.pending)
