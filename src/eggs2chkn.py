import re, inspect, os.path, colorama
from difflib import SequenceMatcher
colorama.init()

WARNING = colorama.Fore.LIGHTYELLOW_EX
ERROR   = colorama.Fore.LIGHTRED_EX

def cprint(color, *args, **kwargs):
    print(end=(color))
    print(*args, **kwargs)
    print(end=(colorama.Fore.RESET + colorama.Back.RESET))


FILEPATH = lambda CALLNAME: "\\".join(inspect.getfile(inspect.currentframe()).split("\\")[:-1]) + ".\\lib\\" + CALLNAME
ops = {
        'axe': 0,
        'chicken': 1,
        'add': 2,
        'fox': 3,
        'rooster': 4,
        'compare': 5,
        'pick': 6,
        'peck': 7,
        'fr': 8,
        'bbq': 9
    }


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

names = [
        "exit",
        "chicken",
        "add",
        "fox",
        "rooster",
        "compare",
        "pick",
        "peck",
        "fr",
        "BBQ"
    ]

PUSH = re.compile(r"^[ \t]*push((?: \d+|\d*\.\d*)| ?(?P<quote>[\"'])(?P<str>(?:(?=(?P<slash>\\?))(?P=slash)[ -~])*?)(?P=quote))$")
PICK = re.compile(r"^[ \t]*pick (\d+)$")
PECK = re.compile(r"^[ \t]*peck (\d+)$")
CALL = re.compile(r"^[ \t]*hatch ([A-Za-z0-9\.]+)$")
COMMENT = re.compile(
    r"(?<![A-Za-z0-9\ \"\'{])([\ \t]*//.*\n?)|([\ \t]*//.*?(?=\n))|(?<![A-Za-z0-9\ \"\'{]])([\ \t]*/\*.*?(?:(?=\*/)\*/|$)\n*)|([\ \t]*/\*.*?(?:(?=\*/)\*/|$))(?=\n*)|(?<![A-Za-z0-9\ \"\'{])([\ \t]*~~\[==.*?(?:(?===\]~~)==\]~~|$)\n*)|([\ \t]*~~\[==.*?(?:(?===\]~~)==\]~~|$))(?=\n*)",
    re.S)
VARIABLE = re.compile(r"^(?:(?P<name>[A-Za-z0-9_]+)(?:\[(?P<index>\d+)\])?(?:\s*?=\s*?(?P<value>Top|(?P<assquote>[\"'])(?P<str>(?:(?=(?P<slash>\\?))(?P=slash)[ -~])*?)(?P=assquote)|\d+))?)$") # "assquote" is short for assignment quote :3
VARS     = {"input": 1}
MACRO    = re.compile(r"^(?P<replace>.+) +[Aa]s +(?P<replacement>.+)$", re.M)
MACROS   = {}
ROOST     = re.compile(r"build[ \t]+(?P<name>[A-Za-z_][A-Za-z0-9_]*)[ \t]*{")
ROOSTN    = 0
ROOSTS    = {}

def fuzzyMatchesIn(a, l):
    matches = {}
    a = a.lower()
    for b in l:
        m = SequenceMatcher(None, a, b.lower()).ratio()
        if m >= 0.5:
            matches[b] = m
    return ([*zip(*sorted(matches.items(), key=lambda kv: kv[1], reverse=True))] or [[]])[0]  # Sort suggestions by similarity
                                                                                              # Like meh spook?

def getProc(CODE, LINENUMBER, FILENAME, ROOT):
    ENDCHKN = ""
    n = 1
    while CODE.split("\n")[LINENUMBER] != "}":
        ENDCHKN += transpile(CODE.split("\n")[LINENUMBER], FILENAME, ROOT, LINENUMBER+1)
        n += 1
        LINENUMBER += 1
    return (n, ENDCHKN)

def transpile(CODE, FILENAME, ROOT, LINEORIGIN=1):
    global VARS, MACROS, ROOSTN, ROOSTS
    ENDCHKN = ""
    borken = False
    for LINENUMBER, LINE in enumerate(CODE.split("\n"), LINEORIGIN):
        if not re.match(MACRO, LINE):
            for M in MACROS:
                LINE = LINE.replace(M, MACROS[M])
        if ROOSTN:
            ROOSTN -= 1
            continue
        if LINE != "":
            LINE = LINE.strip()
            if LINE in ops:
                ENDCHKN += ("chicken " * ops[LINE])[:-1] + "\n"
            else:
                N = re.match(PUSH, LINE)
                if not N:
                    X = re.match(CALL, LINE)
                    if not X:
                        W = re.match(MACRO, LINE)
                        if not W:
                            B = re.match(ROOST, LINE)
                            if not B:
                                Y = re.match(VARIABLE, LINE)
                                if not Y:
                                    Z = re.match(PICK, LINE)
                                    if not Z:
                                        C = re.match(PECK, LINE)
                                        if not C:
                                            borken = True
                                        else:
                                            ENDCHKN += transpile("push %s\npeck" % C[1], FILENAME, ROOT)
                                    else:
                                        ENDCHKN += transpile("push %s\npick" % Z[1], FILENAME, ROOT)
                                else:
                                    name  = Y["name"]
                                    index = Y["index"]
                                    value = Y["value"]
                                    if name not in VARS and index == None or name in names:
                                        cprint(ERROR, "\nError: Variable %r not defined on line %d in file %r" % (name, LINENUMBER, FILENAME))
                                        suggestions = fuzzyMatchesIn(name, VARS)
                                        if suggestions:
                                            cprint(ERROR, "Alternate Suggestions:", *suggestions, sep="\n\t")
                                        borken = True

                                    if name in VARS and index != None:
                                        cprint(WARNING, "\nWarning: Variable index of %r redefined on line %d, may have unexpected results." % (name, LINENUMBER))

                                    if index != None:
                                        index = int(index)
                                        VARS[name] = index

                                    if name in VARS.keys():
                                        if value == None and index == None:                                     # caseSensitiveVariableName([x])
                                            ENDCHKN += transpile("push %d\npick\naxe" % VARS[name], FILENAME, ROOT)
                                        elif value == "Top":                                                    # caseSensitiveVariableName([x]) = Top
                                            ENDCHKN += transpile("push %d\npeck" % (VARS[name]), FILENAME, ROOT)
                                        else:                                                                   # caseSensitiveVariableName([x]) = "anything else"
                                            ENDCHKN += transpile("push %s\npush %d\npeck" % (value, VARS[name]), FILENAME, ROOT)
                            else:
                                procCode = getProc(CODE, LINENUMBER, FILENAME, ROOT)
                                ROOSTN = procCode[0]
                                ROOSTS[B["name"]] = procCode[1]
                        else:
                            if W["replace"] in MACROS:
                                cprint(WARNING, "\nWarning: Macro %r redefined on line %d as %r" % (
                                    W["replace"] + " as " + MACROS[W["replace"]],
                                    LINENUMBER,
                                    W["replace"] + " as " + W["replacement"])
                                )
                            MACROS[W["replace"]] = W["replacement"]

                    else:
                        if X[1] in ROOSTS:
                            ENDCHKN += ROOSTS[X[1]]
                            continue
                        CALLNAME = X[1].replace(".", "\\") + ".eggs"
                        LIBFILE = FILEPATH(CALLNAME)
                        try:
                            with open(LIBFILE, "r") as CALLFILE:
                                CALLCHKN = transpile(re.sub(COMMENT, "", CALLFILE.read()), CALLNAME, ROOT)
                                ENDCHKN += CALLCHKN
                        except FileNotFoundError:
                            try:
                                with open(ROOT + CALLNAME, "r") as CALLFILE:
                                    CALLCHKN = transpile(re.sub(COMMENT, "", CALLFILE.read()), CALLNAME, ROOT)
                                    ENDCHKN += CALLCHKN
                            except FileNotFoundError:
                                borken = True
                                cprint(ERROR, "\nError: Neither file %r nor function %r exists, called on line %d" % (ROOT + CALLNAME, X[1], LINENUMBER))
                                suggestions = fuzzyMatchesIn(X[1], ROOSTS)
                                if suggestions:
                                    cprint(ERROR, "Alternate Function Suggestions:", *suggestions, sep="\n\t")
                else:
                    if '"' in LINE or "'" in LINE:
                        STRING = N["str"]
                        STRING = STRING.replace("\\r", "")
                        STRING = STRING.replace("\\n", "\n")
                        STRING = re.sub(r"\\([ -~])", r"\1", STRING)
                        for x, i in enumerate(STRING):
                            ENDCHKN += transpile(symbolCodes[i], FILENAME, ROOT)
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
    return ENDCHKN.lstrip("\n") * (not borken)


VALIDCODE = re.compile(r"^(?:(?:push[ \t]*(?:(?: [+-]?\d+| [+-]?(?:\d+\.\d*|\d*\.\d+))|(?P<quote>[\"'])(?:(?=(?P<slash>\\?))(?P=slash)[ -~])*?(?P=quote)))|^(?:pick \d+)$|^(?:hatch [A-Za-z0-9_\.]+)$|(?:[A-Za-z_][A-Za-z0-9_]*(?:\[\d+\])?(?:\s*?=\s*?(?:Top|(?P<assquote>[\"'])(?:(?=(?P<ASSslash>\\?))(?P=ASSslash)[ -~])*?(?P=assquote)|[0-9]+))?)|(?:[^ \t]+.+ +[Aa]s +.+)|\n|)$|^build[ \t]+[A-Za-z_][A-Za-z0-9_]*[ \t]*{[ \t]*$|^}$")
def validate(CODE, FILENAME, ROOT):
    borken = False
    for LINENUMBER, LINE in enumerate(CODE.split("\n"), 1):
        LINE = LINE.strip()

        if not re.match(VALIDCODE, LINE):
            cprint(ERROR, "\nError: Invalid command on line %d in file %s: %s" % (LINENUMBER, repr(FILENAME), repr(LINE)))
            borken = True

    return not borken
