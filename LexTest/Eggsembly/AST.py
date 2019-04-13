from typing import List, Union, NoReturn, Dict
from .extras import cprint, ERROR

__doc__ = "Abstract Syntax Tree for mathematical functions"
__all__ = ["Function", "Const", "Var", "Neg", "Add", "Sub", "Mul", "FloorDiv", "Div", "Mod", "Pow", "FuncInFunc"]


class Function(object):
    def __init__(self, name: str, args: List[str], ast: 'Expr') -> NoReturn:
        self.name: str = name
        self.args: List[str] = args
        self._ast: Expr = ast

    def __call__(self, _globals: 'Dict[str, Union[Function, int, float]]', *args: Union[float, int]) -> Union[float,
                                                                                                              int]:
        # Combines global and local variables, overwrites global variables with local ones; pretty neato
        kwargs: 'Dict[str, Union[Function, float, int]]' = {**_globals, **dict(zip(self.args, args))}
        if len(self.args) != len(args):
            raise TypeError(f"Function {self.name} expected {len(self.args)} arguments, received {len(args)}")

        return self._ast(kwargs, _globals)


class FuncInFunc(object):
    def __init__(self, f: str, arg_ast: 'List[Expr]', lineno: int) -> NoReturn:
        self.f: str = f
        self._ast: List[Expr] = arg_ast
        self.lineno: int = lineno

    def __call__(self, kwargs, _globals) -> Union[float, int]:
        if self.f not in _globals:
            cprint(ERROR, f"Non-existent name {self.f} used on line {self.lineno}")
            exit(-1)
        return _globals[self.f](_globals,
                                *[i(kwargs, _globals) for i in self._ast])


class Op(object):
    def __init__(self):
        self.value = None
        self.term = None
        self.left = None
        self.right = None

    def __str__(self):
        if self.right is not None and self.left is not None:
            return f"{self.__class__.__name__}({self.left}, {self.right})"

        if self.term is not None:
            return f"{self.__class__.__name__}({self.term})"

    __repr__ = __str__


class BinaryOperator(Op):
    def __init__(self, left: 'Expr', right: 'Expr') -> NoReturn:
        super().__init__()
        self.left: Expr = left
        self.right: Expr = right


class UnaryOperator(Op):
    def __init__(self, term: 'Expr') -> NoReturn:
        super().__init__()
        self.term = term


class Const(object):
    def __init__(self, value: Union[float, int]) -> NoReturn:
        self.value: Union[float, int] = value
        self.term = None

    def __call__(self, kwargs, _globals: Dict[str, Union[Function, float, int]]) -> Union[float, int]:
        return self.value

    def __str__(self):
        return f"Const({self.value})"

    def __neg__(self):
        return Const(-self.value)

    def __truediv__(self, other):
        return Const(self.value / other.value)

    def __floordiv__(self, other):
        return Const(self.value // other.value)

    def __pow__(self, other):
        return Const(self.value**other.value)

    def __add__(self, other):
        return Const(self.value + other.value)

    def __sub__(self, other):
        return Const(self.value - other.value)

    def __mod__(self, other):
        return Const(self.value % other.value)

    def __mul__(self, other):
        return Const(self.value * other.value)

    __repr__ = __str__


class Var(object):
    def __init__(self, name: str, lineno: int) -> NoReturn:
        self.value = None
        self.term = None
        self.name: str = name
        self.lineno: int = lineno

    def __call__(self, kwargs, _globals):
        if self.name not in kwargs:
            cprint(ERROR, f"Non-existent name {self.name} used on line")
            exit(-1)
        return kwargs[self.name]

    def __str__(self):
        return f"Var({self.name!r})"

    __repr__ = __str__


class Neg(UnaryOperator):
    def __call__(self, kwargs, _globals) -> Union[float, int]:
        return self.term(kwargs, _globals)


class Add(BinaryOperator):
    def __call__(self, kwargs, _globals) -> Union[float, int]:
        return self.left(kwargs, _globals) + self.right(kwargs, _globals)


class Sub(BinaryOperator):
    def __call__(self, kwargs, _globals) -> Union[float, int]:
        return self.left(kwargs, _globals) - self.right(kwargs, _globals)


class Mul(BinaryOperator):
    def __call__(self, kwargs, _globals) -> Union[float, int]:
        return self.left(kwargs, _globals) * self.right(kwargs, _globals)


class Div(BinaryOperator):
    def __call__(self, kwargs, _globals) -> float:
        return self.left(kwargs, _globals) / self.right(kwargs, _globals)


class FloorDiv(BinaryOperator):
    def __call__(self, kwargs, _globals) -> Union[float, int]:
        return self.left(kwargs, _globals) // self.right(kwargs, _globals)


class Mod(BinaryOperator):
    def __call__(self, kwargs, _globals) -> Union[float, int]:
        return self.left(kwargs, _globals) % self.right(kwargs, _globals)


class Pow(BinaryOperator):
    def __call__(self, kwargs, _globals) -> Union[float, int]:
        return self.left(kwargs, _globals) ** self.right(kwargs, _globals)


Expr = Union[Const, Var, Add, Sub, Mul, Div, FloorDiv, Pow, FuncInFunc]

if __name__ == '__main__':
    print(Function("f", ["x", "y"], Add(Sub(Div(Pow(Var("x"), Var("y")), Const(2)), Var("y")), Const(2)))(2, 4))
