import os
import sys


def startidx(s, idx=-1):
    n = len(s)
    if idx < 0:
        idx = n + idx
    i = min(idx, n-1)
    while i >= 0:
        if s[i] == os.sep:
            return i+1
        if s[i] == ' ' and s[max(i-1, 0)] != '\\':
            return i+1
        i -= 1
    return 0


def get_quote_char(s, lx=None):
    if lx is None:
        lx = sys.maxint
    lx = min(len(s)-1, lx)

    dq = s.find('"')
    while dq > 0 and s[dq-1] == '\\' and dq < lx:
        dq = s.find('"', dq+1)
    if dq >= lx:
        dq = -1

    sq = s.find("'")
    while sq > 0 and s[sq-1] == '\\' and sq < lx:
        sq = s.find("'", sq+1)
    if sq >= lx:
        sq = -1

    if dq >= 0 and (sq < 0 or sq > dq):
        return '"'
    if sq >= 0 and (dq < 0 or dq > sq):
        return "'"
    return '\\'


def escape(args):
    if args:
        if '\\ ' in args or '\\"' in args or "'\\''" in args:
            return args
        args = args.replace(' ', '\\ ')
        args = args.replace('"', '\\"')
        args = args.replace("'", "'\\''")
    return args


def unescape(args):
    qc = get_quote_char(args)
    if qc in ('"', "'"):
        return q_unescape(args, qc)
    return bs_unescape(args)


def bs_unescape(args):
    if len(args) > 1:
        args = args.replace('\\ ', ' ')
        args = args.replace('\\"', '"')
        args = args.replace("'\\''", "'")
    return args


def q_unescape(args, quote_char):
    if len(args) > 1:
        if args[-1] == quote_char and args[-2] != '\\':
            args = args[:-1]
        if args[0] == quote_char:
            args = args[1:]
    return bs_unescape(args)


def split(args):
    qc = get_quote_char(args)
    if qc in ('"', "'"):
        return q_split(args, qc)
    return bs_split(args)


def bs_split(args):
    r = []
    i = j = 0
    n = len(args)
    while i < n:
        if args[i] == ' ' and args[max(i-1, 0)] != '\\':
            r.append(args[j:i])
            j = i+1
        i = i+1
    if n:
        r.append(args[j:])
    return tuple(r)


def q_split(args, quote_char):
    r = []
    i = j = 0
    n = len(args)
    q = False
    while i < n:
        if args[i] == quote_char and args[max(i-1, 0)] != '\\':
            q = not q
        if args[i] == ' ' and not q:
            r.append(args[j:i])
            j = i+1
            while args[j] == ' ':
                i = i+1
                j = j+1
        i = i+1
    if n:
        r.append(args[j:])
    return tuple(r)

