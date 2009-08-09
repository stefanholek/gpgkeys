import os
import sys


def scan_unquoted(s, c, x, lx):
    q = s.find(c, x)
    while q > 0 and s[q-1] == '\\' and q < lx:
        q = s.find(c, q+1)
    if q >= lx:
        q = -1
    return q


def scan_open(s, c, x, lx):
    q = scan_unquoted(s, c, x, lx)
    if q >= 0:
        qq = scan_unquoted(s, c, q+1, lx)
        if qq > q:
            # This quote is closed, continue
            return scan_open(s, c, qq+1, lx)
    return q


def get_quote_char(s, lx=-1, any=False):
    if lx < 0:
        lx = sys.maxint
    lx = min(len(s), lx)

    if any:
        dq = scan_unquoted(s, '"', 0, lx)
        sq = scan_unquoted(s, "'", 0, lx)
    else:
        dq = scan_open(s, '"', 0, lx)
        sq = scan_open(s, "'", 0, lx)

    if dq >= 0 and (sq < 0 or sq > dq):
        qc = '"'
    elif sq >= 0 and (dq < 0 or dq > sq):
        qc = "'"
    else:
        qc = '\\'

    return qc


def escape(args):
    if args:
        qc = get_quote_char(args)
        if '\\ ' in args or '\\"' in args or "'\\''" in args:
            return args
        if qc != "'":
            if '\\\\' in args:
                return args
            args = args.replace('\\', '\\\\')
        args = args.replace(' ', '\\ ')
        args = args.replace('"', '\\"')
        args = args.replace("'", "'\\''")
    return args


def unescape(args):
    qc = get_quote_char(args)
    if qc in ('"', "'"):
        return qc_unescape(args, qc)
    return bs_unescape(args, qc)


def qc_unescape(args, qc):
    if len(args) > 1:
        if args[-1] == qc and args[-2] != '\\':
            args = args[:-1]
        if args[0] == qc:
            args = args[1:]
    return bs_unescape(args, qc)


def bs_unescape(args, qc):
    if len(args) > 1:
        if qc != "'":
            args = args.replace('\\\\', '\\')
        args = args.replace('\\ ', ' ')
        args = args.replace('\\"', '"')
        args = args.replace("'\\''", "'")
    return args


def split(args):
    qc = get_quote_char(args, any=True)
    if qc in ('"', "'"):
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


def bs_split(args, qc):
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

