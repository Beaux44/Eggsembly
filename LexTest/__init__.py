import extras, Lexer, Parser

""" TODO:
         Take OOP too far
         Make it do anything
         ✓ Come up with better while notation
         ✓ Make blocks work
         ✓ Add more comments
"""
if __name__ == '__main__':
    lexer = Lexer.EggLex()
    parser = Parser.EggParse()

    from time import time_ns
    from pprint import pprint

    blah = open('blah.eggs', 'r').read()

    start = time_ns()
    lexed = lexer(blah)
    end = time_ns()
    print(*map(lambda a: f"Line {a[0]}: {a[1]}", enumerate(lexed, 1)), sep="\n")
    print("\nTook", (end - start) / 10 ** 6, "milliseconds\n\n")

    start = time_ns()

    parsed = parser(blah, debug=0)
    # [Command('PUSH', None, None, -64.0),
    #  Command('PUSH', None, None, 4.0),
    #  Command('PUSH', None, None, -6),
    #  Command('PUSH', None, None, 1.0),
    #  Command('PUSH', None, None, 192.0),
    #  Command('PUSH', None, None, 144.0),
    #  Command('PUSH', None, None, 144.0),
    #  Command('PUSH', None, None, "'3'"),
    #  Command('AS', ('a', 'b'), None, None),
    #  Command('AS', ('x', 'y'), None, None),
    #  Command('AXE', None, None, None),
    #  Command('CHICKEN', None, None, None),
    #  Command('ADD', None, None, None),
    #  Command('FOX', None, None, None),
    #  Command('ROOSTER', None, None, None),
    #  Command('COMPARE', None, None, None),
    #  Command('PICK', None, None, None),
    #  Command('PUSH', None, None, 5),
    #  Command('PICK', None, None, None),
    #  Command('PECK', None, None, None),
    #  Command('PUSH', None, None, 3),
    #  Command('PICK', None, None, None),
    #  Command('FR', None, None, None),
    #  Command('BBQ', None, None, None),
    #  Command('SET', 'baz', None, 3.0),
    #  Block(('BUILD', 'qux'), code),
    #  Block(('IF', 'TRUE'), code),
    #  Block(('IF', 'FALSE'), code),
    #  Block(('LOOP', 'TRUE'), code),
    #  Block(('LOOP', 'FALSE'), code),
    #  Block(('REPEAT', 'TRUE'), code),
    #  Block(('REPEAT', 'FALSE'), code)]

    end = time_ns()
    pprint(parsed)
    print("\nTook", (end - start) / 10 ** 6, "milliseconds")

    print("\n\n\n")
    print(str(parser))
