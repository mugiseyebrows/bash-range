import re
import itertools
import sys

def split_arg(arg):
    gs = []
    op = -1
    for i, c in enumerate(arg):
        if c == '{':
            op = i
        elif c == '}':
            if op > -1:
                gs.append((op, i))
            op = -1
    res = []
    prev = 0
    for op, cl in gs:
        res.append(arg[prev:op])
        res.append(arg[op:cl+1])
        prev = cl+1
    res.append(arg[prev:])
    return res

def digits_range(i1, i2, inc):
    if i1 > i2:
        return [str(e) for e in reversed(range(i2, i1+1, inc))]
    else:
        return [str(e) for e in range(i1, i2+1, inc)]

def letters_range(o1, o2, inc):
    if o1 > o2:
        return [chr(e) for e in reversed(range(o2, o1+1, inc))]
    else:
        return [chr(e) for e in range(o1, o2+1, inc)]

def is_lower(c):
    return c == c.lower()

def expand_group(grp):
    if grp == '':
        return [grp]
    digits = None
    letters = None
    m = re.match('^[{]([0-9]+)\\.\\.([0-9]+)\\.\\.([0-9]+)[}]$', grp)
    if m:
        return digits_range(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.match('^[{]([0-9]+)\\.\\.([0-9]+)[}]$', grp)
    if m:
        return digits_range(int(m.group(1)), int(m.group(2)), 1)
    m = re.match('^[{]([a-z])\\.\\.([a-z])\\.\\.([0-9]+)[}]$', grp, re.IGNORECASE)
    if m:
        c1 = m.group(1)
        c2 = m.group(2)
        inc = int(m.group(3))
        if is_lower(c1) == is_lower(c2):
            return letters_range(ord(c1), ord(c2), inc)
    m = re.match('^[{]([a-z])\\.\\.([a-z])[}]$', grp, re.IGNORECASE)
    if m:
        c1 = m.group(1)
        c2 = m.group(2)
        inc = 1
        if is_lower(c1) == is_lower(c2):
            return letters_range(ord(c1), ord(c2), inc)
    if ',' in grp and ' ' not in grp and grp.startswith('{') and grp.endswith('}'):
        return grp[1:-1].split(',')
    return [grp]

def has_expanded_groups(groups):
    for group in groups:
        if len(group) > 1:
            return True
    return False

def unquote(s):
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    if s.startswith("'") and s.endswith("'"):
        return s[1:-1]
    return s

def unquote_group(group):
    if len(group) == 1:
        return [unquote(e) for e in group]
    return group

def expand_arg(arg):
    groups = [expand_group(e) for e in split_arg(arg)]
    if has_expanded_groups(groups):
        groups = [unquote_group(group) for group in groups]
        res = []
        for cmb in itertools.product(*groups):
            res.append("".join(cmb))
        return res
    return [arg]

def expand_args(args = None):
    if args is None:
        args = sys.argv[1:]
    res = []
    for arg in args:
        res += expand_arg(arg)
    return res