import locale

_cache = []


def decode(text):
    """Decode from the charset of the current locale."""
    if not _cache:
        _cache.append(locale.getlocale()[1])
    return text.decode(_cache[0])


def encode(text):
    """Encode to the charset of the current locale."""
    if not _cache:
        _cache.append(locale.getlocale()[1])
    return text.encode(_cache[0])

