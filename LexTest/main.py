import ply.lex  as lex, ply.yacc as yacc
from pprint import pprint

"""
    TODO:
        Take OOP too far
        Make it do anything
        Come up with better while notation
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
        return "Block(%r, code)" % self.type

    def __str__(self):
        if self.type.type == "BUILD":
            return "build " + self.type.ident + " {\n" + '\n'.join(["\t" + str(i) for i in self.code]) + "\n}"
        else:
            return ("%s_%s {\n" % (self.type.type.lower(), self.type.ident.lower())
                    + '\n'.join(["\t" + str(i) for i in self.code]) + "\n}")

    def __iter__(self):
        print(self.code)
        return self.code.__iter__()


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
               ("Syntax Error in file %r on line %d, column %d:\n"
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
        'if_alse': 'IFF',
    }

    tokens = ['INT',
              'STR',
              'ID',
              'EQ',
              'DOT',
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

    literals = "()[]{}.="
    t_EQ = r'='
    t_DOT = r'\.'
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

    def t_ID(self, t):
        r'\b([A-Za-z_][A-Za-z0-9_]*)\b'
        t.type = self.reserved.get(t.value, 'ID')
        return t

    def t_INT(self, t):
        r'\b\d+\b'
        t.value = int(t.value)
        return t

    def t_FLOAT(self, t):
        r'(?:\b\d+\.\d*|\d*\.\d+\b)'
        t.value = float(t.value)
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
        self.lexer = EggLex()
        self.parser = yacc.yacc(module=self, **kwargs)
        self.parser.lineno = 1

    def __call__(self, data, **kwargs):
        self.data = self.lexer.data = data
        return self.parser.parse(self.data, **kwargs)

    tokens = EggLex.tokens

    def p_ignore(self, p):
        " \t"

    def p_error(self, p):
        cprint(ERROR, "Syntax error on line %d:\n\t%s" % (self.lexer.lineno,
                                                          self.data.split("\n")[self.lexer.lineno - 1].strip()))

    def p_expressions_program(self, p):
        """expressions : expressions NEWLINE block
                       | expressions NEWLINE statement
                       | block
                       | statement
                       | NEWLINE
        """
        if len(p) == 4:
            p[0] = flatten([p[1], p[3]])
        else:
            p[0] = p[1]

    def p_enter_block_build(self, p):
        "enter : BUILD ID LBRACE"
        p[0] = Command("BUILD", p[2])

    def p_enter_block_loopt(self, p):
        "enter : LOOPT LBRACE"
        p[0] = Command("LOOP", "TRUE")

    def p_enter_block_loopf(self, p):
        "enter : LOOPF LBRACE"
        p[0] = Command("LOOP", "FALSE")

    def p_enter_block_rept(self, p):
        "enter : REPT LBRACE"
        p[0] = Command("REPEAT", "TRUE")

    def p_enter_block_repf(self, p):
        "enter : REPF LBRACE"
        p[0] = Command("REPEAT", "FALSE")

    def p_enter_block_ift(self, p):
        "enter : IFT LBRACE"
        p[0] = Command("IF", "TRUE")

    def p_enter_block_iff(self, p):
        "enter : IFF LBRACE"
        p[0] = Command("IF", "FALSE")

    def p_expression_block(self, p):
        "block : enter NEWLINE expressions NEWLINE RBRACE"
        p[0] = Block(p[1], p[3])

    def p_statement_keyword(self, p):
        """statement : AXE
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

    def p_statement_HATCH(self, p):
        "statement : HATCH FUNC"
        p[0] = Command("HATCH", p[2])

    def p_statement_PUSH(self, p):
        """statement : PUSH STR
                     | PUSH INT
                     | PUSH FLOAT
        """
        p[0] = Command("PUSH", None, None, p[2])

    def p_statement_AS(self, p):
        "statement : IDSTR AS IDSTR"
        p[0] = Command("AS", (p[1], p[3]))

    def p_statement_SETVAR(self, p):
        """statement : ID LBRACK INT RBRACK EQ VAL
                     | ID EQ VAL
        """
        if len(p) == 7:
            p[0] = Command("SET", p[1], p[3], p[6])
        else:
            p[0] = Command("SET", p[1], None, p[3])

    def p_statement_GETVAR(self, p):
        """statement : ID LBRACK INT RBRACK
                     | ID
        """
        if len(p) == 5:
            p[0] = Command("GET", p[1], p[3])
        else:
            p[0] = Command("GET", p[1])

    def p_FUNCTION(self, p):
        """FUNC : ID DOT FUNC
                | ID
        """
        p[0] = ''.join(flatten(p[1:]))

    def p_VAL(self, p):
        """VAL : STR
               | INT
               | TOP
               | FLOAT
        """
        p[0] = p[1]

    def p_IDSTR(self, p):
        """IDSTR : ID
                 | STR
        """
        p[0] = p[1]

    # def p_OPTNEWLINE(self, p):
    #     """OPTNEWLINE : NEWLINE
    #                   |
    #     """


lexer = EggLex()
parser = EggParse()

print(*lexer(
    "a as b\n"
    "x as y \n"
    "build blah {\n"
    "\thatch ab.a\n"
    "\ta[2] = '3'\n"
    "\ta\n"
    "\tif_true {\n"
    "\t\tloop_false {\n"
    "\t\t\tb[3] = Top\n"
    "\t\t}\n"
    "\t}\n"
    "\tb\n"
    "\tpush 3\n"
    "\trooster\n"
    "\ta = Top\n"
    "} // blah"
), "", sep="\n")

pprint(parser(
    "a as b\n"
    "x as y\n"
    "build blah {\n"
    "\thatch ab.a\n"
    "\ta[2] = '3'\n"
    "\ta\n"
    "\tif_true {\n"
    "\t\tloop_false {\n"
    "\t\t\tb[3] = Top\n"
    "\t\t}\n"
    "\t}\n"
    "\tb\n"
    "\n"
    "\tpush 3\n"
    "\trooster\n"
    "\ta = Top\n"
    "} // blah", debug=0
))
