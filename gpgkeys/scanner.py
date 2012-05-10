QUOTECHARS = ('"', "'")
WHITESPACE = (' ', '\t', '\n')


def char_is_quoted(text, index):
    """Return true if the character at 'index' is quoted.

    Duplicated here to stay independent of readline completer
    configuration.
    """
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
        elif c in QUOTECHARS:
            quote_char = c
    # A closing quote character is never quoted
    if index < len(text) and text[index] == quote_char:
        return False
    return bool(quote_char)


def find_unquoted(text, end, chars):
    """Find any one of the characters in 'chars' before 'end'.

    Does not find quote characters.
    """
    skip_next = False
    quote_char = ''
    for i in range(end):
        c = text[i]
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


def rfind_unquoted(text, end, chars):
    """Find any one of the characters in 'chars' before 'end',
    starting at 'end'.

    Does not find quote characters.
    """
    skip_next = False
    quote_char = ''
    result = -1
    for i in range(end):
        c = text[i]
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

