from .extras import *
import ply.yacc as yacc
from .Lexer import EggLex
from .AST import *

__all__ = ["EggParse"]


class EggParse(object):
    """Class for parsing Eggsembly"""
    def __init__(self, file, **kwargs):
        self.vars: Dict[str, Union[int, float, str]] = {}
        self.funcs: Dict[str, Block] = {}
        self.mfuncs: Dict[str, Callable[..., floatOrInt]] = {}
        self.consts: Dict[str, floatIntOrString] = {}

        self.lexer = EggLex(file)
        self.parser: yacc.LRParser = yacc.yacc(module=self, debug=True, write_tables=False, **kwargs)
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
        ('right', 'NEG', 'POS'),
        ('right', 'POW'),
        ('left', 'LPAREN')
    )

    def p_ignore(self, p):
        """ \t"""

    def p_error(self, p):
        cprint(ERROR, "Syntax error on line %d:\n\t%s" % (self.lexer.lineno,
                                                          self.data.split("\n")[self.lexer.lineno - 1].strip()))

    # The main syntax of the language,
    def p_syntax(self, p):
        """syntax : syntax NEWLINE block
                  | syntax NEWLINE stmt
                  | block
                  | stmt
        """
        if len(p) == 4:
            p[0] = p[1] + (not isinstance(p, list) and [p] or [*p]) if p[3] is not None else p[1]
        else:
            p[0] = [p[1]] if p[1] is not None else []

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
        """block : enter NEWLINE syntax NEWLINE RBRACE"""
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
        if p[2] in self.mfuncs:
            cprint(ERROR, f"Name {p[2]} used for constant and mathematical function, line {self.lexer.lineno}")
        elif p[2] not in self.consts:
            if isinstance(p[4], Function):
                self.mfuncs[p[2]] = p[4]
            else:
                self.consts[p[2]] = p[4]
        else:
            raise ConstChangedError("Constant %r redefined" % p[2])


    def p_stmt_BLANKLINE(self, p):
        """stmt : """

    def p_expr_MUL(self, p):
        """mathexpr : mathexpr MUL mathexpr"""
        p[0] = p[1] * p[3]

    def p_expr_FUNCCALL(self, p):
        """mathexpr : mathexpr LPAREN TUPLE COM RPAREN
                    | mathexpr LPAREN TUPLE RPAREN
        """
        if not isinstance(p[1], Function):
            cprint(ERROR, f"Innapropriate function call, line {self.lexer.lineno}")
            exit()
        else:
            p[0] = p[1]({**self.mfuncs, **self.consts}, *p[3])

    def p_expr_FUNCCALL_e(self, p):
        """mathexpr : mathexpr LPAREN mathexpr RPAREN"""
        if not isinstance(p[1], Function):
            cprint(ERROR, f"Innapropriate function call, line {self.lexer.lineno}")
            exit()
        else:
            p[0] = p[1]({**self.mfuncs, **self.consts}, p[3])


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
        if p[1] in self.consts:
            p[0] = self.consts[p[1]]
        elif p[1] in self.mfuncs:
            p[0] = self.mfuncs[p[1]]
        else:
            cprint(ERROR, f"Non-existent name {p[1]!r} used on line {self.lexer.lineno}")

    def p_stmt_SETFUNC(self, p):
        """stmt : LET ID IDTUPLE EQ AST"""
        if p[2] in self.mfuncs:
            cprint(WARNING, f"Function {p[2]} redefined on {self.lexer.lineno - 1}")
        if p[2] in self.consts:
            cprint(ERROR, f"Name {p[2]} used for constant and mathematical function on line {self.lexer.lineno - 1}")
        else:
            self.mfuncs[p[2]] = Function(p[2], p[3], p[5])
        if isinstance(p[5], Const):
            cprint(WARNING, f"Function {p[2]} defined on line {self.lexer.lineno - 1} can be made into a const")
        elif isinstance(p[5].term, Const):
            cprint(WARNING, f"Function {p[2]} defined on line {self.lexer.lineno - 1} can be made into a const")

    def p_AST_MUL(self, p):
        """AST : AST MUL AST"""
        if isinstance(p[1], Const) and isinstance(p[3], Const):
            p[0] = p[1] * p[3]
            return
        elif isinstance(p[1], Const) or isinstance(p[3], Const):
            if p[1].value == 0:
                p[0] = Const(0)
                return
            elif p[1].value == 1:
                p[0] = p[3]
                return
            else:
                if p[3].value == 0:
                    p[0] = Const(0)
                    return
                elif p[3].value == 1:
                    p[0] = p[1]
                    return

        if isinstance(p[1], Neg) and isinstance(p[3], Const):
            p[0] = Mul(p[1].term, -p[3])
        elif isinstance(p[1], Const) and isinstance(p[3], Neg):
            p[0] = Mul(-p[1], p[3].term)
        else:
            p[0] = Mul(p[1], p[3])

    def p_AST_FUNCCALL(self, p):
        """AST : AST LPAREN AST RPAREN"""
        if not isinstance(p[1], Var):
            cprint(ERROR, f"Invalid call")
        p[0] = FuncInFunc(p[1].name, [p[3]], self.lexer.lineno)

    def p_AST_DIV(self, p):
        """AST : AST DIV AST"""
        if isinstance(p[1], Const) and isinstance(p[3], Const):
            p[0] = p[1] / p[3]
        else:
            p[0] = Div(p[1], p[3])

    def p_AST_MOD(self, p):
        """AST : AST MOD AST"""
        if isinstance(p[1], Const) and isinstance(p[3], Const):
            p[0] = p[1] % p[3]
        else:
            p[0] = Mod(p[1], p[3])

    def p_AST_FDIV(self, p):
        """AST : AST FDIV AST"""
        if isinstance(p[1], Const) and isinstance(p[3], Const):
            p[0] = p[1] // p[3]
        else:
            p[0] = FloorDiv(p[1], p[3])

    def p_AST_ADDE(self, p):
        """AST : AST ADDE AST"""
        if isinstance(p[1], Const) and isinstance(p[3], Const):
            p[0] = p[1] + p[3]
        else:
            if p[1].value == 0:
                p[0] = p[3]
                return
            elif p[3].value == 0:
                p[0] = p[1]
                return

            p[0] = Add(p[1], p[3])

    def p_AST_SUB(self, p):
        """AST : AST SUB AST"""
        if isinstance(p[1], Const) and isinstance(p[3], Const):
            p[0] = p[1] - p[3]
            return
        elif isinstance(p[1], Const):
            if isinstance(p[3], Neg):
                x = p[3].term
            else:
                x = Neg(p[3])

            if p[1].value == 0:
                p[0] = x
                return

            p[0] = Add(p[1], x)

        p[0] = Sub(p[1], p[3])

    def p_AST_POW(self, p):
        """AST : AST POW AST"""
        if isinstance(p[1], Const) and isinstance(p[3], Const):
            p[0] = p[1] ** p[3]
        elif p[3].value == 0:
            p[0] = Const(1)
        elif p[3].value == 1:
            p[0] = p[1]
        elif p[1].value == 1:
            p[0] = Const(1)
        else:
            p[0] = Pow(p[1], p[3])

    def p_AST_PARENMATH(self, p):
        """AST : LPAREN AST RPAREN"""
        p[0] = p[2]

    def p_AST_NEG(self, p):
        """AST : SUB AST %prec NEG"""
        if isinstance(p[2], Neg):
            p[0] = p[2].term
        elif isinstance(p[2], Const):
            p[0] = Const(-p[2].value)
        else:
            p[0] = Neg(p[2])

    def p_AST_POS(self, p):
        """AST : ADDE AST %prec POS"""
        p[0] = p[2]

    def p_AST_MATH(self, p):
        """AST : INT
               | FLOAT
        """
        p[0] = Const(p[1])

    def p_AST_ID(self, p):
        """AST : ID"""
        p[0] = Var(p[1], self.lexer.lineno)

    def p_FUNCTION(self, p):
        """FUNC : FUNC DOT ID
                | ID
        """
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

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

    def p_TUPLE_T(self, p):
        """TUPLE : TUPLE COM mathexpr"""
        p[0] = p[1] + [p[2]]

    def p_TUPLE_TF(self, p):
        """TUPLE : mathexpr COM mathexpr"""
        p[0] = [p[1], p[3]]

    def p_AST_TUPLE_T(self, p):
        """ASTTUPLE : TUPLE COM AST"""
        p[0] = p[1] + [p[2]]

    def p_AST_TUPLE_TF(self, p):
        """ASTTUPLE : AST COM AST"""
        p[0] = [p[1], p[3]]

    def p_IDTUPLE(self, p):
        """IDTUPLE : LPAREN IDTUPLE_T RPAREN
                   | LPAREN IDTUPLE_T COM RPAREN
        """
        p[0] = p[2]

    def p_IDTUPLE_T(self, p):
        """IDTUPLE_T : IDTUPLE_T COM ID
                     | ID
        """
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]
