import os
import sys

from datetime import datetime
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


def compose(s):
    """Return fully composed UTF-8."""
    return normalize('NFC', s.decode('utf-8')).encode('utf-8')


def decompose(s):
    """Return fully decomposed UTF-8 for HFS Plus."""
    return normalize('NFD', s.decode('utf-8')).encode('utf-8')


class Logging(object):
    """Simple logging for filename completion
    """

    def __init__(self, do_log=False):
        self.do_log = do_log
        self.log_file = os.path.abspath('gpgkeys.log')

    def log(self, format, *args, **kw):
        if not self.do_log:
            return

        now = datetime.now().isoformat()[:19]
        now = '%s %s\t' % (now[:10], now[11:])

        f = open(self.log_file, 'at')
        try:
            f.write(now)
            if kw.get('ruler', False):
                ruler = '0123456789' * 6
                mark = kw.get('mark')
                if mark is not None and mark < len(ruler):
                    ruler = list(ruler)
                    ruler[mark] = '*'
                    ruler = ''.join(ruler)
                f.write('--------\t\t %s\n' % ruler)
                f.write(now)
            f.write(format % args)
            f.write('\n')
        finally:
            f.close()


class FilenameCompletionStrategy(Logging):
    """Perform filename completion

    Extends readline's default filename quoting by taking
    care of backslash-quoted characters.

    Quote characters are double quote and single quote.
    Prefers double-quote quoting over backslash quoting.
    Word break characters are quoted with backslashes when needed.
    Backslash quoting is disabled between single quotes.
    """

    def __init__(self, do_log=False):
        Logging.__init__(self, do_log)
        self.quoted = dict((x, '\\'+x) for x in BASH_FILENAME_QUOTE_CHARACTERS)
        self.configure()

    def configure(self):
        completer.quote_characters = MY_QUOTE_CHARACTERS
        completer.word_break_characters = MY_WORD_BREAK_CHARACTERS
        completer.filename_quote_characters = MY_FILENAME_QUOTE_CHARACTERS
        completer.char_is_quoted_function = self.char_is_quoted
        completer.filename_quoting_function = self.quote_filename

    @print_exc
    def __call__(self, text):
        self.log('complete_filename\t%r', text)
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
        self.log('complete_filename\t%r', matches[:20])
        return matches

    @print_exc
    def char_is_quoted(self, text, index):
        self.log('char_is_quoted\t\t%r %d', text, index, ruler=True, mark=index)
        skip_next = False
        quote_char = ''
        for i in range(index):
            c = text[i]
            if skip_next:
                skip_next = False
            elif quote_char != "'" and c == '\\':
                skip_next = True
                if i == index-1:
                    self.log('char_is_quoted\t\tTrue1')
                    return True
            elif quote_char != '':
                if c == quote_char:
                    quote_char = ''
            elif c in completer.quote_characters:
                quote_char = c
        # A closing quote character is never quoted
        if index < len(text) and text[index] == quote_char:
            self.log('char_is_quoted\t\tFalse1')
            return False
        # Return true if we have an open quote character
        if quote_char:
            self.log('char_is_quoted\t\tTrue2')
            return True
        self.log('char_is_quoted\t\tFalse2')
        return False

    @print_exc
    def dequote_filename(self, text, quote_char):
        self.log('dequote_filename\t%r %r', text, quote_char)
        if len(text) > 1:
            qc = quote_char or completer.quote_characters[0]
            # Don't backslash-dequote characters between single quotes,
            # except single quotes.
            if qc == "'":
                text = text.replace("'\\''", "'")
            elif '\\' in text:
                for c in BASH_FILENAME_QUOTE_CHARACTERS:
                    text = text.replace(self.quoted[c], c)
        self.log('dequote_filename\t%r', text)
        return text

    @print_exc
    def quote_filename(self, text, single_match, quote_char):
        self.log('quote_filename\t\t%r %s %r', text, single_match, quote_char)
        if text:
            qc = quote_char or completer.quote_characters[0]
            # Don't backslash-quote backslashes between single quotes
            if qc == "'":
                text = text.replace("'", "'\\''")
            else:
                text = text.replace('\\', self.quoted['\\'])
                text = text.replace(qc, self.quoted[qc])
            # Don't add quotes if the filename already is fully quoted
            if qc == "'" or quote_char or not self.is_fully_quoted(text):
                if text.startswith('~') and not quote_char:
                    text = completion.expand_tilde(text)
                if single_match:
                    if os.path.isdir(text):
                        completion.suppress_quote = True
                    if not completion.suppress_quote:
                        text = text + qc
                text = qc + text
        self.log('quote_filename\t\t%r', text)
        return text

    def is_fully_quoted(self, text):
        # Return true if all filename_quote_characters in text
        # are backslash-quoted.
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


class ReadlineCompletionStrategy(FilenameCompletionStrategy):
    """Perform filename completion

    Prefers single-quote quoting which is the readline default.
    """

    def configure(self):
        FilenameCompletionStrategy.configure(self)
        completer.quote_characters = BASH_QUOTE_CHARACTERS


class BashCompletionStrategy(FilenameCompletionStrategy):
    """Perform filename completion

    Prefers backslash quoting a la bash.
    """

    @print_exc
    def quote_filename(self, text, single_match, quote_char):
        # If the user has typed a quote character, use it.
        if quote_char and quote_char in completer.quote_characters:
            return FilenameCompletionStrategy.quote_filename(self, text, single_match, quote_char)
        # If not, default to backslash quoting.
        self.log('quote_filename\t\t%r %s %r', text, single_match, quote_char)
        if text:
            for c in completer.filename_quote_characters:
                text = text.replace(c, self.quoted[c])
        self.log('quote_filename\t\t%r', text)
        return text


class FilenameCompletion(object):
    """Encapsulate filename completion strategies
    """

    def __init__(self, quote_char='\\', do_log=False):
        if quote_char == '"':
            self._strategy = FilenameCompletionStrategy(do_log)
        elif quote_char == "'":
            self._strategy = ReadlineCompletionStrategy(do_log)
        else:
            self._strategy = BashCompletionStrategy(do_log)

    def __call__(self, text):
        return self._strategy(text)

    def __getattr__(self, name):
        return getattr(self._strategy, name)

