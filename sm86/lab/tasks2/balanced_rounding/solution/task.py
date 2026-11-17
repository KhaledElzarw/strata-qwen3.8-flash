from decimal import Decimal, InvalidOperation, localcontext, ROUND_HALF_EVEN, ROUND_FLOOR

def round_rows(rows, places=2):
    if type(places) is not int or not 0 <= places <= 6:
        raise ValueError('places')
    result = []
    with localcontext() as ctx:
        ctx.prec = 100
        quantum = Decimal(1).scaleb(-places)
        for row in rows:
            try:
                values = [Decimal(value) / quantum for value in row]
            except (InvalidOperation, ValueError, TypeError):
                raise ValueError('number') from None
            if any((not v.is_finite() for v in values)):
                raise ValueError('finite')
            floors = [int(v.to_integral_value(rounding=ROUND_FLOOR)) for v in values]
            target = int(sum(values, Decimal(0)).to_integral_value(rounding=ROUND_HALF_EVEN))
            count = target - sum(floors)
            order = sorted(range(len(values)), key=lambda i: (-(values[i] - floors[i]), i))
            for i in order[:count]:
                floors[i] += 1
            result.append([format(Decimal(n) * quantum if n else Decimal(0), f'.{places}f') for n in floors])
    return result
