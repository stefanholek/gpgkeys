from functools import partial

from scanner import WHITESPACE
from scanner import QUOTECHARS
from scanner import char_is_quoted

DIGITS = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')
SHELL1 = ('>', '<', '|', '&', ';')
SHELL2 = ('>>', '>|', '>&', '&>', '<&', '<>', '<<')
SHELL3 = ('<<-', '<<<')

WORDBREAKCHARS = WHITESPACE + QUOTECHARS + SHELL1

# Token types
T_WORD = 1
T_SHELL = 2


class InfiniteString(str):
    """A string without IndexErrors."""

    def __getitem__(self, index):
        if index < 0 or index >= len(self):
            return None
        return str.__getitem__(self, index)


class Token(str):
    """A string with some additional attributes."""

    def __new__(cls, string, start, end, type):
        s = str.__new__(cls, string)
        s.start = start
        s.end = end
        s.type = type
        return s

    def __add__(self, string):
        s = str.__add__(self, string)
        return Token(s, self.start, self.end, self.type)


class Tokens(list):
    """A list of tokens."""

    def append(self, line, start, end, type):
        list.append(self, Token(line[start:end], start, end, type))


def split(line):
    """Return a tuple of tokens found in line.
    """
    skip_next = False
    quote_char = ''
    tokens = Tokens()
    append = partial(tokens.append, line)
    end = len(line)
    s = InfiniteString(line)
    i = j = 0

    while i < end:
        c = s[i]
        if skip_next:
            skip_next = False
        elif quote_char != "'" and c == '\\':
            skip_next = True
        elif quote_char != '':
            if c == quote_char:
                # Don't close the token if this is a backslash-
                # quoted single quote.
                if c in ("'",):
                    if s[i+1] in ('\\',):
                        if s[i+2] in ("'",):
                            if s[i+3] in ("'",):
                                i = i+5
                                continue
                quote_char = ''
                append(j, i+1, T_WORD)
                j = i+1
        elif c in QUOTECHARS:
            if i > j:
                append(j, i, T_WORD)
            j = i
            quote_char = c
        elif c in WHITESPACE:
            if i > j:
                append(j, i, T_WORD)
                j = i+1
            else:
                j = j+1
        elif c in ('|', ';'):
            if i > j:
                append(j, i, T_WORD)
            j = i
            append(j, i+1, T_SHELL)
            j = i+1
        elif c in ('&',):
            if i > j:
                append(j, i, T_WORD)
            j = i
            if s[i+1] in ('>',):
                i = i+1
            append(j, i+1, T_SHELL)
            j = i+1
        elif c in ('>',):
            if i > j:
                append(j, i, T_WORD)
            j = i
            if s[i+1] in ('&',):
                i = i+1
                if s[i+1] in DIGITS:
                    while s[i+1] in DIGITS:
                        i = i+1
                    if s[i+1] in ('-',):
                        i = i+1
            elif s[i+1] in ('>', '|'):
                i = i+1
            append(j, i+1, T_SHELL)
            j = i+1
        elif c in ('<',):
            if i > j:
                append(j, i, T_WORD)
            j = i
            if s[i+1] in ('&',):
                i = i+1
                if s[i+1] in DIGITS:
                    while s[i+1] in DIGITS:
                        i = i+1
                    if s[i+1] in ('-',):
                        i = i+1
                elif s[i+1] in ('-',):
                    i = i+1
            elif s[i+1] in ('>',):
                i = i+1
            elif s[i+1] in ('<',):
                i = i+1
                if s[i+1] in ('<', '-'):
                    i = i+1
            append(j, i+1, T_SHELL)
            j = i+1
        elif c in DIGITS:
            # Digits are not word break characters; they must
            # be preceded by a word break character to trigger.
            if i == 0 or (s[i-1] in WORDBREAKCHARS and not char_is_quoted(s, i-1)):
                j = i
                while s[i+1] in DIGITS:
                    i = i+1
                if s[i+1] in ('>',):
                    i = i+1
                    if s[i+1] in ('&',):
                        i = i+1
                        if s[i+1] in DIGITS:
                            while s[i+1] in DIGITS:
                                i = i+1
                            if s[i+1] in ('-',):
                                i = i+1
                    elif s[i+1] in ('>', '|'):
                        i = i+1
                    append(j, i+1, T_SHELL)
                    j = i+1
                elif s[i+1] in ('<',):
                    i = i+1
                    if s[i+1] in ('&',):
                        i = i+1
                        if s[i+1] in DIGITS:
                            while s[i+1] in DIGITS:
                                i = i+1
                            if s[i+1] in ('-',):
                                i = i+1
                        elif s[i+1] in ('-',):
                            i = i+1
                    elif s[i+1] in ('>',):
                        i = i+1
                    append(j, i+1, T_SHELL)
                    j = i+1
        i = i+1

    if end > j:
        append(j, end, T_WORD)
    return tuple(tokens)


def closequote(tokens):
    """If the last token ends with an open quote, close it.
    """
    if tokens:
        last = tokens[-1]
        if last and last.type == T_WORD:
            if last[0] == '"' and last[-1] != '"':
                tokens = tokens[:-1] + (last+'"',)
            elif last[0] == "'" and last[-1] != "'":
                tokens = tokens[:-1] + (last+"'",)
    return tokens


def splitpipe(tokens):
    """Split tokens at the first shell redirect.
    """
    for i, token in enumerate(tokens):
        if token.type == T_SHELL:
            return tokens[:i], tokens[i:]
    return tokens, ()

