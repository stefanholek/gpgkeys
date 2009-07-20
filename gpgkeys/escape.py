import os


def escape(s):
    if '\\ ' in s:
        return s
    return s.replace(' ', '\\ ')


def unescape(s):
    return s.replace('\\ ', ' ')


def split(args):
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

