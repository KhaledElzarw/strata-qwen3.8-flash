def quantities(lines, allow_zero=False):
    for value in lines.values():
        if not isinstance(value, int) or value < (0 if allow_zero else 1):
            raise ValueError('quantity')
