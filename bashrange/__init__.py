from dataclasses import dataclass
from itertools import product
import sys

def unquoted(s):
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s

def is_int(v):
    try:
        int(v)
        return True
    except ValueError:
        return False

def is_letter(v):
    return len(v) == 1

def is_valid_range(v1, v2):
    i1 = is_int(v1)
    i2 = is_int(v2)
    return (i1 and i2) or (is_letter(v1) and is_letter(v2) and not i1 and not i2)
    
class ExprList:
    def __init__(self, values):
        self.values = values
    def __repr__(self):
        return "ExprList({})".format(",".join(['"{}"'.format(value) for value in self.values]))
    def eval(self):
        return [unquoted(value) for value in self.values]

class ExprRange:
    def __init__(self, value1, value2, step):
        self.value1 = value1
        self.value2 = value2
        self.step = step
    def __repr__(self) -> str:
        return "ExprRange({},{})".format(self.value1, self.value2)
    def eval(self):
        if is_int(self.value1) and is_int(self.value2):
            value1 = int(self.value1)
            value2 = int(self.value2)
            if value1 > value2:
                it = reversed(range(value2,value1+1,self.step))
            else:
                it = range(value1,value2+1,self.step)
            return [str(v) for v in it]
        elif is_letter(self.value1) and is_letter(self.value2):
            value1 = ord(self.value1)
            value2 = ord(self.value2)
            if value1 > value2:
                it = reversed(range(value2,value1+1,self.step))
            else:
                it = range(value1,value2+1,self.step)
            return [chr(v) for v in it]
        else:
            raise ValueError("Invalid {}".format(self))

def parse_and_evaluate(arg, modify, debug = False):

    quote_ranges = []
    double_quotes_ranges = []
    expr_ranges = []

    state_norm, state_quote, state_double_quotes, state_expr = range(4)

    state = state_norm
    pos_quotes = -1
    pos_double_quotes = -1
    pos_expr = -1
    expr_is_valid = True

    for i,c in enumerate(arg):
        if state == state_norm:
            if c == "'":
                pos_quotes = i
                state = state_quote
            elif c == '"':
                pos_double_quotes = i
                state = state_double_quotes
            elif c == '{':
                pos_expr = i
                expr_is_valid = True
                state = state_expr

        elif state == state_quote:
            if c == "'":
                quote_ranges.append((pos_quotes, i))
                state = state_norm

        elif state == state_double_quotes:
            if c == '"':
                double_quotes_ranges.append((pos_double_quotes, i))
                state = state_norm

        elif state == state_expr:
            if c == '{':
                pos_expr = i
                expr_is_valid = True
            elif c == '}':
                if expr_is_valid:
                    expr_ranges.append((pos_expr, i))
                state = state_norm
            elif c in ["'", '"']:
                expr_is_valid = False
    
    evaluated = []

    pos_prev = 0
    for pos_op, pos_cl in expr_ranges:
        if pos_prev < pos_op:
            evaluated.append([modify(arg[pos_prev:pos_op])])
        evaluated.append(evaluate(arg[pos_op+1:pos_cl]))
        pos_prev = pos_cl + 1
    
    pos_op = len(arg)
    if pos_prev < pos_op:
        evaluated.append([modify(arg[pos_prev:pos_op])])

    if debug:
        print("evaluated:", evaluated)
        
    return ["".join(item) for item in product(*evaluated)]

def evaluate(arg):
    if ',' in arg:
        vars = arg.split(',')
        expr = ExprList(vars)
        return expr.eval()
    elif '..' in arg:
        vars = arg.split('..')
        expr = None
        if len(vars) == 2:
            if is_valid_range(vars[0], vars[1]):
                expr = ExprRange(vars[0], vars[1], 1)
        elif len(vars) == 3:
            if is_valid_range(vars[0], vars[1]) and is_int(vars[2]):
                expr = ExprRange(vars[0], vars[1], int(vars[2]))
        if expr:
            return expr.eval()
    return ['{' + arg + '}']

def expand_args(args = None, remove_double_quotes = True, remove_quote = True, debug = False):
    
    if remove_quote and remove_double_quotes:
        modify = lambda s: s.replace('"','').replace("'",'')
    elif remove_double_quotes:
        modify = lambda s: s.replace('"','')
    elif remove_quote:
        modify = lambda s: s.replace('"','')
    else:
        modify = lambda s: s
    
    if args is None:
        args = sys.argv[1:]
    res = []

    for arg in args:
        if "{" not in arg or "}" not in arg :
            res.append(modify(arg))
        else:
            res += parse_and_evaluate(arg, modify, debug)
    return res
