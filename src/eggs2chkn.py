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

symbolNames = {
        '&': 'ampersand',
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
CALL = re.compile(r"^[ \t]*cluck ([A-Za-z0-9\.]+)$")
COMMENT = re.compile(
    r"(?<![A-Za-z0-9\ \"\'])([\ \t]*//.*?\n)|([\ \t]*//.*?(?=\n))|(?<![A-Za-z0-9\ \"\']])([\ \t]*/\*.*?(?:(?=\*/)\*/|$)\n*)|([\ \t]*/\*.*?(?:(?=\*/)\*/|$))(?=\n*)|(?<![A-Za-z0-9\ \"\'])([\ \t]*~~\[==.*?(?:(?===\]~~)==\]~~|$)\n*)|([\ \t]*~~\[==.*?(?:(?===\]~~)==\]~~|$))(?=\n*)",
    re.S)
VARIABLE = re.compile(r"^(?:(?P<name>[A-Za-z0-9_]+)(?:\[(?P<index>\d+)\])?(?:\s*?=\s*?(?P<value>Top|(?P<assquote>[\"'])(?P<str>(?:(?=(?P<slash>\\?))(?P=slash)[ -~])*?)(?P=assquote)|\d+))?)$") # "assquote" is short for assignment quote :3
VARS     = {"input": 1}
MACRO    = re.compile(r"^(?P<replace>.+) +[Aa]s +(?P<replacement>.+)$", re.M)
MACROS   = {}
PROC     = re.compile(r"proc[ \t]+(?P<name>[A-Za-z_][A-Za-z0-9_]*)[ \t]*{")
PROCN    = 0
PROCS    = {}

def fuzzyMatchesIn(a, l):
    matches = {}
    a = a.lower()
    for b in l:
        m = SequenceMatcher(None, a, b.lower()).ratio()
        if m >= 0.5:
            matches[b] = m
    return [*map(lambda kv: kv[0], sorted(matches.items(), key=lambda kv: kv[1]))][::-1] # Sort suggestions by similarity

def getProc(CODE, LINENUMBER, FILENAME, ROOT):
    ENDCHKN = ""
    n = 1
    while CODE.split("\n")[LINENUMBER] != "}":
        ENDCHKN += transpile(CODE.split("\n")[LINENUMBER], FILENAME, ROOT, LINENUMBER+1)
        n += 1
        LINENUMBER += 1
    return (n, ENDCHKN)

def transpile(CODE, FILENAME, ROOT, LINEORIGIN=1):
    global VARS, MACROS, PROCN, PROCS
    ENDCHKN = ""
    borken = False
    for LINENUMBER, LINE in enumerate(CODE.split("\n"), LINEORIGIN):
        if not re.match(MACRO, LINE):
            for M in MACROS:
                LINE = LINE.replace(M, MACROS[M])
        if PROCN:
            PROCN -= 1
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
                            B = re.match(PROC, LINE)
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
                                PROCN = procCode[0]
                                PROCS[B["name"]] = procCode[1]
                        else:
                            if W["replace"] in MACROS:
                                cprint(WARNING, "\nWarning: Macro %r redefined on line %d as %r" % (
                                    W["replace"] + " as " + MACROS[W["replace"]],
                                    LINENUMBER,
                                    W["replace"] + " as " + W["replacement"])
                                )
                            MACROS[W["replace"]] = W["replacement"]

                    else:
                        if X[1] in PROCS:
                            ENDCHKN += PROCS[X[1]]
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
                                cprint(ERROR, "\nERROR: Neither file %r nor function %r exists, called on line %d" % (ROOT + CALLNAME, X[1], LINENUMBER))
                                suggestions = fuzzyMatchesIn(X[1], PROCS)
                                if suggestions:
                                    cprint(ERROR, "Alternate Function Suggestions:", *suggestions, sep="\n\t")
                else:
                    if '"' in LINE or "'" in LINE:
                        STRING = N["str"]
                        STRING = STRING.replace("\\r", "")
                        STRING = STRING.replace("\\n", "\n")
                        STRING = re.sub(r"\\([ -~])", r"\1", STRING)
                        for x, i in enumerate(STRING):
                            if i in symbolNames.keys():
                                ENDCHKN += transpile("cluck ASCII.symbol." + symbolNames[i], FILENAME, ROOT)
                            elif i.lower() in "abcdefghijklmnopqrstuvwxyz":
                                if i.isupper():
                                    ENDCHKN += transpile("cluck ASCII.upper." + i, FILENAME, ROOT)
                                else:
                                    ENDCHKN += transpile("cluck ASCII.lower." + i, FILENAME, ROOT)
                            else:
                                ENDCHKN += transpile("cluck ASCII." + i, FILENAME, ROOT)
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


VALIDCODE = re.compile(r"^(?:(?:push[ \t]*(?:(?: [+-]?\d+| [+-]?(?:\d+\.\d*|\d*\.\d+))|(?P<quote>[\"'])(?:(?=(?P<slash>\\?))(?P=slash)[ -~])*?(?P=quote)))|^(?:pick \d+)$|^(?:cluck [A-Za-z0-9_\.]+)$|(?:[A-Za-z_][A-Za-z0-9_]*(?:\[\d+\])?(?:\s*?=\s*?(?:Top|(?P<assquote>[\"'])(?:(?=(?P<ASSslash>\\?))(?P=ASSslash)[ -~])*?(?P=assquote)|[0-9]+))?)|(?:[^ \t]+.+ +[Aa]s +.+)|\n|)$|^proc[ \t]+[A-Za-z_][A-Za-z0-9_]*[ \t]*{[ \t]*$|^}$")
def validate(CODE, FILENAME, ROOT):
    borken = False
    for LINENUMBER, LINE in enumerate(CODE.split("\n"), 1):
        LINE = LINE.strip()

        if not re.match(VALIDCODE, LINE):
            cprint(ERROR, "\nError: Invalid command on line %d in file %s: %s" % (LINENUMBER, repr(FILENAME), repr(LINE)))
            borken = True

    return not borken
