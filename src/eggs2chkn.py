import re, inspect, os.path, colorama
from difflib import SequenceMatcher
colorama.init()

def cprint(color, *args, **kwargs):
    print(color, end="")
    print(*args, **kwargs)
    print(colorama.Fore.RESET + colorama.Back.RESET, end="")

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

PUSH = re.compile(r"^(?:push)((?: \d+|\d*\.\d*)|(?P<quote>[\"'])(?P<str>(?:(?=(?P<slash>\\?))(?P=slash)[ -~])*?)(?P=quote))$")
PICK = re.compile(r"^(?:pick )(\d+)$")
CALL = re.compile(r"^(?:cluck )([A-Za-z0-9\.]+)$")
COMMENT = re.compile(
    r"(?<![A-Za-z0-9\ \"\'])([\ \t]*//.*?\n)|([\ \t]*//.*?(?=\n))|(?<![A-Za-z0-9\ \"\']])([\ \t]*/\*.*?(?:(?=\*/)\*/|$)\n*)|([\ \t]*/\*.*?(?:(?=\*/)\*/|$))(?=\n*)|(?<![A-Za-z0-9\ \"\'])([\ \t]*~~\[==.*?(?:(?===\]~~)==\]~~|$)\n*)|([\ \t]*~~\[==.*?(?:(?===\]~~)==\]~~|$))(?=\n*)",
    re.S)
VARIABLE = re.compile(r"^(?:(?P<name>[A-Za-z0-9_]+)(?:\[(?P<index>\d+)\])?(?:\s*?=\s*?(?P<value>Top|(?P<assquote>[\"'])(?P<str>(?:(?=(?P<slash>\\?))(?P=slash)[ -~])*?)(?P=assquote)|\d+))?)$") # "assquote" is short for assignment quote :3
MACRO = re.compile(r"^(?P<replace>.+) +[Aa]s +(?P<replacement>.+)$", re.M)
VARS = {}
MACROS = {}

def varFuzzyMatches(a):
    matches = {}
    a = a.lower()
    for b in VARS:
        m = SequenceMatcher(None, a, b.lower()).ratio()
        if m >= 0.5:
            matches[b] = m
    return [*map(lambda kv: kv[0], sorted(matches.items(), key=lambda kv: kv[1]))] # Sort suggestions by similarity

def transpile(CODE, FILENAME, ROOT):
    ENDCHKN = ""
    borken = False
    for LINENUMBER, LINE in enumerate(CODE.split("\n"), 1):
        if not re.match(MACRO, LINE):
            for M in MACROS:
                LINE = LINE.replace(M, MACROS[M])
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
                            Y = re.match(VARIABLE, LINE)
                            if not Y:
                                Z = re.match(PICK, LINE)
                                if not Z:
                                    # print("Error: Something's mega wrong here, bud:\n\tOn line %d of file %s\n\t\t%s\n\n" % (LINENUMBER, repr(FILENAME), repr(LINE)))
                                    borken = True
                                else:
                                    ENDCHKN += transpile("push %s\npick" % Z[1], FILENAME, ROOT)
                            else:
                                name  = Y["name"]
                                index = Y["index"]
                                value = Y["value"]
                                if name not in VARS and index == None or name in names:
                                    cprint(colorama.Fore.LIGHTRED_EX, "\nError: Variable %r not defined on line %d in file %r" % (name, LINENUMBER, FILENAME))
                                    suggestions = varFuzzyMatches(name)
                                    if suggestions:
                                        cprint(colorama.Fore.LIGHTRED_EX, "Alternate Suggestions:", *suggestions, sep="\n\t")
                                    borken = True

                                if name in VARS and index != None:
                                    cprint(colorama.Fore.LIGHTYELLOW_EX, "\nWarning: Variable index of %r redefined on line %d, may have unexpected results." % (name, LINENUMBER))

                                if index != None:
                                    index = int(index)
                                    VARS[name] = index
                                if name in VARS.keys() and index != None:
                                    if value == None:                                                       # caseSensitiveVariableName([x])
                                        ENDCHKN += transpile("push %d\npick\naxe" % VARS[name], FILENAME, ROOT)
                                    elif value == "Top":                                                    # caseSensitiveVariableName([x]) = Top
                                        ENDCHKN += transpile("push %d\npeck" % (VARS[name]), FILENAME, ROOT)
                                    else:                                                                   # caseSensitiveVariableName([x]) = "anything else"
                                        ENDCHKN += transpile("push %s\npush %d\npeck" % (value, VARS[name]), FILENAME, ROOT)
                        else:
                            if W["replace"] in MACROS:
                                cprint(colorama.Fore.LIGHTYELLOW_EX, "\nWarning: Macro %r redefined on line %d as %r" % (
                                    W["replace"] + " as " + MACROS[W["replace"]],
                                    LINENUMBER,
                                    W["replace"] + " as " + W["replacement"])
                                )
                            MACROS[W["replace"]] = W["replacement"]

                    else:
                        CALLNAME = LINE.split()[-1].replace(".", "\\") + ".eggs"
                        LIBFILE = FILEPATH(CALLNAME)
                        try:
                            with open(LIBFILE, "r") as CALLFILE:
                                CALLCHKN = transpile(re.sub(COMMENT, "", CALLFILE.read()), CALLNAME, ROOT)
                                ENDCHKN += CALLCHKN
                        except FileNotFoundError:
                            with open(ROOT + CALLNAME, "r") as CALLFILE:
                                CALLCHKN = transpile(re.sub(COMMENT, "", CALLFILE.read()), CALLNAME, ROOT)
                                ENDCHKN += CALLCHKN
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
    if not borken:
        return ENDCHKN.lstrip("\n")
    return ""


VALIDCODE = re.compile(r"^(?:(?:push(?:(?: [+-]?\d+| [+-]?(?:\d+\.\d*|\d*\.\d+))|(?P<quote>[\"'])(?:(?=(?P<slash>\\?))(?P=slash)[ -~])*?(?P=quote)))|^(?:pick \d+)$|^(?:cluck [A-Za-z0-9_\.]+)$|(?:[A-Za-z_][A-Za-z0-9_]*(?:\[\d+\])?(?:\s*?=\s*?(?:Top|(?P<assquote>[\"'])(?:(?=(?P<ASSslash>\\?))(?P=ASSslash)[ -~])*?(?P=assquote)|[0-9]+))?)|(?:[^ \t]+.+ +[Aa]s +.+)|\n|)$")
def validate(CODE, FILENAME, ROOT):
    borken = False
    for LINENUMBER, LINE in enumerate(CODE.split("\n"), 1):
        if re.match(CALL, LINE):

            CALLNAME = LINE.split()[1].replace(".", "\\") + ".eggs"
            LIBFILE = FILEPATH(CALLNAME)
            if not os.path.isfile(LIBFILE):
                try:
                    with open(ROOT + CALLNAME, "r") as CALLFILE:
                        if not validate(CALLFILE.read(), CALLNAME, ROOT):
                            borken = True
                except FileNotFoundError:
                    cprint(colorama.Fore.LIGHTRED_EX, "\nError: %s does not exist, called on line %d:\n\t%s" % (repr(CALLNAME), LINENUMBER, LINE))
                    borken = True

        elif not re.match(VALIDCODE, LINE):
            cprint(colorama.Fore.LIGHTRED_EX, "\nError: Invalid command on line %d in file %s: %s" % (LINENUMBER, repr(FILENAME), repr(LINE)))
            borken = True

    return not borken
