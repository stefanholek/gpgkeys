WHITESPACE = (' ', '\t', '\n')
QUOTECHARS = ('"', "'")

SHELLCHARS1 = ('>', '<', '|', '&', ';')
SHELLCHARS2 = ('>>', '2>', '>&', '>|', '<&')
SHELLCHARS3 = ('2>>',)

WORDBREAKCHARS = WHITESPACE + QUOTECHARS + SHELLCHARS1
SHELLREDIR = SHELLCHARS1[:3] + SHELLCHARS2 + SHELLCHARS3


def scan_first_quote(s, lx):
    skip_next = False
    for i in range(lx):
        c = s[i]
        if skip_next:
            skip_next = False
        elif c == '\\':
            skip_next = True
        elif c in QUOTECHARS:
            return c
    return ''


def scan_open_quote(s, lx):
    skip_next = False
    quote_char = ''
    for i in range(lx):
        c = s[i]
        if skip_next:
            skip_next = False
        elif quote_char != "'" and c == '\\':
            skip_next = True
        elif quote_char != '':
            if c == quote_char:
                quote_char = ''
        elif c in QUOTECHARS:
            quote_char = c
    return quote_char


def scan_unquoted(s, lx, chars):
    skip_next = False
    quote_char = ''
    for i in range(lx):
        c = s[i]
        if skip_next:
            skip_next = False
        elif quote_char != "'" and c == '\\':
            skip_next = True
        elif quote_char != '':
            if c == quote_char:
                quote_char = ''
        elif c in QUOTECHARS:
            quote_char = c
        elif c in chars:
            return i
    return -1


class InfiniteString(str):
    """A string without IndexErrors."""

    def __getitem__(self, index):
        if index < 0 or index >= len(self):
            return None
        return str.__getitem__(self, index)


def scan_tokens(s):
    """Return a sequence of (start, end) tuples.

    Each tuple represents the start and end indexes
    of a token in the line.
    """
    skip_next = False
    quote_char = ''
    tokens = []
    end = len(s)
    s = InfiniteString(s)
    i = j = 0

    while i < end:
        c = s[i]
        if skip_next:
            skip_next = False
        elif quote_char != "'" and c == '\\':
            skip_next = True
        elif quote_char != '':
            if c == quote_char:
                quote_char = ''
                tokens.append((j, i+1))
                j = i+1
        elif c in QUOTECHARS:
            if i > j:
                tokens.append((j, i))
            j = i
            quote_char = c
        elif c in WHITESPACE:
            if i > j:
                tokens.append((j, i))
                j = i+1
            else:
                j = j+1
        elif c in ('|', '&', ';'):
            if i > j:
                tokens.append((j, i))
            j = i
            tokens.append((j, i+1))
            j = i+1
        elif c == '>':
            if i > j:
                tokens.append((j, i))
            j = i
            if s[i+1] in ('>', '|', '&'):
                i = i+1
            tokens.append((j, i+1))
            j = i+1
        elif c == '<':
            if i > j:
                tokens.append((j, i))
            j = i
            if s[i+1] == '&':
                i = i+1
            tokens.append((j, i+1))
            j = i+1
        elif c == '2':
            # '2' is not a word break character
            if i == 0 or (s[i-1] in WORDBREAKCHARS and s[i-2] != '\\'):
                j = i
                if s[i+1] == '>':
                    i = i+1
                    if s[i+1] == '>':
                        i = i+1
                tokens.append((j, i+1))
                j = i+1
        i = i+1

    if end > j:
        tokens.append((j, end))
    return tuple(tokens)


def split(args):
    return tuple(args[j:i] for (j, i) in scan_tokens(args))

