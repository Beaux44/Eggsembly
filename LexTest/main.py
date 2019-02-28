import ply.lex as lex, ply.yacc as yacc
from pprint import pprint

"""
    TODO:
        Take OOP too far
        Make it do anything
        Come up with better while notation
        Make blocks work
"""

nonExistentFileName = ""

try:
    import colorama

    colorama.init()

    WARNING = colorama.Fore.LIGHTYELLOW_EX
    ERROR = colorama.Fore.LIGHTRED_EX


    def cprint(color, *args, **kwargs):
        print(end=(color))
        print(*args, **kwargs)
        print(end=(colorama.Fore.RESET + colorama.Back.RESET))

except ImportError:
    WARNING = ""
    ERROR = ""


    def cprint(_, *args, **kwargs):
        print(*args, **kwargs)


class Command(object):
    def __init__(self, type, ident=None, index=None, value=None):
        self.type = type
        self.ident = ident
        self.index = index
        self.value = value

    def __repr__(self):
        return "Command(%r, %r, %r, %r)" % (self.type, self.ident, self.index, self.value)

    def __str__(self):
        if self.type in ["GET", "SET"]:
            return (self.ident
                    + ("[%s]" % str(self.index)) * (self.index is not None)
                    + (" = " + str(self.value)) * (self.value is not None))
        if self.type == "PUSH":
            return "%s %s" % (self.type.lower(), self.value)
        if self.type == "HATCH":
            return "%s %s" % (self.type.lower(), self.ident)
        if self.type in ["IF", "WHILE", "LOOP"]:
            return "%s_%s" % (self.type.lower(), self.ident.lower())
        return self.type.lower()

    def __iter__(self):
        yield self


class Block(object):
    def __init__(self, type, code):
        self.type: Command = type
        self.code: list = code

    def __repr__(self):
        return "Block(%r, code)" % (self.type,)

    def __str__(self):
        if self.type.type == "BUILD":
            return "build " + self.type.ident + " {\n" + '\n'.join(["\t" + str(i) for i in self.code]) + "\n}"
        else:
            return ("%s_%s {\n" % (self.type.type.lower(), self.type.ident.lower())
                    + '\n'.join(["\t" + str(i) for i in self.code]) + "\n}")

    def __iter__(self):
        print(self.code)
        return self.code.__iter__()


class Const(object):
    def __init__(self, ID, VAL):
        self.ID = ID
        self.VAL = VAL


class EggLex(object):
    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)
        self.lineno = self.lexer.lineno

    def __call__(self, data):
        self.data = data
        self.lexer.input(data)
        line = 0
        toks = [[]]
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            if tok.type == "NEWLINE":
                toks[line] += [tok]
                line += 1
                toks += [[]]
            else:
                toks[line] += [tok]
        return [*map(tuple, toks)]

    def findColumn(self, token):
        line_start = self.data.rfind('\n', 0, token.lexpos)
        return (token.lexpos - line_start) - 1

    def t_error(self, t):
        cprint(ERROR,
               ("Invalid symbol in file %r on line %d, column %d:\n"
                "\t%s\n\t") % (nonExistentFileName,
                               t.lexer.lineno,
                               self.findColumn(t),
                               self.data.split("\n")[t.lexer.lineno - 1])
               + ' ' * (self.findColumn(t) - 1) + "^")  # .center(len(t.value.split('\n')[0]), "~"))
        exit(0)

    reserved = {
        'axe': 'AXE',
        'chicken': 'CHICKEN',
        'add': 'ADD',
        'fox': 'FOX',
        'rooster': 'ROOSTER',
        'compare': 'COMPARE',
        'pick': 'PICK',
        'peck': 'PECK',
        'fr': 'FR',
        'bbq': 'BBQ',
        'as': 'AS',
        'push': 'PUSH',
        'hatch': 'HATCH',
        'build': 'BUILD',
        'Top': 'TOP',
        'loop_true': 'LOOPT',
        'loop_false': 'LOOPF',
        'repeat_true': 'REPT',
        'repeat_false': 'REPF',
        'if_true': 'IFT',
        'if_false': 'IFF',
        'const': 'CONST',
    }

    tokens = ['INT',
              'STR',
              'ID',
              'EQ',
              'DOT',
              'ADDE',
              'SUB',
              'DIV',
              'MUL',
              'POW',
              'FLOAT',
              'LPAREN',
              'LBRACE',
              'LBRACK',
              'RPAREN',
              'RBRACE',
              'RBRACK',
              'NEWLINE',
              ] + [*reserved.values()]

    def t_ignore_COMMENT(self, t):
        r'(//[^\n]*|/\*(?:.|\n)*?(?:\*/|\Z)|~~\[==(?:.|\n)*?(?:==\]~~/|\Z))'

    t_ignore = ' \t'

    literals = "()[]{}.=/+-*^"
    t_EQ = r'='
    t_DOT = r'\.'
    t_ADD = r'\+'
    t_SUB = r'-'
    t_MUL = r'\*'
    t_DIV = r'/'
    t_POW = r'\^'
    t_LPAREN = r'\('
    t_LBRACE = r'{'
    t_LBRACK = r'\['
    t_RPAREN = r'\)'
    t_RBRACE = r'}'
    t_RBRACK = r']'


    def t_NEWLINE(self, t):
        r'(?:\r?\n)+'
        t.lexer.lineno += t.value.count("\n")
        self.lineno = t.lexer.lineno
        t.value = t.value.count("\n")
        return t

    def t_FLOAT(self, t):
        r'(?:\d+\.\d*|\d*\.\d+)'
        t.value = float(t.value)
        return t

    def t_INT(self, t):
        r'\b\d+'
        t.value = int(t.value)
        return t

    def t_ID(self, t):
        r'\b([A-Za-z_]\w*)\b'
        t.type = self.reserved.get(t.value, 'ID')
        return t

    t_STR = r'(?P<quote>["\'])(?P<str>(?:(?=(?P<slash>\\?))(?P=slash)[ -~])+?)(?P=quote)'


def flatten(a: list) -> list:
    b = []
    for i in a:
        if i is not None:
            if isinstance(i, list):
                b += flatten(i)
            else:
                b += [i]
    return b


class EggParse(object):
    def __init__(self, **kwargs):
        self.vars = {}
        self.funcs = {}
        self.consts = {}
        self.lexer = EggLex()
        self.parser = yacc.yacc(module=self, **kwargs)
        self.parser.lineno = 1

    def __call__(self, data, **kwargs):
        self.data = self.lexer.data = data
        return self.parser.parse(self.data, lexer=self.lexer.lexer, **kwargs)

    tokens = EggLex.tokens

    precedence = (
        ('nonassoc', 'EQ'),
        ('left', 'ADDE', 'SUB'),
        ('left', 'MUL', 'DIV'),
        # ('right', 'IMPMUL'),
        ('right', 'NEG', 'POS'),
        ('right', 'POW')
    )

    def p_ignore(self, p):
        " \t"

    def p_error(self, p):
        cprint(ERROR, "Syntax error on line %d:\n\t%s" % (self.lexer.lineno,
                                                          self.data.split("\n")[self.lexer.lineno - 1].strip()))

    def p_program(self, p):
        """expressions : expressions NEWLINE block
                       | expressions NEWLINE stmt
                       | block
                       | stmt
        """
        if len(p) == 4:
            p[0] = flatten([p[1], p[3]])
        else:
            p[0] = p[1]

    def p_enter_block_build(self, p):
        "enter : BUILD FUNC LBRACE"
        p[0] = ("BUILD", p[2])

    def p_enter_block_loopt(self, p):
        "enter : LOOPT LBRACE"
        p[0] = ("LOOP", "TRUE")

    def p_enter_block_loopf(self, p):
        "enter : LOOPF LBRACE"
        p[0] = ("LOOP", "FALSE")

    def p_enter_block_rept(self, p):
        "enter : REPT LBRACE"
        p[0] = ("REPEAT", "TRUE")

    def p_enter_block_repf(self, p):
        "enter : REPF LBRACE"
        p[0] = ("REPEAT", "FALSE")

    def p_enter_block_ift(self, p):
        "enter : IFT LBRACE"
        p[0] = ("IF", "TRUE")

    def p_enter_block_iff(self, p):
        "enter : IFF LBRACE"
        p[0] = ("IF", "FALSE")

    def p_block(self, p):
        """block : enter NEWLINE expressions NEWLINE RBRACE"""
        p[0] = Block(p[1], p[3])

    def p_stmt_keyword(self, p):
        """stmt : AXE
                | CHICKEN
                | ADD
                | FOX
                | ROOSTER
                | COMPARE
                | PICK
                | PECK
                | FR
                | BBQ
        """
        p[0] = Command(p[1].upper())

    def p_stmt_HATCH(self, p):
        "stmt : HATCH FUNC"
        p[0] = Command("HATCH", p[2])

    def p_stmt_PUSH(self, p):
        """stmt : PUSH STR
                | PUSH mathexpr
        """
        p[0] = Command("PUSH", None, None, p[2])

    def p_stmt_AS(self, p):
        "stmt : IDSTR AS IDSTR"
        p[0] = Command("AS", (p[1], p[3]))

    def p_stmt_SETVAR(self, p):
        """stmt : ID LBRACK INT RBRACK EQ VAL
                | ID EQ VAL
        """
        if len(p) == 7:
            p[0] = Command("SET", p[1], p[3], p[6])
        else:
            p[0] = Command("SET", p[1], None, p[3])

    def p_stmt_GETVAR(self, p):
        """stmt : ID LBRACK INT RBRACK
                | ID
        """
        if len(p) == 5:
            p[0] = Command("GET", p[1], p[3])
        else:
            p[0] = Command("GET", p[1])

    def p_stmt_SETCONST(self, p):
        """stmt : CONST ID EQ VAL"""
        self.consts[p[2]] = p[4]

    def p_stmt_BLANKLINE(self, p):
        "stmt : "

    def p_expr_MUL(self, p):
        """mathexpr : mathexpr MUL mathexpr"""
        p[0] = p[1] * p[3]

    # def p_expr_IMPMUL(self, p):
    #     """mathexpr : mathexpr LPAREN mathexpr RPAREN %prec IMPMUL"""
    #     p[0] = p[1] * p[3]

    def p_expr_DIV(self, p):
        """mathexpr : mathexpr DIV mathexpr"""
        if isinstance(p[1], float) or isinstance(p[3], float):
            p[0] = p[1] / p[3]
        else:
            p[0] = p[1] // p[3]
    
    def p_expr_ADDE(self, p):
        """mathexpr : mathexpr ADDE mathexpr"""
        p[0] = p[1] + p[3]

    def p_expr_SUB(self, p):
        """mathexpr : mathexpr SUB mathexpr"""
        p[0] = p[1] - p[3]
    
    def p_expr_POW(self, p):
        """mathexpr : mathexpr POW mathexpr"""
        p[0] = p[1]**p[3]

    def p_expr_PARENMATH(self, p):
        """mathexpr : LPAREN mathexpr RPAREN"""
        p[0] = p[2]

    def p_expr_NEG(self, p):
        """mathexpr : SUB mathexpr %prec NEG"""
        p[0] = -p[2]

    def p_expr_POS(self, p):
        """mathexpr : ADDE mathexpr %prec POS"""
        p[0] = p[2]

    def p_expr_MATH(self, p):
        """mathexpr : INT
                    | FLOAT
        """
        p[0] = p[1]

    def p_expr_MATHVAR(self, p):
        """mathexpr : ID"""
        p[0] = self.consts[p[1]]


    def p_FUNCTION(self, p):
        """FUNC : ID DOT FUNC
                | ID
        """
        p[0] = ''.join(flatten(p[1:]))

    def p_VAL(self, p):
        """VAL : STR
               | TOP
               | mathexpr
        """
        p[0] = p[1]

    def p_IDSTR(self, p):
        """IDSTR : ID
                 | STR
        """
        p[0] = p[1]


lexer = EggLex()
parser = EggParse()

from time import time_ns
start = time_ns()
print(*map(lambda a: f"Line {a[0]}: {a[1]}", enumerate(lexer(
    "const foo = 2^4 / 4\n"
    "const bar = 3\n"
    "push -foo^bar\n"
    "push foo\n"
    "push ((2-1)^bar)^foo\n"
    "push foo*bar*foo^2\n"
    "push bar*foo*bar*foo\n"
    "a as b\n"
    "x as y\n"
    "baz = foo*bar/2.0^2\n"
    "build qux {\n"
    "   hatch ab.a\n"
    "   a[2] = '3'\n"
    "   a\n"
    "   if_true {\n"
    "       loop_false {\n"
    "           b = Top\n"
    "       }\n"
    "   }\n"
    "   b\n"
    "\n"
    "   push foo\n"
    "   rooster\n"
    "   a = Top\n"
    "} // blah\n"
    "if_false {\n"
    "   push bar\n"
    "}\n"
    "if_true {\n"
    "   push foo\n"
    "}\n"
    "loop_true {\n"
    "   push 2\n"
    "}\n"
    "loop_false {\n"
    "   push 1\n"
    "}\n"
    "repeat_true {\n"
    "   push 0\n"
    "}\n"
    "repeat_false {\n"
    "   push -1\n"
    "}\n"
    "\n"
), 1)), sep="\n")
end = time_ns()
print("\nTook", (end - start) / 10**6, "milliseconds\n\n")

start = time_ns()
pprint(parser(
    "const foo = 2^4 / 4\n"
    "const bar = 3\n"
    "push -foo^bar\n"
    "push foo\n"
    "push ((2-1)^bar)^foo\n"
    "push foo*bar*foo^2\n"
    "push bar*foo*bar*foo\n"
    "a as b\n"
    "x as y\n"
    "baz = foo*bar/2.0^2\n"
    "build qux {\n"
    "   hatch ab.a\n"
    "   a[2] = '3'\n"
    "   a\n"
    "   if_true {\n"
    "       loop_false {\n"
    "           b = Top\n"
    "       }\n"
    "   }\n"
    "   b\n"
    "\n"
    "   push foo\n"
    "   rooster\n"
    "   a = Top\n"
    "} // blah\n"
    "if_false {\n"
    "   push bar\n"
    "}\n"
    "if_true {\n"
    "   push foo\n"
    "}\n"
    "loop_true {\n"
    "   push 2\n"
    "}\n"
    "loop_false {\n"
    "   push 1\n"
    "}\n"
    "repeat_true {\n"
    "   push 0\n"
    "}\n"
    "repeat_false {\n"
    "   push -1\n"
    "}\n"
    "\n", debug=0
))  # -->
#        [Command('PUSH', None, None, -64),
#         Command('PUSH', None, None, 4),
#         Command('PUSH', None, None, 1),
#         Command('PUSH', None, None, 192),
#         Command('PUSH', None, None, 144),
#         Command('AS', ('a', 'b'), None, None),
#         Command('AS', ('x', 'y'), None, None),
#         Command('SET', 'baz', None, 3.0),
#         Block(('BUILD', 'qux'), code),
#         Block(('IF', 'FALSE'), code),
#         Block(('IF', 'TRUE'), code),
#         Block(('LOOP', 'TRUE'), code),
#         Block(('LOOP', 'FALSE'), code),
#         Block(('REPEAT', 'TRUE'), code),
#         Block(('REPEAT', 'FALSE'), code)]

end = time_ns()
print("\nTook", (end - start) / 10**6, "milliseconds")
