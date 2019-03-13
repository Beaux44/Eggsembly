from extras import cprint, ERROR
import ply.lex as lex


nonExistentFileName = ''


# Class that is used to lex Eggsembly
class EggLex(object):
    def __init__(self, **kwargs):
        self.lexer: lex.Lexer = lex.lex(module=self, **kwargs)
        self.lineno: int = self.lexer.lineno

    def __call__(self, data: str):
        self.data: str = data
        self.lexer.input(data)
        line = 0
        toks: List[List[lex.LexToken]] = [[]]
        tok: lex.LexToken = self.lexer.token()
        while tok:
            toks[line] += [tok]
            if tok.type == "NEWLINE":
                line += 1
                toks += [[]]
            tok = self.lexer.token()
        return [*map(tuple, toks)]

    def __str__(self):
        return str(self.code)

    def findColumn(self, t: lex.LexToken) -> int:       # Finds column of given token, used for Syntax Errors
        line_start = self.data.rfind('\n', 0, t.lexpos)
        return (t.lexpos - line_start) - 1

    def t_error(self, t: lex.LexToken) -> None:
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
        'repeat_while': 'REPW',
        'repeat_until': 'REPU',
        'if_true': 'IFT',
        'if_false': 'IFF',
        'const': 'CONST',
        'func': 'FUNCT',
    }

    tokens = ['INT',
              'STR',
              'ID',
              'EQ',
              'DOT',
              'ADDE',
              'SUB',
              'DIV',
              'FDIV',
              'MUL',
              'MOD',
              'POW',
              'COM',
              'FLOAT',
              'LPAREN',
              'LBRACE',
              'LBRACK',
              'RPAREN',
              'RBRACE',
              'RBRACK',
              'NEWLINE',
              ] + [*reserved.values()]

    def t_ignore_COMMENT(self, t: lex.LexToken) -> None:
        r'(//[^\n]*|/\*(?:.|\n)*?(?:\*/|\Z)|~~\[==(?:.|\n)*?(?:==\]~~/|\Z))'

    t_ignore = ' \t'

    literals = "()[]{}.=\\/+-*^"
    t_EQ = r'='
    t_DOT = r'\.'
    t_ADDE = r'\+'
    t_SUB = r'-'
    t_MUL = r'\*'
    t_DIV = r'/'
    t_MOD = r'%'
    t_FDIV = r'\\'
    t_POW = r'\^'
    t_COM = r','
    t_LPAREN = r'\('
    t_LBRACE = r'{'
    t_LBRACK = r'\['
    t_RPAREN = r'\)'
    t_RBRACE = r'}'
    t_RBRACK = r']'

    def t_NEWLINE(self, t: lex.LexToken) -> lex.LexToken:
        r'(?:\r?\n)+'
        t.lexer.lineno += t.value.count("\n")
        self.lineno = t.lexer.lineno
        t.value = t.value.count("\n")
        return t

    def t_FLOAT(self, t: lex.LexToken) -> lex.LexToken:
        r'(?:\d+\.\d*|\d*\.\d+)'
        t.value = float(t.value)
        return t

    def t_INT(self, t: lex.LexToken) -> lex.LexToken:
        r'\b\d+'
        t.value = int(t.value)
        return t

    def t_ID(self, t: lex.LexToken) -> lex.LexToken:
        r'\b([A-Za-z_]\w*)\b'
        t.type = self.reserved.get(t.value, 'ID')
        return t

    t_STR = r'(?P<quote>["\'])(?P<str>(?:(?=(?P<slash>\\?))(?P=slash)[ -~])+?)(?P=quote)'

