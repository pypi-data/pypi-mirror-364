def dom_id(ids: list):
    return '-'.join(ids)


def dom_class(ids: list):
    return '-'.join(ids)


def svg_class(ids: list):
    return f"SvgIcon-{'-'.join(ids)}"
