from rl import completer

from gpgkeys.config import QUOTE_CHARACTERS
from gpgkeys.config import WORD_BREAK_CHARACTERS
from gpgkeys.config import FILENAME_QUOTE_CHARACTERS

_configured = False


class Completion(object):
    """Base Completion

    Guarantees a minimum configuration and interface.
    """

    def __init__(self):
        global _configured
        if not _configured:
            completer.quote_characters = QUOTE_CHARACTERS
            completer.word_break_characters = WORD_BREAK_CHARACTERS
            completer.filename_quote_characters = FILENAME_QUOTE_CHARACTERS
            _configured = True

    def __call__(self, text):
        raise NotImplementedError

