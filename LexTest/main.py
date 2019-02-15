import ply.lex  as lex, \
       ply.yacc as yacc
import colorama
from pprint import pprint


"""
    TODO:
        Take OOP too far
        Make it do anything
        Come up with better while notation
        Make blocks work
        
"""


nonExistentFileName = ""

colorama.init()

WARNING = colorama.Fore.LIGHTYELLOW_EX
ERROR = colorama.Fore.LIGHTRED_EX


def cprint(color, *args, **kwargs):
    print(end=color)
    print(*args, **kwargs)
    print(end=(colorama.Fore.RESET + colorama.Back.RESET))


class Command(object):
    def __init__(self, type, ident=None, index=None, value=None):
        self.type = type
        self.ident = ident
        self.index = index
        self.value = value

    def __str__(self):
        return "Command(%r, %r, %r, %r)" % (self.type, self.ident, self.index, self.value)

    __repr__ = __str__


class Block(object):
    def __init__(self, type, code):
        self.type = type
        self.code = code

    def __str__(self):
        return "Block(%r, code)" % self.type

    __repr__ = __str__


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
        'whiletrue': 'WHILET',
        'whilefalse': 'WHILEF',
        'iftrue': 'IFT',
        'ifalse': 'IFF',
    }

    tokens = ['INT',
              'STR',
              'ID',
              'EQ',
              'DOT',
              'LPAREN',
              'LBRACE',
              'LBRACK',
              'RPAREN',
              'RBRACE',
              'RBRACK',
              'NEWLINE',
              ] + [*reserved.values()]

    t_ignore = ' \t'

    literals = "()[]{}.=\\"
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

    def t_ignore_COMMENT(self, t):
        r'(//[^\n]*|/\*(?:.|\n)*?(?:\*/|\Z)|~~\[==(?:.|\n)*?(?:==\]~~/|\Z))'

    def t_ID(self, t):
        r'\b([A-Za-z_][A-Za-z0-9_]*)\b'
        t.type = self.reserved.get(t.value, 'ID')
        return t

    def t_INT(self, t):
        r'\b\d+\b'
        t.value = int(t.value)
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
        cprint(ERROR, "Syntax error on line %d:\n\t%s" % (self.lexer.lineno - 1,
                                                          self.data.splitlines()[self.lexer.lineno - 2]))

    def p_expression_program(self, p):
        """expressions : expressions NEWLINE expression
                       | expression
                       | NEWLINE
        """
        if len(p) == 4:
            p[0] = flatten([p[1], p[3]])
        else:
            p[0] = p[1]

    def p_expression_keyword(self, p):
        """expression : AXE
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

    def p_expression_SETVAR(self, p):
        """expression : ID LBRACK INT RBRACK EQ val
                      | ID EQ val
        """
        if len(p) == 7:
            p[0] = Command("SET", p[1], p[3], p[6])
        else:
            p[0] = Command("SET", p[1], None, p[3])

    def p_expression_GETVAR(self, p):
        """expression : ID LBRACK INT RBRACK
                      | ID
        """
        if len(p) == 5:
            p[0] = Command("GET", p[1], p[3])
        else:
            p[0] = Command("GET", p[1])

    def p_expression_PUSH(self, p):
        """expression : PUSH STR
                      | PUSH INT
        """
        p[0] = Command("PUSH", p[1], None, p[2])

    def p_expression_HATCH(self, p):
        "expression : HATCH function"
        p[0] = Command("HATCH", p[2])

    def p_expression_AS(self, p):
        "expression : ID AS ID"
        p[0] = Command("AS", (p[1], p[3]))

    def p_expression_enter_block_build(self, p):
        "expression : BUILD ID LBRACE"
        p[0] = Command("BUILD", p[2])

    def p_expression_enter_block_whilet(self, p):
        "expression : WHILET LBRACE"
        p[0] = Command("WHILE", "TRUE")

    def p_expression_enter_block_whilef(self, p):
        "expression : WHILEF LBRACE"
        p[0] = Command("WHILE", "FALSE")

    def p_expression_enter_block_ift(self, p):
        "expression : IFT LBRACE"
        p[0] = Command("IF", "TRUE")

    def p_expression_enter_block_iff(self, p):
        "expression : IFF LBRACE"
        p[0] = Command("IF", "FALSE")

    def p_expression_exit_block(self, p):
        "expression : RBRACE"
        p[0] = Command("EXIT")

    def p_FUNCTION(self, p):
        """function : ID DOT function
                    | ID
        """
        p[0] = ''.join(flatten(p[1:]))

    def p_VAL(self, p):
        """val : STR
               | INT
               | TOP
        """
        p[0] = p[1]



lexer = EggLex()
parser = EggParse()

print(*lexer(
    "a as b\n"
    "build blah {\n"
    "\thatch ab.a\n"
    "\ta[2] = '3'\n"
    "\ta\n"
    "\tiftrue {\n"
    "\t\twhilefalse {\n"
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
    "build blah {\n"
    "\thatch ab.a\n"
    "\ta[2] = '3'\n"
    "\ta\n"
    "\tiftrue {\n"
    "\t\twhilefalse {\n"
    "\t\t\tb[3] = Top\n"
    "\t\t}\n"
    "\t}\n"
    "\tb\n"
    "\tpush 3\n"
    "\trooster\n"
    "\ta = Top\n"
    "} // blah", debug=True
))

