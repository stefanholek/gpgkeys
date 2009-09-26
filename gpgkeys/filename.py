import os

from datetime import datetime

from rl import completer
from rl import completion
from rl import print_exc

from escape import scan_open_quote

BASH_QUOTE_CHARACTERS = "'\""
BASH_COMPLETER_WORD_BREAK_CHARACTERS = " \t\n\"'@><=;|&(:"
BASH_NOHOSTNAME_WORD_BREAK_CHARACTERS = " \t\n\"'><=;|&(:"
BASH_FILENAME_QUOTE_CHARACTERS = "\\ \t\n\"'@<>=;|&()#$`?*[!:{~"
BASH_COMMAND_SEPARATORS = ";|&{(`"


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
                f.write('\t\t\t 0123456789012345678901234567890123456789012345678901234567890\n')
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
        completer.quote_characters = '"\''
        completer.word_break_characters = BASH_NOHOSTNAME_WORD_BREAK_CHARACTERS
        completer.filename_quote_characters = BASH_FILENAME_QUOTE_CHARACTERS
        completer.char_is_quoted_function = self.char_is_quoted
        completer.filename_quoting_function = self.quote_filename
        completer.filename_dequoting_function = self.dequote_filename
        completer.directory_completion_hook = self.dequote_dirname
        completer.match_hidden_files = False
        completer.tilde_expansion = True
        self.quoted = dict((x, '\\'+x) for x in completer.filename_quote_characters)
        self.log('-----')

    @print_exc
    def __call__(self, text):
        self.log('complete_filename\t%r', text)
        if text.startswith('~') and (os.sep not in text):
            completion.suppress_quote = True # Tilde triggers closing quote
            matches = completion.complete_username(text)
        else:
            matches = completion.complete_filename(text)
        self.log('complete_filename\t%r', matches[:20])
        return matches

    @print_exc
    def char_is_quoted(self, text, index):
        qc = scan_open_quote(text, index)
        self.log('char_is_quoted\t\t%r %d %r', text, index, qc, ruler=True)
        if index > 0:
            # If a character is preceded by a backslash, we consider
            # it quoted.
            if qc != "'" and text[index-1] == '\\':
                self.log('char_is_quoted\t\tTrue1')
                return True
            # If we have an unquoted quote character, check whether
            # it is quoted by the other quote character.
            if text[index] in completer.quote_characters:
                if qc and qc in completer.quote_characters and qc != text[index]:
                    self.log('char_is_quoted\t\tTrue2')
                    return True
            else:
                # If we have an unquoted character, check whether
                # there is an open quote character.
                if qc and qc in completer.quote_characters:
                    self.log('char_is_quoted\t\tTrue3')
                    return True
        self.log('char_is_quoted\t\tFalse')
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
            else:
                for c in completer.filename_quote_characters:
                    text = text.replace(self.quoted[c], c)
        self.log('dequote_filename\t%r', text)
        return text

    @print_exc
    def dequote_dirname(self, text):
        # XXX By using this hook we lose the ability to switch off
        #     tilde expansion. Bug or feature?
        self.log("dequote_dirname\t\t%r %r", text, completion.quote_character)
        saved, self.do_log = self.do_log, False
        text = self.dequote_filename(text, completion.quote_character)
        self.do_log = saved
        self.log('dequote_dirname\t\t%r', text)
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
            # Don't quote strings if all characters are already
            # backslash-quoted.
            check = text
            if qc != "'" and check and not quote_char:
                for c in completer.filename_quote_characters:
                    check = check.replace(self.quoted[c], '')
                if check:
                    for c in completer.filename_quote_characters:
                        if c in check:
                            break
                    else:
                        check = ''
            # Add leading and trailing quote characters
            if check:
                if (single_match and not completion.suppress_quote
                    and not os.path.isdir(os.path.expanduser(text))):
                    text = text + qc
                text = qc + text
        self.log('quote_filename\t\t%r', text)
        return text


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
            def quote(s, c):
                return s.replace(c, self.quoted[c])

            for c in completer.filename_quote_characters:
                # Don't quote a leading tilde
                if c == '~' and text.startswith(c):
                    text = c + quote(text[1:], c)
                else:
                    text = quote(text, c)
        self.log('quote_filename\t\t%r', text)
        return text


class FilenameCompletion(object):
    """Encapsulate filename completion strategies
    """

    def __init__(self, do_log=False, bash=False):
        if bash:
            self._strategy = BashCompletionStrategy(do_log)
        else:
            self._strategy = FilenameCompletionStrategy(do_log)

    def __call__(self, text):
        return self._strategy(text)

    def __getattr__(self, name):
        return getattr(self._strategy, name)

