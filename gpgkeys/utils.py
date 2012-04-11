import sys
import signal
import locale

if sys.version_info[0] >= 3:
    errors = 'surrogateescape'
else:
    errors = 'replace'


def decode(text):
    """Decode from the charset of the current locale."""
    return text.decode(locale.getlocale()[1], errors)


def encode(text):
    """Encode to the charset of the current locale."""
    return text.encode(locale.getlocale()[1], errors)


def char(int):
    """Create a one-character byte string from the ordinal ``int``."""
    if sys.version_info[0] >= 3:
        return bytes((int,))
    else:
        return chr(int)


class ignoresignals(object):
    """Context manager to temporarily ignore SIGINT and SIGQUIT.
    """

    def __enter__(self):
        self.signums = (signal.SIGINT, signal.SIGQUIT)
        self.saved = {}
        for signum in self.signums:
            self.saved[signum] = signal.getsignal(signum)
            signal.signal(signum, signal.SIG_IGN)

    def __exit__(self, *ignored):
        for signum in self.signums:
            signal.signal(signum, self.saved[signum])


class surrogateescape(object):
    """Context manager to switch sys.stdin to 'surrogateescape'
    error handling. Requires Python 3.
    """

    def __enter__(self):
        import io
        self.saved = sys.stdin.errors
        sys.stdin = io.TextIOWrapper(
            sys.stdin.detach(), sys.stdin.encoding, 'surrogateescape')

    def __exit__(self, *ignored):
        import io
        sys.stdin = io.TextIOWrapper(
            sys.stdin.detach(), sys.stdin.encoding, self.saved)

