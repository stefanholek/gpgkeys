import os
import sys

WHITESPACE = (' ', '\t', '\n')
QUOTECHARS = ('"', "'")


def scan_open_quote(s, lx):
    # XXX MB support?
    quote_char = ''
    skip_next = False
    for i in range(lx):
        c = s[i]
        if skip_next:
            skip_next = False
            continue
        if quote_char != "'" and c == '\\':
            skip_next = True
            continue
        if quote_char != '':
            if c == quote_char:
                quote_char = ''
        elif c in QUOTECHARS:
            quote_char = c
    return quote_char


def scan_first_quote(s, lx):
    # XXX MB support?
    skip_next = False
    for i in range(lx):
        c = s[i]
        if skip_next:
            skip_next = False
            continue
        if c == '\\':
            skip_next = True
            continue
        if c in QUOTECHARS:
            return c
    return ''


def scan_unquoted(s, cs, lx):
    # XXX MB support?
    quote_char = ''
    skip_next = False
    for i in range(lx):
        c = s[i]
        if skip_next:
            skip_next = False
            continue
        if quote_char != "'" and c == '\\':
            skip_next = True
            continue
        if quote_char != '':
            if c == quote_char:
                quote_char = ''
        else:
            if c in QUOTECHARS:
                quote_char = c
            elif c in cs:
                return i
    return -1


def split(args):
    qc = scan_first_quote(args, len(args))
    if qc in QUOTECHARS:
        return qc_split(args, qc)
    return bs_split(args, qc)


def qc_split(args, qc):
    r = []
    i = j = 0
    n = len(args)
    q = False
    while i < n:
        if args[i] == qc and args[max(i-1, 0)] != '\\':
            q = not q
        if args[i] in WHITESPACE and not q:
            r.append(args[j:i])
            j = i+1
            while args[j] in WHITESPACE:
                i = i+1
                j = j+1
        i = i+1
    if n:
        r.append(args[j:])
    return tuple(r)


def bs_split(args, qc):
    r = []
    i = j = 0
    n = len(args)
    while i < n:
        if args[i] in WHITESPACE and args[max(i-1, 0)] != '\\':
            r.append(args[j:i])
            j = i+1
        i = i+1
    if n:
        r.append(args[j:])
    return tuple(r)

