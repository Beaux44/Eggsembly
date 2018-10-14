import re
ops = {'axe': 0, 'chicken': 1, 'add': 2, 'fox': 3, 'rooster': 4, 'compare': 5, 'pick': 6, 'peck': 7, 'fr': 8, 'bbq': 9}
PUSH = re.compile(r"^(?:push )([0-9]+)$")
CALL = re.compile(r"^(?:call )([A-z0-9\.])")
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
                        CALLNAME = LINE.split()[1].replace(".", "/") + ".eggs"
                        with open(ROOT + CALLNAME, "r") as CALLFILE:
                            CALLCHKN = transpile(re.sub(re.compile(
                                r"""(?<![A-z0-9\ ])([\ \t]*//.*?\n)|([\ \t]*//.*?(?=\n))|(?<![A-z0-9\ ])([\ \t]*/\*.*?(?:(?=\*/)\*/|$)\n*)|([\ \t]*/\*.*?(?:(?=\*/)\*/|$))(?=\n*)|(?<![A-z0-9\ ])([\ \t]*~~\[==.*?(?:(?===\]~~)==\]~~|$)\n*)|([\ \t]*~~\[==.*?(?:(?===\]~~)==\]~~|$))(?=\n*)""",
                                re.S), "", CALLFILE.read()), CALLNAME, ROOT)
                            ENDCHKN += CALLCHKN
                else:
                    ENDCHKN += ("chicken " * (int(N[1]) + 10))[:-1] + "\n"
    else:
        return ENDCHKN.lstrip("\n")
    return ""


SINGLELINECOMMENT = re.compile(r"[\t\ ]*//.*|[\t \ ]*/\*.*", re.S)
VALIDCODE = re.compile(r"^((?:push \d+)|(?:call [A-z0-9_\.]+)|(?:axe|chicken|add|fox|rooster|compare|pick|peck|fr|bbq)|\n|)$")
def validate(CODE, FILENAME, ROOT):
    INCOM = False
    for LINENUMBER, LINE in enumerate(CODE.split("\n")):
        if re.match(CALL, LINE):

            CALLNAME = LINE.split()[1].replace(".", "/") + ".eggs"
            try:
                with open(ROOT + CALLNAME, "r") as CALLFILE:
                    if not validate(CALLFILE.read(), CALLNAME, ROOT):
                        return False
            except FileNotFoundError:
                print("%s does not exist, called on line %d:\n\t%s" % (repr(CALLNAME), LINENUMBER + 1, LINE))
                return False

        elif not re.match(VALIDCODE, re.sub(SINGLELINECOMMENT, "", LINE)) and not INCOM:
            print("Invalid command on line %d in file %s: %s" % (LINENUMBER + 1, repr(FILENAME), repr(LINE)))
            return False

        if "/*" in LINE and INCOM == False:
            INCOM = True

        if "*/" in LINE and INCOM == True:
            INCOM = False
    return True
