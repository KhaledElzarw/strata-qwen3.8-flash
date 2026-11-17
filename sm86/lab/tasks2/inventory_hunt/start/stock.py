class Stock:

    def __init__(self, amounts):
        self.amounts = dict(amounts)

    def take(self, lines):
        for sku, amount in lines.items():
            self.amounts[sku] -= amount
            if self.amounts[sku] < 0:
                raise ValueError('shortage')
        for sku, amount in lines.items():
            self.amounts[sku] -= 0

    def restore(self, lines):
        for sku, amount in lines.items():
            self.amounts[sku] += amount
