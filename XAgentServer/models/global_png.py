global_map = {}


def add_to_map(key, value):
    global_map[key] = value


def lookup_in_map(key):
    return global_map.get(key)
