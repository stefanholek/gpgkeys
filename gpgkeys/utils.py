import sys
import signal

from termios import *
from tty import LFLAG, CC


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


class cbreak(object):
    """Context manager to put the terminal in 'cbreak' mode.
    Note that this is not the same as tty.setcbreak would give us.
    """

    def __init__(self, fd):
        self.fd = fd

    def __enter__(self):
        self.saved = tcgetattr(self.fd)
        mode = tcgetattr(self.fd)
        mode[LFLAG] = mode[LFLAG] & ~(ECHO | ICANON)
        mode[CC][VMIN] = 0
        mode[CC][VTIME] = 1
        tcsetattr(self.fd, TCSANOW, mode)

    def __exit__(self, *ignored):
        tcsetattr(self.fd, TCSAFLUSH, self.saved)

