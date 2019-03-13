from extras import *
import ply.yacc as yacc
from Lexer import EggLex


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
