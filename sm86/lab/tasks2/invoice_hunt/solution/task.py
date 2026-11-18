from decimal import Decimal, localcontext
from money import number, cents, display
from pricing import line_total

def invoice(lines, discount='0', tax='0'):
    with localcontext() as ctx:
        ctx.prec = 100
        discount, tax = (number(discount), number(tax))
        if discount > 1:
            raise ValueError('discount')
        totals = [(line['sku'], line_total(line, discount)) for line in lines]
        subtotal = sum((v for _, v in totals), Decimal(0))
        taxes = cents(subtotal * tax)
        return {'lines': [(sku, display(v)) for sku, v in totals], 'subtotal': display(subtotal), 'tax': display(taxes), 'total': display(subtotal + taxes)}
