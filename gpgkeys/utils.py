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


class ignoresignals(object):
    """Context manager to temporarily ignore SIGINT and SIGQUIT.
    """

    def __init__(self):
        self.signums = (signal.SIGINT, signal.SIGQUIT)
        self.saved = {}

    def __enter__(self):
        for signum in self.signums:
            self.saved[signum] = signal.getsignal(signum)
            signal.signal(signum, signal.SIG_IGN)

    def __exit__(self, *ignored):
        for signum in reversed(self.signums):
            signal.signal(signum, self.saved[signum])


class surrogateescape(object):
    """Context manager to switch sys.stdin to 'surrogateescape'
    error handling. Requires Python 3.
    """

    def __init__(self):
        self.saved = sys.stdin.errors

    def __enter__(self):
        import io
        sys.stdin = io.TextIOWrapper(
            sys.stdin.detach(), sys.stdin.encoding, 'surrogateescape')

    def __exit__(self, *ignored):
        import io
        sys.stdin = io.TextIOWrapper(
            sys.stdin.detach(), sys.stdin.encoding, self.saved)

