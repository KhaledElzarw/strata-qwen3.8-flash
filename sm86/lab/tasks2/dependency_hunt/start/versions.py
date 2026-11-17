def choices(catalog):
    return [(name, sorted(versions)) for name, versions in sorted(catalog.items())]
