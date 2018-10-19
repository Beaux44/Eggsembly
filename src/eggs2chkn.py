import re, inspect, os.path
ops = {'axe': 0, 'chicken': 1, 'add': 2, 'fox': 3, 'rooster': 4, 'compare': 5, 'pick': 6, 'peck': 7, 'fr': 8, 'bbq': 9}
symbolNames = {'&': 'ampersand',
                "'": 'apostrophe',
                '*': 'asterisk',
                '@': 'at',
                '\\': 'backSlash',
                '|': 'bar',
                '{': 'beginBrace',
                '[': 'beginBracket',
                '(': 'beginParenthesis',
                '^': 'caret',
                ':': 'colon',
                ',': 'comma',
                '$': 'dollar',
                '}': 'endBrace',
                ']': 'endBracket',
                ')': 'endParenthesis',
                '=': 'equals',
                '!': 'exclamation',
                '>': 'greaterThan',
                '#': 'hash',
                '<': 'lessThan',
                '-': 'minus',
                '%': 'percent',
                '.': 'period',
                '+': 'plus',
                '?': 'question',
                '"': 'quotation',
                ';': 'semicolon',
                '/': 'Slash',
                ' ': 'space',
                '`': 'tick',
                '~': 'tilde',
                '_': 'underScore'
}
PUSH = re.compile(r"^(?:push )([0-9]+|(?:\'|\")[A-z0-9~`!@#$%^&*\(\)_+=|\\\{\}\[\]:;'<>,.?\/ ]*(?:\'|\"))$")
CALL = re.compile(r"^(?:call )([A-z0-9\.]+)$")
COMMENT = re.compile(
    r"""(?<![A-z0-9\ ])([\ \t]*//.*?\n)|([\ \t]*//.*?(?=\n))|(?<![A-z0-9\ ])([\ \t]*/\*.*?(?:(?=\*/)\*/|$)\n*)|([\ \t]*/\*.*?(?:(?=\*/)\*/|$))(?=\n*)|(?<![A-z0-9\ ])([\ \t]*~~\[==.*?(?:(?===\]~~)==\]~~|$)\n*)|([\ \t]*~~\[==.*?(?:(?===\]~~)==\]~~|$))(?=\n*)""",
    re.S)
def transpile(CODE, FILENAME, ROOT):
    ENDCHKN = ""
    for LINE in CODE.split("\n"):
        if LINE != "":
            LINE = LINE.strip()
            if LINE in ops:
                ENDCHKN += ("chicken " * ops[LINE])[:-1] + "\n"
            else:
                N = re.match(PUSH, LINE)
                if not N:
                    X = re.match(CALL, LINE)
                    if not X:
                        print("Something's mega wrong here, bud:\n\tIn file %s\n\t\t%s" % (repr(FILENAME), repr(LINE)))
                        break
                    else:
                        CALLNAME = LINE.split()[-1].replace(".", "\\") + ".eggs"
                        LIBFILE = "\\".join(inspect.getfile(inspect.currentframe()).split("\\")[:-1]) + "\\lib\\" + CALLNAME
                        if os.path.isfile(LIBFILE):
                            with open(LIBFILE, "r") as CALLFILE:
                                CALLCHKN = transpile(re.sub(COMMENT, "", CALLFILE.read()), CALLNAME, ROOT)
                                ENDCHKN += CALLCHKN
                        else:
                            with open(ROOT + CALLNAME, "r") as CALLFILE:
                                CALLCHKN = transpile(re.sub(COMMENT, "", CALLFILE.read()), CALLNAME, ROOT)
                                ENDCHKN += CALLCHKN
                else:
                    if "\"" in LINE or "'" in LINE:
                        LINE = N[1].strip("\"\'")
                        for x, i in enumerate(LINE):
                            if i in symbolNames.keys():
                                ENDCHKN += transpile("call ASCII.symbol." + symbolNames[i], FILENAME, ROOT)
                            elif i.lower() in "abcdefghijklmnopqrstuvwxyz":
                                if i.isupper():
                                    ENDCHKN += transpile("call ASCII.upper." + i, FILENAME, ROOT)
                                else:
                                    ENDCHKN += transpile("call ASCII.lower." + i, FILENAME, ROOT)
                            else:
                                ENDCHKN += transpile("call ASCII." + i, FILENAME, ROOT)
                            if x > 0:
                                ENDCHKN += "chicken chicken\n"
                    else:
                        if int(N[1]) < 0:
                            ENDCHKN += transpile("push 0\npush %s\nfox\n" % N[1], FILENAME, ROOT)
                        else:
                            ENDCHKN += ("chicken " * (int(N[1]) + 10))[:-1] + "\n"
    else:
        return ENDCHKN.lstrip("\n")
    return ""


SINGLELINECOMMENT = re.compile(r"[\t\ ]*//.*|[\t \ ]*/\*.*", re.S)
VALIDCODE = re.compile(r"^((?:push (?:[+-]?\d+|(?:\'|\")[A-z0-9~`!@#$%^&*\(\)_+=|\\\{\}\[\]:;'<>,.?\/ ]*(?:\'|\")))|(?:call [A-z0-9_\.]+)|(?:axe|chicken|add|fox|rooster|compare|pick|peck|fr|bbq)|\n|)$")
def validate(CODE, FILENAME, ROOT):
    INCOM = False
    for LINENUMBER, LINE in enumerate(CODE.split("\n"), 1):
        if re.match(CALL, LINE):

            CALLNAME = LINE.split()[1].replace(".", "\\") + ".eggs"
            LIBFILE = "\\".join(inspect.getfile(inspect.currentframe()).split("\\")[:-1]) + "\\lib\\" + CALLNAME
            if not os.path.isfile(LIBFILE):
                try:
                    with open(ROOT + CALLNAME, "r") as CALLFILE:
                        if not validate(CALLFILE.read(), CALLNAME, ROOT):
                            return False
                except FileNotFoundError:
                    print("%s does not exist, called on line %d:\n\t%s" % (repr(CALLNAME), LINENUMBER, LINE))
                    return False

        elif not re.match(VALIDCODE, re.sub(SINGLELINECOMMENT, "", LINE)) and not INCOM:
            print("Invalid command on line %d in file %s: %s" % (LINENUMBER, repr(FILENAME), repr(LINE)))
            return False

        if "/*" in LINE and INCOM == False:
            INCOM = True

        if "*/" in LINE and INCOM == True:
            INCOM = False
    return True
