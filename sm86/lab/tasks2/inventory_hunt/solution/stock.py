class Stock:

    def __init__(self, amounts):
        self.amounts = dict(amounts)

    def take(self, lines):
        for sku, amount in lines.items():
            if self.amounts[sku] < amount:
                raise ValueError('shortage')
        for sku, amount in lines.items():
            self.amounts[sku] -= amount

    def restore(self, lines):
        for sku, amount in lines.items():
            self.amounts[sku] += amount
