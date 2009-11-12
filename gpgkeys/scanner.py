WHITESPACE = (' ', '\t', '\n')
QUOTECHARS = ('"', "'")


def scan_open_quote(s, lx):
    """Find an open quote character before lx.
    """
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
    """Find any one of the characters in chars before lx.
    """
    # Doesn't find quote characters
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


def rscan_unquoted(s, lx, chars):
    """Find any one of the characters in chars before lx, starting
    at the end of the string.
    """
    # Doesn't find quote characters
    skip_next = False
    quote_char = ''
    results = []
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
            results.append(i)
    if results:
        return results[-1]
    return -1


def char_is_quoted(s, x):
    """Return True if the character at x is quoted.
    """
    skip_next = False
    quote_char = ''
    for i in range(x):
        c = s[i]
        if skip_next:
            skip_next = False
        elif quote_char != "'" and c == '\\':
            skip_next = True
            if i == x-1:
                return True
        elif quote_char != '':
            if c == quote_char:
                quote_char = ''
        elif c in QUOTECHARS:
            quote_char = c
    if x < len(s) and s[x] == quote_char:
        return False
    return bool(quote_char)

