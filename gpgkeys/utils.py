import sys
import locale
import signal
import termios
import functools

preferrederrors = 'replace'


def memoize(func):
    """Cache forever."""
    cache = {}
    def memoizer():
        if 0 not in cache:
            cache[0] = func()
        return cache[0]
    return functools.wraps(func)(memoizer)


@memoize
def getpreferredencoding():
    """Return preferred encoding for text I/O."""
    encoding = locale.getpreferredencoding(False)
    if sys.platform == 'darwin' and encoding.startswith('mac-'):
        # Upgrade ancient MacOS encodings in Python < 2.7
        encoding = 'utf-8'
    return encoding


def getpreferrederrors():
    """Return preferred error handler (currently 'replace')."""
    return preferrederrors


def getinputencoding(stream=None):
    """Return preferred encoding for reading from ``stream``.

    ``stream`` defaults to sys.stdin.
    """
    if stream is None:
        stream = sys.stdin
    encoding = stream.encoding
    if not encoding:
        encoding = getpreferredencoding()
    return encoding


def getoutputencoding(stream=None):
    """Return preferred encoding for writing to ``stream``.

    ``stream`` defaults to sys.stdout.
    """
    if stream is None:
        stream = sys.stdout
    encoding = stream.encoding
    if not encoding:
        encoding = getpreferredencoding()
    return encoding


def decode(string, encoding=None, errors=None):
    """Decode from specified encoding.

    ``encoding`` defaults to the preferred encoding.
    ``errors`` defaults to the preferred error handler.
    """
    if encoding is None:
        encoding = getpreferredencoding()
    if errors is None:
        errors = getpreferrederrors()
    return string.decode(encoding, errors)


def encode(string, encoding=None, errors=None):
    """Encode to specified encoding.

    ``encoding`` defaults to the preferred encoding.
    ``errors`` defaults to the preferred error handler.
    """
    if encoding is None:
        encoding = getpreferredencoding()
    if errors is None:
        errors = getpreferrederrors()
    return string.encode(encoding, errors)


def char(int):
    """Create a one-character byte string from the ordinal ``int``."""
    if sys.version_info[0] >= 3:
        return bytes((int,))
    else:
        return chr(int)


def b(string, encoding='utf-8'):
    """Used instead of b'' literals to stay Python 2.5 compatible.

    ``encoding`` should match the encoding of the source file.
    """
    if sys.version_info[0] >= 3:
        return string.encode(encoding)
    else:
        return string


class conditional(object):
    """Wrap another context manager and enter it only if condition is true.
    """

    def __init__(self, condition, contextmanager):
        self.condition = condition
        self.contextmanager = contextmanager

    def __enter__(self):
        if self.condition:
            return self.contextmanager.__enter__()

    def __exit__(self, *args):
        if self.condition:
            return self.contextmanager.__exit__(*args)


class ignoresignals(object):
    """Context manager to temporarily ignore SIGINT and SIGQUIT.
    """
    signums = (signal.SIGINT, signal.SIGQUIT)

    def __enter__(self):
        self.saved = {}
        for signum in self.signums:
            self.saved[signum] = signal.getsignal(signum)
            signal.signal(signum, signal.SIG_IGN)

    def __exit__(self, *ignored):
        for signum in self.signums:
            signal.signal(signum, self.saved[signum])


class savettystate(object):
    """Context manager to save and restore the terminal state.

    Has no effect if sys.stdin is not a tty.
    """

    def __enter__(self):
        self.saved = None
        try:
            self.saved = termios.tcgetattr(sys.stdin)
        except termios.error:
            pass

    def __exit__(self, *ignored):
        if self.saved is not None:
            termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, self.saved)


class surrogateescape(object):
    """Context manager to switch sys.stdin to surrogateescape error handling.

    Has no effect under Python 2.
    """

    def __enter__(self):
        if sys.version_info[0] >= 3:
            import io
            self.encoding = sys.stdin.encoding
            self.errors = sys.stdin.errors
            self.newline = None if sys.platform == 'win32' else '\n'
            self.line_buffering = sys.stdin.line_buffering
            sys.stdin = io.TextIOWrapper(
                sys.stdin.detach(), self.encoding, 'surrogateescape',
                self.newline, self.line_buffering)

    def __exit__(self, *ignored):
        if sys.version_info[0] >= 3:
            import io
            sys.stdin = io.TextIOWrapper(
                sys.stdin.detach(), self.encoding, self.errors,
                self.newline, self.line_buffering)

