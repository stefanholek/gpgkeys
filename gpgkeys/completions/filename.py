import os
import sys

from unicodedata import normalize

from rl import completer
from rl import completion
from rl import print_exc

BASH_QUOTE_CHARACTERS = "'\""
BASH_COMPLETER_WORD_BREAK_CHARACTERS = " \t\n\"'@><;|&=(:"
BASH_NOHOSTNAME_WORD_BREAK_CHARACTERS = " \t\n\"'><;|&=(:"
BASH_FILENAME_QUOTE_CHARACTERS = "\\ \t\n\"'@><;|&=()#$`?*[!:{~"
BASH_COMMAND_SEPARATORS = ";|&{(`"

MY_QUOTE_CHARACTERS = "\"'"
MY_WORD_BREAK_CHARACTERS = BASH_NOHOSTNAME_WORD_BREAK_CHARACTERS[:-3]
MY_FILENAME_QUOTE_CHARACTERS = BASH_FILENAME_QUOTE_CHARACTERS[:-1]

QUOTED = dict((x, '\\'+x) for x in BASH_FILENAME_QUOTE_CHARACTERS)


def compose(text):
    """Return fully composed UTF-8."""
    return normalize('NFC', text.decode('utf-8')).encode('utf-8')


def decompose(text):
    """Return fully decomposed UTF-8 for HFS Plus."""
    return normalize('NFD', text.decode('utf-8')).encode('utf-8')


def char_is_quoted(text, index):
    """Return true if the character at index is quoted."""
    skip_next = False
    quote_char = ''
    for i in range(index):
        c = text[i]
        if skip_next:
            skip_next = False
        elif quote_char != "'" and c == '\\':
            skip_next = True
            if i == index-1:
                return True
        elif quote_char != '':
            if c == quote_char:
                quote_char = ''
        elif c in completer.quote_characters:
            quote_char = c
    # A closing quote character is never quoted
    if index < len(text) and text[index] == quote_char:
        return False
    if quote_char:
        return True
    return False


def is_fully_quoted(text):
    """Return true if all filename_quote_characters in text
    are backslash-quoted."""
    skip_next = False
    size = len(text)
    for i in range(size):
        c = text[i]
        if skip_next:
            skip_next = False
        elif c == '\\':
            skip_next = True
            if i == size-1:
                return False
        elif c in completer.filename_quote_characters:
            return False
    return True


def dequote_filename(text, quote_char):
    """Return a dequoted version of text."""
    if len(text) > 1:
        qc = quote_char or completer.quote_characters[0]
        # Don't backslash-dequote characters between single quotes,
        # except single quotes.
        if qc == "'":
            text = text.replace("'\\''", "'")
        elif '\\' in text:
            for c in BASH_FILENAME_QUOTE_CHARACTERS:
                text = text.replace(QUOTED[c], c)
    return text


def quote_filename(text, single_match, quote_char):
    """Return a quoted version of text."""
    if text:
        qc = quote_char or completer.quote_characters[0]
        # Don't backslash-quote backslashes between single quotes
        if qc == "'":
            text = text.replace("'", "'\\''")
        else:
            text = text.replace('\\', QUOTED['\\'])
            text = text.replace(qc, QUOTED[qc])
        # Don't add quotes if the filename already is fully quoted
        if qc == "'" or quote_char or not is_fully_quoted(text):
            if text.startswith('~') and not quote_char:
                text = completion.expand_tilde(text)
            if single_match:
                if os.path.isdir(text):
                    completion.suppress_quote = True
                if not completion.suppress_quote:
                    text = text + qc
            text = qc + text
    return text


def backslash_quote_filename(text, single_match, quote_char):
    """Return a (backslash) quoted version of text."""
    if text:
        # If the user has typed a quote character, use it.
        if quote_char:
            text = quote_filename(text, single_match, quote_char)
        else:
            for c in completer.filename_quote_characters:
                text = text.replace(c, QUOTED[c])
    return text


class FilenameCompletion(object):
    """Perform filename completion

    Extends readline's default filename quoting by taking
    care of backslash-quoted characters.
    """

    def __init__(self, quote_char='\\'):
        self.configure(quote_char)

    def configure(self, quote_char):
        completer.quote_characters = MY_QUOTE_CHARACTERS
        completer.word_break_characters = MY_WORD_BREAK_CHARACTERS
        completer.filename_quote_characters = MY_FILENAME_QUOTE_CHARACTERS
        completer.char_is_quoted_function = self.char_is_quoted
        completer.filename_quoting_function = self.quote_filename

        if quote_char == "'":
            completer.quote_characters = BASH_QUOTE_CHARACTERS
        elif quote_char == '\\':
            completer.filename_quoting_function = self.backslash_quote_filename

    @print_exc
    def __call__(self, text):
        matches = []
        # Dequoting early allows us to skip some hooks
        if completion.found_quote:
            text = self.dequote_filename(text, completion.quote_character)
        if text.startswith('~') and (os.sep not in text):
            matches = completion.complete_username(text)
        if not matches:
            matches = completion.complete_filename(text)
            # HFS Plus uses "decomposed" UTF-8
            if sys.platform == 'darwin':
                if not matches:
                    matches = completion.complete_filename(decompose(text))
                matches = [compose(x) for x in matches]
        return matches

    @print_exc
    def char_is_quoted(self, text, index):
        return char_is_quoted(text, index)

    @print_exc
    def dequote_filename(self, text, quote_char):
        return dequote_filename(text, quote_char)

    @print_exc
    def quote_filename(self, text, single_match, quote_char):
        return quote_filename(text, single_match, quote_char)

    @print_exc
    def backslash_quote_filename(self, text, single_match, quote_char):
        return backslash_quote_filename(text, single_match, quote_char)

