from typing import Union, Tuple, List
import re

symbolCodes = {
    '\t': 'push9\nbbq',
    '\n': 'push 10\nbbq\n',
    '\r': 'push 4\npush 4\nrooster\npush 1\nadd\nbbq\n',
    ' ': 'push 8\npush 4\nrooster\nbbq\n',
    '!': 'push 8\npush 4\nrooster\npush 1\nadd\nbbq\n',
    '"': 'push 8\npush 4\nrooster\npush 2\nadd\nbbq\n',
    '#': 'push 8\npush 4\nrooster\npush 3\nadd\nbbq\n',
    '$': 'push 9\npush 4\nrooster\nbbq\n',
    '%': 'push 9\npush 4\nrooster\npush 1\nadd\nbbq\n',
    '&': 'push 9\npush 4\nrooster\npush 2\nadd\nbbq\n',
    "'": 'push 9\npush 4\nrooster\npush 3\nadd\nbbq\n',
    '(': 'push 8\npush 5\nrooster\nbbq\n',
    ')': 'push 8\npush 5\nrooster\npush 1\nadd\nbbq\n',
    '*': 'push 8\npush 5\nrooster\npush 2\nadd\nbbq\n',
    '+': 'push 8\npush 5\nrooster\npush 3\nadd\nbbq\n',
    ',': 'push 9\npush 5\nrooster\npush 1\nfox\nbbq\n',
    '-': 'push 9\npush 5\nrooster\nbbq\n',
    '.': 'push 9\npush 5\nrooster\npush 1\nadd\nbbq\n',
    '/': 'push 9\npush 5\nrooster\npush 2\nadd\nbbq\n',
    '0': 'push 7\npush 7\nrooster\npush 1\nfox\nbbq\n',
    '1': 'push 7\npush 7\nrooster\nbbq\n',
    '2': 'push 10\npush 5\nrooster\nbbq\n',
    '3': 'push 10\npush 5\nrooster\npush 1\nadd\nbbq\n',
    '4': 'push 10\npush 5\nrooster\npush 2\nadd\nbbq\n',
    '5': 'push 7\npush 7\nrooster\npush 4\nadd\nbbq\n',
    '6': 'push 10\npush 5\nrooster\npush 4\nadd\nbbq\n',
    '7': 'push 11\npush 5\nrooster\nbbq\n',
    '8': 'push 11\npush 5\nrooster\npush 1\nadd\nbbq\n',
    '9': 'push 11\npush 5\nrooster\npush 2\nadd\nbbq\n',
    ':': 'push 10\npush 6\nrooster\npush 2\nfox\nbbq\n',
    ';': 'push 10\npush 6\nrooster\npush 1\nfox\nbbq\n',
    '<': 'push 10\npush 6\nrooster\nbbq\n',
    '=': 'push 10\npush 6\nrooster\npush 1\nadd\nbbq\n',
    '>': 'push 10\npush 6\nrooster\npush 1\nadd\nbbq\n',
    '?': 'push 10\npush 6\nrooster\npush 3\nadd\nbbq\n',
    '@': 'push 8\npush 8\nrooster\nbbq\n',
    'A': 'push 9\npush 7\nrooster\npush 2\nadd\nbbq\n',
    'B': 'push 11\npush 6\nrooster\nbbq\n',
    'C': 'push 11\npush 6\nrooster\npush 1\nadd\nbbq\n',
    'D': 'push 11\npush 6\nrooster\npush 2\nadd\nbbq\n',
    'E': 'push 11\npush 6\nrooster\npush 3\nadd\nbbq\n',
    'F': 'push 10\npush 7\nrooster\nbbq\n',
    'G': 'push 10\npush 7\nrooster\npush 1\nadd\nbbq\n',
    'H': 'push 9\npush 8\nrooster\nbbq\n',
    'I': 'push 9\npush 8\nrooster\npush 1\nadd\nbbq\n',
    'J': 'push 9\npush 8\nrooster\npush 2\nadd\nbbq\n',
    'K': 'push 9\npush 8\nrooster\npush 3\nadd\nbbq\n',
    'L': 'push 9\npush 8\nrooster\npush 4\nadd\nbbq\n',
    'M': 'push 9\npush 8\nrooster\npush 5\nadd\nbbq\n',
    'N': 'push 9\npush 8\nrooster\npush 6\nadd\nbbq\n',
    'O': 'push 9\npush 8\nrooster\npush 7\nadd\nbbq\n',
    'P': 'push 10\npush 8\nrooster\nbbq\n',
    'Q': 'push 9\npush 9\nrooster\nbbq\n',
    'R': 'push 10\npush 8\nrooster\npush 2\nadd\nbbq\n',
    'S': 'push 10\npush 8\nrooster\npush 3\nadd\nbbq\n',
    'T': 'push 10\npush 8\nrooster\npush 4\nadd\nbbq\n',
    'U': 'push 10\npush 8\nrooster\npush 5\nadd\nbbq\n',
    'V': 'push 10\npush 8\nrooster\npush 6\nadd\nbbq\n',
    'W': 'push 10\npush 8\nrooster\npush 7\nadd\nbbq\n',
    'X': 'push 11\npush 8\nrooster\nbbq\n',
    'Y': 'push 11\npush 8\nrooster\npush 1\nadd\nbbq\n',
    'Z': 'push 10\npush 9\nrooster\nbbq\n',
    '[': 'push 10\npush 9\nrooster\npush 1\nadd\nbbq\n',
    '\\': 'push 10\npush 9\nrooster\npush 2\nadd\nbbq\n',
    ']': 'push 10\npush 9\nrooster\npush 3\nadd\nbbq\n',
    '^': 'push 10\npush 9\nrooster\npush 4\nadd\nbbq\n',
    '_': 'push 10\npush 9\nrooster\npush 5\nadd\nbbq\n',
    '`': 'push 10\npush 9\nrooster\npush 6\nadd\nbbq\n',
    'a': 'push 10\npush 10\nrooster\npush 3\nfox\nbbq\n',
    'b': 'push 10\npush 10\nrooster\npush 2\nfox\nbbq\n',
    'c': 'push 10\npush 10\nrooster\npush 1\nfox\nbbq\n',
    'd': 'push 10\npush 10\nrooster\nbbq\n',
    'e': 'push 10\npush 10\nrooster\npush 1\nadd\nbbq\n',
    'f': 'push 10\npush 10\nrooster\npush 2\nadd\nbbq\n',
    'g': 'push 10\npush 10\nrooster\npush 3\nadd\nbbq\n',
    'h': 'push 10\npush 10\nrooster\npush 4\nadd\nbbq\n',
    'i': 'push 10\npush 10\nrooster\npush 5\nadd\nbbq\n',
    'j': 'push 11\npush 10\nrooster\npush 4\nfox\nbbq\n',
    'k': 'push 11\npush 10\nrooster\npush 3\nfox\nbbq\n',
    'l': 'push 11\npush 10\nrooster\npush 2\nfox\nbbq\n',
    'm': 'push 11\npush 10\nrooster\npush 1\nfox\nbbq\n',
    'n': 'push 11\npush 10\nrooster\nbbq\n',
    'o': 'push 11\npush 10\nrooster\npush 1\nadd\nbbq\n',
    'p': 'push 11\npush 10\nrooster\npush 2\nadd\nbbq\n',
    'q': 'push 11\npush 10\nrooster\npush 3\nadd\nbbq\n',
    'r': 'push 11\npush 10\nrooster\npush 4\nadd\nbbq\n',
    's': 'push 11\npush 10\nrooster\npush 5\nadd\nbbq\n',
    't': 'push 12\npush 10\nrooster\npush 4\nfox\nbbq\n',
    'u': 'push 12\npush 10\nrooster\npush 3\nfox\nbbq\n',
    'v': 'push 12\npush 10\nrooster\npush 2\nfox\nbbq\n',
    'w': 'push 12\npush 10\nrooster\npush 1\nfox\nbbq\n',
    'x': 'push 12\npush 10\nrooster\nbbq\n',
    'y': 'push 12\npush 10\nrooster\npush 1\nadd\nbbq\n',
    'z': 'push 12\npush 10\nrooster\npush 2\nadd\nbbq\n',
    '{': 'push 12\npush 10\nrooster\npush 3\nadd\nbbq\n',
    '|': 'push 12\npush 10\nrooster\npush 4\nadd\nbbq\n',
    '}': 'push 5\npush 5\npush 5\nrooster\nrooster\nbbq\n',
    '~': 'push 12\npush 10\nrooster\npush 6\nadd\nbbq\n'
}


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

    def __str__(self) -> str:  # Compiles command object to equivalent Chicken code
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
