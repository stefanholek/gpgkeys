import sys


def decode(text):
    """Decode from the charset of the current locale."""
    if sys.version_info[0] >= 3:
        return text.decode(sys.getfilesystemencoding(), 'surrogateescape')
    else:
        return text.decode(sys.getfilesystemencoding(), 'replace')


def encode(text):
    """Encode to the charset of the current locale."""
    if sys.version_info[0] >= 3:
        return text.encode(sys.getfilesystemencoding(), 'surrogateescape')
    else:
        return text.encode(sys.getfilesystemencoding(), 'replace')


def char(int):
    """Create a one-character byte string from the ordinal ``int``."""
    if sys.version_info[0] >= 3:
        return bytes((int,))
    else:
        return chr(int)

