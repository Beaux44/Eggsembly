import ply.lex as lex, ply.yacc as yacc, re
from pprint import pprint
from typing import Union, List, Dict, Tuple, Callable
from extras import symbolCodes


# This is likely to be rather slow due to the instantiation of a parser, but ideally it's only called a few times in a
# program. I could try making the symbolCodes the pure chicken constants to speed it up, but that would be quite a
# little hassle to accomplish, so I won't do it for a while. Not until this proves infeasible.
def chickenifyStr(string: str):
    string = eval(string)
    eggs = ""
    parser = EggParse()
    for x, i in enumerate(string):
        eggs += symbolCodes.get(i, "")
        if x > 0:
            eggs += "add\n"
    parser(eggs)
    return str(parser)

escapedChars = re.compile(r"\\(.)")
nonExistentFileName = ""

# Import colorama if it exists, otherwise make cprint equivalent to print
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

baseCommands = {'AXE':     '',
                'CHICKEN': 'chicken',
                'ADD':     'chicken chicken',
                'FOX':     'chicken chicken chicken',
                'ROOSTER': 'chicken chicken chicken chicken',
                'COMPARE': 'chicken chicken chicken chicken chicken',
                'PICK':    'chicken chicken chicken chicken chicken chicken',
                'PECK':    'chicken chicken chicken chicken chicken chicken chicken',
                'FR':      'chicken chicken chicken chicken chicken chicken chicken chicken',
                'BBQ':     'chicken chicken chicken chicken chicken chicken chicken chicken chicken'}


class ConstChangedError(Exception):
    """Used when there is an attempt to redefine a defined constant"""


"""
# Compiled PLY BNF rules

expressions : expressions NEWLINE block
            | expressions NEWLINE stmt
            | block
            | stmt

enter : BUILD FUNC LBRACE
      | LOOPT      LBRACE
      | LOOPF      LBRACE
      | REPW       LBRACE
      | REPU       LBRACE
      | IFT        LBRACE
      | IFF        LBRACE

block : enter NEWLINE expressions NEWLINE RBRACE

keyword : AXE
        | CHICKEN
        | ADD
        | FOX
        | ROOSTER
        | COMPARE
        | PICK
        | PECK
        | FR
        | BBQ

stmt : keyword
     | PICK INT
     | PECK INT
     | HATCH FUNC
     | PUSH STR
     | PUSH mathexpr
     | IDSTR AS IDSTR
     | ID LBRACK INT RBRACK EQ VAL
     | ID EQ VAL
     | ID LBRACK INT RBRACK
     | ID
     | CONST ID EQ CONSTVAL
     | 

IDSTR : ID
      | STR

FUNC : ID DOT FUNC
     | ID

VAL : TOP
    | CONSTVAL

CONSTVAL : STR
         | mathexpr

mathexpr : mathexpr ADDE mathexpr
         | mathexpr SUB  mathexpr
         | mathexpr MUL  mathexpr
         | mathexpr DIV  mathexpr
         | mathexpr FDIV mathexpr
         | mathexpr MOD  mathexpr
         | mathexpr POW  mathexpr
         | LPAREN mathexpr RPAREN
         | mathexpr LPAREN mathexpr RPAREN
         | ID
         | INT
         | FLOAT

"""


# Used to simplify Chicken compilation
class Command(object):
    def __init__(self, type, ident=None, index=None, val=None):
        self.type: str = type
        self.ident: str = ident
        self.index: int = index
        self.value: Union[str, float, int] = val
        self.code = None

    def __repr__(self):
        return "Command(%r, %r, %r, %r)" % (self.type, self.ident, self.index, self.value)

    def __str__(self) -> str:    # Compiles command object to equivalent Chicken code
        if self.code is not None:
            return self.code.__iter__()
        if self.type in baseCommands:
            return baseCommands[self.type]
        if self.type == "PUSH":
            if isinstance(self.value, int):
                chicken = ("chicken " * (10 + abs(self.value))).strip()
                if self.value < 0:
                    chicken = ("chicken chicken chicken chicken chicken chicken chicken chicken chicken chicken\n"
                               "%s\n"
                               "chicken chicken chicken") % chicken
            elif isinstance(self.value, float):
                chicken = chickenifyStr('"' + str(self.value) + '"')
                chicken += ("chicken chicken chicken chicken chicken chicken chicken chicken chicken chicken\n"
                            "chicken chicken chicken")
            else:
                chicken = chickenifyStr(self.value)

            return chicken
        # if self.type == "SET":

    def __iter__(self):
        yield self


# Contains a number of Commands
class Block(object):
    def __init__(self, sort: Tuple[str, str], code: List[Command]):
        self.type = sort
        self.code = code

    def __repr__(self):
        return "Block(%r, code)" % (self.type,)

    def __str__(self):  # Compiles all contained Commands and self to equivalent Chicken
        chicken = ""
        for i in self:
            chicken += str(i)
        chicken = chicken.split("\n")
        if self.type[0] == "IF":
            if self.type[1] == "TRUE":
                chicken = [str(Command("PUSH", val=0)),
                           str(Command("COMPARE")),
                           str(Command("PUSH", val=len(chicken))),
                           str(Command("FR")),
                           *chicken]
            else:
                chicken = [str(Command("PUSH", val=len(chicken))),
                           str(Command("FR")),
                           *chicken]
        elif self.type[0] == "LOOP":
            if self.type[1] == "TRUE":
                chicken = [str(Command("PUSH", val=0)),
                           str(Command("COMPARE")),
                           str(Command("PUSH", val=len(chicken) + 4)),
                           str(Command("FR")),
                           *chicken,
                           str(Command("PUSH", val=1)),
                           str(Command("PUSH", val=0)),
                           str(Command("PUSH", val=len(chicken) + 7)),
                           str(Command("FOX")),
                           str(Command("FR"))]
            else:
                chicken = [str(Command("PUSH", val=len(chicken) + 4)),
                           str(Command("FR")),
                           *chicken,
                           str(Command("PUSH", val=1)),
                           str(Command("PUSH", val=0)),
                           str(Command("PUSH", val=len(chicken) + 5)),
                           str(Command("FOX")),
                           str(Command("FR"))]
        elif self.type[0] == "REPEAT":
            if self.type[1] == "TRUE":
                chicken = [*chicken,
                           str(Command("PUSH", val=0)),
                           str(Command("PUSH", val=len(chicken) + 1)),
                           str(Command("FR"))]
            else:
                chicken = [*chicken,
                           str(Command("PUSH", val=0)),
                           str(Command("COMPARE")),
                           str(Command("PUSH", val=0)),
                           str(Command("PUSH", val=len(chicken) + 1)),
                           str(Command("FR"))]

        return '\n'.join(chicken)

    def __iter__(self):
        yield self.code.__iter__()


class ChickenCode(object):
    def __init__(self):
        self.code = []

    def __iadd__(self, line: Union[Block, Command]) -> None:
        """Converts given Command and Block objects into Chicken and adds it to the code"""
        self.code.extend(line)

    def __str__(self):
        """Returns Chicken program"""
        return '\n'.join(map(str, self.code))

    def __iter__(self):
        return self.code.__iter__()


def flatten(a: list) -> list:
    b = []
    for i in a:
        if i is not None:
            if isinstance(i, list):
                b += flatten(i)
            else:
                b += [i]
    return b


floatOrInt = Union[float, int]
floatIntOrString = Union[floatOrInt, str]


class EggParse(object):
    def __init__(self, **kwargs):
        self.vars: Dict[str, Union[int, float, str]] = {}
        self.funcs: Dict[str, Block] = {}
        self.mfuncs: Dict[str, Callable[[floatOrInt, ...], floatOrInt]] = {}
        self.consts: Dict[str, floatIntOrString] = {}

        self.lexer = EggLex()
        self.parser: yacc.LRParser = yacc.yacc(module=self, debug=False, write_tables=False, **kwargs)
        self.parser.lineno = 1
        self.code = ChickenCode()

    # Takes Eggsembly program string as data argument, parses and returns it
    def __call__(self, data: str, **kwargs) -> List[Union[Command, Block]]:
        self.data = self.lexer.data = data
        return self.parser.parse(self.data, lexer=self.lexer.lexer, **kwargs)

    def __str__(self):        # This is what *actually* compiles an Eggsembly program, used after calling the object
        return str(self.code)

    tokens = EggLex.tokens

    precedence = (
        ('right', 'EQ'),
        ('left', 'ADDE', 'SUB'),
        ('left', 'MUL', 'DIV', 'FDIV', 'MOD'),
        ('left', 'LPAREN'),
        ('right', 'NEG', 'POS'),
        ('right', 'POW')
    )

    def p_ignore(self, p):
        """ \t"""

    def p_error(self, p):
        cprint(ERROR, "Syntax error on line %d:\n\t%s" % (self.lexer.lineno,
                                                          self.data.split("\n")[self.lexer.lineno - 1].strip()))

    # The main syntax of the language,
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
        """enter : BUILD FUNC LBRACE"""
        p[0] = ("BUILD", p[2])

    def p_enter_block_loopt(self, p):
        """enter : LOOPT LBRACE"""
        p[0] = ("LOOP", "TRUE")

    def p_enter_block_loopf(self, p):
        """enter : LOOPF LBRACE"""
        p[0] = ("LOOP", "FALSE")

    def p_enter_block_rept(self, p):
        """enter : REPW LBRACE"""
        p[0] = ("REPEAT", "TRUE")

    def p_enter_block_repf(self, p):
        """enter : REPU LBRACE"""
        p[0] = ("REPEAT", "FALSE")

    def p_enter_block_ift(self, p):
        """enter : IFT LBRACE"""
        p[0] = ("IF", "TRUE")

    def p_enter_block_iff(self, p):
        """enter : IFF LBRACE"""
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
        # self.code += p[0]

    def p_stmt_pick(self, p):
        """stmt : PICK INT"""
        p[0] = [Command("PUSH", None, None, p[2]), Command("PICK")]
        # self.code += p[0]

    def p_stmt_peck(self, p):
        """stmt : PECK INT"""
        p[0] = [Command("PUSH", None, None, p[2]), Command("PECK")]
        # self.code += p[0]

    def p_stmt_HATCH(self, p):
        """stmt : HATCH FUNC"""
        p[0] = Command("HATCH", p[2])

    def p_stmt_PUSH(self, p):
        """stmt : PUSH STR
                | PUSH mathexpr
        """
        p[0] = Command("PUSH", None, None, p[2])
        # self.code += p[0]

    def p_stmt_AS(self, p):
        """stmt : IDSTR AS IDSTR"""
        p[0] = Command("AS", (p[1], p[3]))
        # self.code += p[0]

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
        """stmt : CONST ID EQ CONSTVAL"""
        if p[2] not in self.consts:
            self.consts[p[2]] = p[4]
        else:
            raise ConstChangedError("Constant %r redefined" % p[2])

    # def p_stmt_SETFUNCT(self, p):
    #     """stmt : FUNCT ID EQ CONSTVAL"""


    def p_stmt_BLANKLINE(self, p):
        """stmt : """

    def p_expr_MUL(self, p):
        """mathexpr : mathexpr MUL mathexpr"""
        p[0] = p[1] * p[3]

    def p_expr_IMPMUL(self, p):
        """mathexpr : mathexpr LPAREN mathexpr RPAREN"""
        p[0] = p[1] * p[3]

    def p_expr_DIV(self, p):
        """mathexpr : mathexpr DIV mathexpr"""
        p[0] = p[1] / p[3]

    def p_expr_MOD(self, p):
        """mathexpr : mathexpr MOD mathexpr"""
        p[0] = p[1] % p[3]

    def p_expr_FDIV(self, p):
        """mathexpr : mathexpr FDIV mathexpr"""
        p[0] = p[1] // p[3]

    def p_expr_ADDE(self, p):
        """mathexpr : mathexpr ADDE mathexpr"""
        p[0] = p[1] + p[3]

    def p_expr_SUB(self, p):
        """mathexpr : mathexpr SUB mathexpr"""
        p[0] = p[1] - p[3]

    def p_expr_POW(self, p):
        """mathexpr : mathexpr POW mathexpr"""
        p[0] = p[1] ** p[3]

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

    def p_expr_ID(self, p):
        """mathexpr : ID"""
        p[0] = self.consts[p[1]]

    def p_FUNCTION(self, p):
        """FUNC : ID DOT FUNC
                | ID
        """
        p[0] = ''.join(flatten(p[1:]))

    def p_VAL(self, p):
        """VAL : TOP
               | CONSTVAL
        """
        p[0] = p[1]

    def p_CONSTVAL(self, p):
        """CONSTVAL : STR
                    | mathexpr
        """
        p[0] = p[1]

    def p_IDSTR(self, p):
        """IDSTR : ID
                 | STR
        """
        p[0] = p[1]

    # def p_TUPLE(self, p):
    #     """TUPLE : TUPLE COM mathexpr
    #              | mathexpr
    #     """
    #     if len(p) == 4:
    #         p[0] = (*p[1], p[3])
    #     else:
    #         p[0] = (p[1],)




lexer = EggLex()
parser = EggParse()

from time import time_ns
blah = open('blah.eggs', 'r').read()

start = time_ns()
lexed = lexer(blah)
end = time_ns()
print(*map(lambda a: f"Line {a[0]}: {a[1]}", enumerate(lexed, 1)), sep="\n")
print("\nTook", (end - start) / 10 ** 6, "milliseconds\n\n")

start = time_ns()

# Parses the show Eggsembly program and assigns it to parsed
parsed = parser(blah, debug=0)  # -->
#         [Command('PUSH', None, None, -64.0),
#          Command('PUSH', None, None, 4.0),
#          Command('PUSH', None, None, -6),
#          Command('PUSH', None, None, 1.0),
#          Command('PUSH', None, None, 192.0),
#          Command('PUSH', None, None, 144.0),
#          Command('PUSH', None, None, 144.0),
#          Command('PUSH', None, None, "'3'"),
#          Command('AS', ('a', 'b'), None, None),
#          Command('AS', ('x', 'y'), None, None),
#          Command('AXE', None, None, None),
#          Command('CHICKEN', None, None, None),
#          Command('ADD', None, None, None),
#          Command('FOX', None, None, None),
#          Command('ROOSTER', None, None, None),
#          Command('COMPARE', None, None, None),
#          Command('PICK', None, None, None),
#          Command('PUSH', None, None, 5),
#          Command('PICK', None, None, None),
#          Command('PECK', None, None, None),
#          Command('PUSH', None, None, 3),
#          Command('PICK', None, None, None),
#          Command('FR', None, None, None),
#          Command('BBQ', None, None, None),
#          Command('SET', 'baz', None, 3.0),
#          Block(('BUILD', 'qux'), code),
#          Block(('IF', 'TRUE'), code),
#          Block(('IF', 'FALSE'), code),
#          Block(('LOOP', 'TRUE'), code),
#          Block(('LOOP', 'FALSE'), code),
#          Block(('REPEAT', 'TRUE'), code),
#          Block(('REPEAT', 'FALSE'), code)]

end = time_ns()
pprint(parsed)
print("\nTook", (end - start) / 10 ** 6, "milliseconds")

print("\n\n\n")
print(str(parser))
