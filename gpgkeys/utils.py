import sys
import signal


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


def ignoresignal(signum):
    """Decorator to temporarily ignore signals."""
    def wrapper(func):
        def wrapped_func(*args, **kw):
            saved = signal.getsignal(signum)
            signal.signal(signum, signal.SIG_IGN)
            try:
                return func(*args, **kw)
            finally:
                signal.signal(signum, saved)

        wrapped_func.__doc__ = func.__doc__
        wrapped_func.__name__ = func.__name__
        wrapped_func.__module__ = func.__module__
        wrapped_func.__dict__.update(func.__dict__)
        return wrapped_func
    return wrapper


class ignore_signals(object):
    """Context manager to temporarily ignore signals."""

    def __init__(self, *signums):
        self.signums = signums
        self.saved = {}

    def __enter__(self):
        for signum in self.signums:
            self.saved.setdefault(signum, signal.getsignal(signum))
            signal.signal(signum, signal.SIG_IGN)

    def __exit__(self, *ignored):
        for signum in reversed(self.signums):
            signal.signal(signum, self.saved[signum])

