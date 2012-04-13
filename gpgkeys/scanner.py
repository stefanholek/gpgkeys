from kmd.completions.quoting import char_is_quoted

WHITESPACE = (' ', '\t', '\n')
QUOTECHARS = ('"', "'")


def find_unquoted(s, lx, chars):
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


def rfind_unquoted(s, lx, chars):
    """Find any one of the characters in chars before lx, starting
    at the end of the string.
    """
    # Doesn't find quote characters
    skip_next = False
    quote_char = ''
    result = -1
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
            result = i
    return result

