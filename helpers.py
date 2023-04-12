def get_from_dict(d, path, default=''):
    try:
        for k in path:
            d = d[k]
        return d
    except KeyError:
        return default
