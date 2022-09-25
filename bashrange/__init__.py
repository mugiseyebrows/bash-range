from dataclasses import dataclass
from itertools import product
import sys

class Tok:
    (
        undefined,
        open_brace,
        close_brace,
        single_quotes,
        double_quotes,
        comma,
        range,
        value,
    ) = range(8)

@dataclass
class T:
    type: int
    cont: str

class Lexer:
    def __init__(self):
        self.res = []
        self.tok = T(Tok.undefined, "")
    
    def flush(self, t = Tok.undefined, allow_empty = False):
        if t != Tok.undefined:
            self.tok.type = t
        if allow_empty or self.tok.cont != "":
            self.res.append(self.tok)
        self.clear()

    def clear(self):
        self.tok = T(Tok.undefined, "")

    def push(self, c):
        self.tok.cont += c

    def append(self, tok):
        self.res.append(tok)

def lexer(arg):

    # todo escaping

    in_braces = False
    in_single_quotes = False
    in_double_quotes = False
    list_mode = False

    lexer = Lexer()

    def char_at(i, ch):
        if i >= 0 and i < len(arg):
            return arg[i] == ch
        return False

    for i,c in enumerate(arg):

        if in_single_quotes:
            lexer.push(c)
            if c == "'":
                in_single_quotes = False
                lexer.flush()
                
        elif in_double_quotes:
            lexer.push(c)
            if c == '"':
                in_double_quotes = False
                lexer.flush()

        else:

            if c == "{":

                lexer.flush()
                lexer.append(T(Tok.open_brace, "{"))
                in_braces = True

            elif c == "}":

                allow_empty = in_braces and list_mode
                type_ = Tok.value if in_braces else Tok.undefined

                lexer.flush(type_, allow_empty=allow_empty)
                lexer.append(T(Tok.close_brace, "}"))
                in_braces = False
                list_mode = False

            elif c == '"':

                lexer.flush()
                lexer.push(c)
                in_double_quotes = True
                    
            elif c == "'":

                lexer.flush()
                lexer.push(c)
                in_single_quotes = True

            elif c == '.':

                if in_braces and char_at(i+1, ".") and not list_mode:
                    lexer.flush(Tok.value)

                lexer.push(c)
                if lexer.tok.cont == "..":
                    lexer.flush(Tok.range)

            elif c == ',':

                if in_braces:
                    list_mode = True
                    lexer.flush(Tok.value, allow_empty=True)
                    lexer.append(T(Tok.comma, ","))
                else:
                    lexer.push(c)

            else:
                lexer.push(c)

    lexer.flush()

    return lexer.res

def index_of(tokens, t, start = 0):
    for i, tok in enumerate(tokens):
        if i < start:
            continue
        if tok.type == t:
            return i

def unquoted(s):
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s

class ExprStr:
    def __init__(self, tokens, unquote = True):
        if unquote:
            modify = unquoted
        else:
            modify = lambda s: s
        self.cont = "".join([modify(tok.cont) for tok in tokens])
    def __repr__(self) -> str:
        return "ExprStr({})".format(self.cont)
    def eval(self):
        return [self.cont]

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

def parse(tokens_):
    tokens = tokens_[:]
    blocks = []
    while len(tokens):
        ix_open_brace = index_of(tokens, Tok.open_brace)
        ix_close_brace = index_of(tokens, Tok.close_brace)

        if None not in [ix_open_brace, ix_close_brace]:
            # } {
            if ix_close_brace < ix_open_brace:
                ix_close_brace = index_of(tokens, Tok.close_brace, ix_open_brace + 1)

        if None not in [ix_open_brace, ix_close_brace]:
            # { { } 
            for ix in range(ix_open_brace+1, ix_close_brace):
                if tokens[ix].type == Tok.open_brace:
                    ix_open_brace = ix

        if ix_open_brace is None or ix_close_brace is None:
            blocks.append(ExprStr(tokens))
            tokens = []
            break

        if ix_open_brace > 0:
            blocks.append(ExprStr(tokens[0:ix_open_brace]))


        list_mode = False
        for ix in range(ix_open_brace + 1, ix_close_brace):
            if tokens[ix].type == Tok.comma:
                list_mode = True

        if not list_mode:

            ix_value1 = ix_open_brace + 1
            ix_range = ix_open_brace + 2
            ix_value2 = ix_open_brace + 3
            ix_range2 = ix_open_brace + 4
            ix_step = ix_open_brace + 5


            # {value1..value2..step}
            with_step = ix_step + 1 == ix_close_brace
            # {value1..value2}
            without_step = ix_value2 + 1 == ix_close_brace

            ok = False
            if with_step:
                step_str = tokens[ix_step].cont
                ok = tokens[ix_range].type == Tok.range and tokens[ix_range2].type == Tok.range and is_int(step_str)
            elif without_step:
                step_str = "1"
                ok = tokens[ix_range].type == Tok.range
            
            if ok:
                value1 = tokens[ix_value1].cont
                value2 = tokens[ix_value2].cont
                step = abs(int(step_str))
                ok = is_valid_range(value1, value2) and tokens[ix_range].type == Tok.range
                
            if ok:
                blocks.append(ExprRange(value1, value2, step))
            else:
                blocks.append(ExprStr(tokens[ix_open_brace:ix_close_brace+1], unquote=False))

        else:
            # list mode

            ok = True
            ix = ix_open_brace + 1
            values = []
            while True:
                if tokens[ix].type != Tok.value:
                    ok = False
                values.append(tokens[ix].cont)
                ix += 1
                if ix == ix_close_brace:
                    break
                if tokens[ix].type != Tok.comma:
                    ok = False
                ix += 1
                if ix == ix_close_brace:
                    break
            
            if ok:
                blocks.append(ExprList(values))
            else:
                blocks.append(ExprStr(tokens[ix_open_brace:ix_close_brace+1], unquote=False))

            
        tokens = tokens[ix_close_brace+1:]
    return blocks

def evaluate(blocks):
    evaluated = [block.eval() for block in blocks]
    return ["".join(item) for item in product(*evaluated)]
    
def parse_lex_evaluate(arg, debug = False):
    tokens = lexer(arg)
    if debug:
        print("tokens: ", tokens)
    blocks = parse(tokens)
    if debug:
        print("blocks: ", blocks)
    return evaluate(blocks)

def expand_args(args = None, debug = False):
    if args is None:
        args = sys.argv[1:]
    res = []
    for arg in args:
        if "{" not in arg or "}" not in arg :
            res.append(arg)
        else:
            res += parse_lex_evaluate(arg, debug)
    return res
