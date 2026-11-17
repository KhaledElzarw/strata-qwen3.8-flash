from money import number, cents

def line_total(line, discount):
    quantity = line['quantity']
    if type(quantity) is not int or quantity <= 0:
        raise ValueError('quantity')
    return cents(number(line['price']) * quantity * (1 - discount))
