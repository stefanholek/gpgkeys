import sys
import signal
import re

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


class cbreakmode(object):
    """Context manager to put the terminal in 'cbreak' mode.
    Note that this is not the same as tty.setcbreak would give us!
    """

    def __enter__(self):
        self.saved = tcgetattr(sys.stdin)
        mode = tcgetattr(sys.stdin)
        mode[LFLAG] = mode[LFLAG] & ~(ECHO | ICANON)
        mode[CC][VMIN] = 0  # Zero chars is a valid result
        mode[CC][VTIME] = 1 # Wait for input
        tcsetattr(sys.stdin, TCSANOW, mode)

    def __exit__(self, *ignored):
        tcsetattr(sys.stdin, TCSAFLUSH, self.saved)


def _readyx():
    """Read a CSI R formatted response from sys.stdin.
    """
    p = ''
    c = sys.stdin.read(1)
    while c:
        p += c
        if c == 'R':
            break
        c = sys.stdin.read(1)
    if p:
        m = re.search(r'\[(\d+);(\d+)R', p)
        if m is not None:
            return int(m.group(1), 10), int(m.group(2), 10)
    return 0, 0


def getyx():
    """Return the cursor position as 1-based (row, col) tuple.
    Row and col are 0 if the terminal does not support DSR 6.
    """
    with cbreakmode():
        sys.stdout.write('\033[6n')
        return _readyx()


def getmaxyx():
    """Return the terminal window dimensions as (maxrow, maxcol) tuple.
    Maxrow and maxcol are 0 if the terminal does not support DSR 6.
    """
    with cbreakmode():
        row, col = getyx()
        try:
            sys.stdout.write('\033[10000;10000f\033[6n')
            return _readyx()
        finally:
            sys.stdout.write('\033[%d;%df' % (row, col))

