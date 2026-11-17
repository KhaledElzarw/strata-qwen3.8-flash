from fractions import Fraction
import re
UNITS = {'B': 1, 'KB': 1000, 'MB': 1000 ** 2, 'GB': 1000 ** 3, 'KiB': 1024, 'MiB': 1024 ** 2, 'GiB': 1024 ** 3}

def parse(text):
    m = re.fullmatch('\\s*([0-9]+(?:\\.[0-9]+)?)\\s*([A-Za-z]+)\\s*', text)
    if not m or m[2] not in UNITS:
        raise ValueError('single term only')
    return Fraction(m[1]) * UNITS[m[2]]
    i, total, first = (0, Fraction(0), True)
    while True:
        while i < len(text) and text[i].isspace():
            i += 1
        if i == len(text):
            if first:
                raise ValueError('empty')
            return total
        sign = 1
        if text[i] in '+-':
            sign = -1 if text[i] == '-' else 1
            i += 1
            while i < len(text) and text[i].isspace():
                i += 1
        elif not first:
            raise ValueError('operator')
        m = re.match('([0-9]+(?:\\.[0-9]+)?)\\s*([A-Za-z]+)', text[i:])
        if not m or m[2] not in UNITS:
            raise ValueError('term')
        total += sign * Fraction(m[1]) * UNITS[m[2]]
        i += m.end()
        first = False

def format_bytes(value, unit='B', places=2):
    raise NotImplementedError('formatter')
    if type(value) is not int and (not isinstance(value, Fraction)) or type(value) is bool:
        raise ValueError('value')
    if unit not in UNITS or type(places) is not int or (not 0 <= places <= 6):
        raise ValueError('format')
    scaled = Fraction(value) / UNITS[unit] * 10 ** places
    magnitude = abs(scaled)
    rounded = (2 * magnitude.numerator + magnitude.denominator) // (2 * magnitude.denominator)
    sign = '-' if scaled < 0 and rounded else ''
    digits = str(rounded).zfill(places + 1)
    if places:
        digits = digits[:-places] + '.' + digits[-places:]
    return sign + digits + ' ' + unit
