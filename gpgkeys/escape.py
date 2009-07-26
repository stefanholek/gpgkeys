import os


def escape(s):
    if '\\ ' in s:
        return s
    return s.replace(' ', '\\ ')


def unescape(s):
    return s.replace('\\ ', ' ')


def split(args):
    lx = len(args)-1

    dq = args.find('"')
    if dq > 0:
        while args[dq-1] == '\\' and dq < lx:
            dq = args.find('"', dq+1)

    sq = args.find("'")
    if sq > 0:
        while args[sq-1] == '\\' and sq < lx:
            sq = args.find("'", sq+1)

    if dq >= 0 and (sq < 0 or sq > dq):
        return q_split(args, '"')
    if sq >= 0 and (dq < 0 or dq > sq):
        return q_split(args, "'")
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

