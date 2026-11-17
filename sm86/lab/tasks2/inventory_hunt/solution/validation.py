def quantities(lines, allow_zero=False):
    for value in lines.values():
        if type(value) is not int or value < (0 if allow_zero else 1):
            raise ValueError('quantity')
