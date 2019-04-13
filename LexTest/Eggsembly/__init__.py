from . import Lexer, Parser, AST, extras
import os

__doc__ = "Module for parsing and lexing the Eggsembly language."
__all__ = ["Lexer", "Parser", "extras"]
__dir__ = os.path.dirname(os.path.realpath(__file__))


def main():
    """Runs and prints result of test code and then exits"""
    lexer = Lexer.EggLex("blah.eggs")
    parser = Parser.EggParse("blah.eggs")

    from time import time_ns
    from pprint import pprint

    blah = open(os.path.join(__dir__, 'blah.eggs'), 'r').read()

    start = time_ns()
    lexed = lexer(blah)
    end = time_ns()
    print(*map(lambda a: f"Line {a[0]}: {a[1]}", enumerate(lexed, 1)), sep="\n")
    print("\nTook", (end - start) / 10 ** 6, "milliseconds\n\n")

    start = time_ns()

    parsed = parser(blah, debug=0)
    # Function g defined on line 62 can be made into a const
    # [Command('PUSH', None, None, -64.0),
    #  Command('PUSH', None, None, 4.0),
    #  Command('PUSH', None, None, -6),
    #  Command('PUSH', None, None, 1.0),
    #  Command('PUSH', None, None, 192.0),
    #  Command('PUSH', None, None, 144.0),
    #  Command('PUSH', None, None, "'3'"),
    #  Command('AS', ('a', 'b'), None, None),
    #  Command('AS', ('x', 'y'), None, None),
    #  Command('AXE', None, None, None),
    #  Command('CHICKEN', None, None, None),
    #  Command('ADD', None, None, None),
    #  Command('FOX', None, None, None),
    #  Command('HATCH', ['a', 'b'], None, None),
    #  Command('ROOSTER', None, None, None),
    #  Command('COMPARE', None, None, None),
    #  Command('PICK', None, None, None),
    #  [Command('PUSH', None, None, 5), Command('PICK', None, None, None)],
    #  Command('PECK', None, None, None),
    #  [Command('PUSH', None, None, 3), Command('PICK', None, None, None)],
    #  Command('FR', None, None, None),
    #  Command('BBQ', None, None, None),
    #  Command('SET', 'baz', None, 3.0),
    #  Block(('BUILD', ['qux']), code),
    #  Block(('IF', 'TRUE'), code),
    #  Block(('IF', 'FALSE'), code),
    #  Block(('LOOP', 'TRUE'), code),
    #  Block(('LOOP', 'FALSE'), code),
    #  Block(('REPEAT', 'TRUE'), code),
    #  Block(('REPEAT', 'FALSE'), code),
    #  Command('PUSH', None, None, 5835)]

    end = time_ns()
    pprint(parsed)
    print("\nTook", (end - start) / 10**6, "milliseconds")

    print("\n\n\n")
    print(str(parser))
    exit(0)


""" TODO:
         Take OOP too far
         Make it do anything
         ✓ Come up with better while notation
         ✓ Make blocks work
         ✓ Add more comments
"""
if __name__ == '__main__':
    main()
