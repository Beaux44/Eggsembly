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
                '_': 'underScore',
                '\r': 'CR',
                '\n': 'LF'
}
PUSH = re.compile(r"""^(?:push )((?:\d+|\d*\.\d*)|(?P<quote>'|")(?P<str>[ -~]*?)(?P=quote))$""")
PICK = re.compile(r"^(?:pick )(\d+)$")
CALL = re.compile(r"^(?:call )([A-Za-z0-9\.]+)$")
COMMENT = re.compile(
    r"(?<![A-z0-9\ ])([\ \t]*//.*?\n)|([\ \t]*//.*?(?=\n))|(?<![A-z0-9\ ])([\ \t]*/\*.*?(?:(?=\*/)\*/|$)\n*)|([\ \t]*/\*.*?(?:(?=\*/)\*/|$))(?=\n*)|(?<![A-z0-9\ ])([\ \t]*~~\[==.*?(?:(?===\]~~)==\]~~|$)\n*)|([\ \t]*~~\[==.*?(?:(?===\]~~)==\]~~|$))(?=\n*)",
    re.S)
VARIABLE = re.compile(r"^(?:(?P<name>[A-Za-z0-9_]+)(?:\[(?P<index>\d+)\])?(?:\s*?=\s*?(?P<value>Top|(?P<assquote>'|\")[ -~]+(?P=assquote)|\d+))?)$")
VARS = {}
def transpile(CODE, FILENAME, ROOT):
    ENDCHKN = ""
    for LINENUMBER, LINE in enumerate(CODE.split("\n"), 1):
        if LINE != "":
            LINE = LINE.strip()
            if LINE in ops:
                ENDCHKN += ("chicken " * ops[LINE])[:-1] + "\n"
            else:
                N = re.match(PUSH, LINE)
                if not N:
                    X = re.match(CALL, LINE)
                    if not X:
                        Y = re.match(VARIABLE, LINE)
                        if not Y:
                            Z = re.match(PICK, LINE)
                            if not Z:
                                    print("Something's mega wrong here, bud:\n\tOn line %d of file %s\n\t\t%s" % (LINENUMBER, repr(FILENAME), repr(LINE)))
                                    break
                            else:
                                ENDCHKN += transpile("push %s\npick" % Z[1], FILENAME, ROOT)
                        else:
                            name = Y["name"]
                            index = Y["index"]
                            value = Y["value"]
                            if index != None:
                                index = int(index)
                                VARS[name] = index

                            if name not in VARS and index == None:
                                print("Variable %r not defined on line %d in file %r" % (name, LINENUMBER, FILENAME))
                                break
                            elif value == None and value != "Top":
                                if index != None:
                                    ENDCHKN += transpile("pick %d\naxe" % index, FILENAME, ROOT)
                                else:
                                    ENDCHKN += transpile("pick %d\naxe" % VARS[name], FILENAME, ROOT)
                            elif value == "Top":
                                ENDCHKN += transpile("push %d\npeck" % (VARS[name]), FILENAME, ROOT)
                            else:
                                ENDCHKN += transpile("push %s\npush %d\npeck" % (value, VARS[name]), FILENAME, ROOT)
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
                    if '"' in LINE or "'" in LINE:
                        LINE = N["str"]
                        LINE = LINE.replace("\\r", "")
                        LINE = LINE.replace("\\n", "\n")
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
                        try:
                            if int(N[1]) < 0:
                                ENDCHKN += transpile("push 0\npush %s\nfox\n" % N[1], FILENAME, ROOT)
                            else:
                                ENDCHKN += ("chicken " * (int(N[1]) + 10))[:-1] + "\n"
                        except:
                            ENDCHKN += transpile('push "%s"\npush 0\nfox' % N[1], FILENAME, ROOT)
    else:
        return ENDCHKN.lstrip("\n")
    return ""


SINGLELINECOMMENT = re.compile(r"[\t ]*//.*|[\t ]*/\*.*", re.S)
VALIDCODE = re.compile(r"^(?:push (?:(?:[+-]?\d+|(?:[+-]?\d+\.\d*|[+-]?\d*\.\d+))|(?P<quote>'|\")[ -~]+(?P=quote))|(?:pick \d+)|(?:call [A-Za-z0-9_\.]+)|(?:[A-Za-z_][A-Za-z0-9_]*?(?:\[\d+\])?(?:\s*?=\s*?(?:Top|(?P<assquote>'|\")[ -~]+(?P=assquote)|[0-9]+))?)|\n|)$")
def validate(CODE, FILENAME, ROOT):
    INCOM = False
    INSTR = False
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

        elif not re.match(VALIDCODE, re.sub(SINGLELINECOMMENT, "", LINE)) and not (INCOM or INSTR):
            print("Invalid command on line %d in file %s: %s" % (LINENUMBER, repr(FILENAME), repr(LINE)))
            return False

        if "/*" in LINE and INCOM == False:
            INCOM = True

        if "*/" in LINE and INCOM == True:
            INCOM = False

        if "\""*3 in LINE and INSTR == True:
            INSTR = False

        if "\""*3 in LINE and INSTR == False:
            INSTR = True


    return True
