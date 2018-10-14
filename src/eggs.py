import argparse

parser = argparse.ArgumentParser(description="Take Eggsembly file (.eggs) and run it.")
parser.add_argument("file", metavar="F", type=str, nargs=1,
                    help="Eggsembly file to run.")

args = parser.parse_args()

import re

COMMENT = re.compile(
    r"(?<![A-z0-9\ ])([\ \t]*//.*?\n)|([\ \t]*//.*?(?=\n))|(?<![A-z0-9\ ])([\ \t]*/\*.*?(?:(?=\*/)\*/|$)\n*)|([\ \t]*/\*.*?(?:(?=\*/)\*/|$))(?=\n*)|(?<![A-z0-9\ ])([\ \t]*~~\[==.*?(?:(?===\]~~)==\]~~|$)\n*)|([\ \t]*~~\[==.*?(?:(?===\]~~)==\]~~|$))(?=\n*)",
    re.S)
FILE = open(args.file[0], "r")
ENDTXT = re.sub(COMMENT, "", FILE.read())
INCOM = False

if len(ENDTXT.strip()) == 0:
    print("\nEmpty file given:", args.file[0])
else:
    SINGLELINECOMMENT = re.compile(r"[\t\ ]*//.*", re.S)
    VALIDCODE = re.compile(r"^((?:push\s\d+)|(?:axe|chicken|add|fox|rooster|compare|pick|peck|fr|bbq)|\n|)$")
    for LINENUMBER, LINE in enumerate(FILE):
        if "/*" in LINE and INCOM == False:
            INCOM = True
        elif "*/" in LINE and INCOM == True:
            INCOM = False
        elif not re.match(VALIDCODE, re.sub(SINGLELINECOMMENT, "", LINE)) and not INCOM:
            print("Invalid command on line " + str(LINENUMBER + 1) + ":", LINE)
            break
    else:
        ops = {'axe': 0, 'chicken': 1, 'add': 2, 'fox': 3, 'rooster': 4, 'compare': 5, 'pick': 6, 'peck': 7, 'fr': 8, 'bbq': 9}
        PUSH = re.compile(r"^(?:push )([0-9]+)$")
        ENDCHKN = ""
        for LINE in ENDTXT.split("\n"):
            if LINE != "":
                LINE = LINE.strip()
                if LINE in ops:
                    ENDCHKN += ("chicken " * ops[LINE])[:-1] + "\n"
                else:
                    N = re.match(PUSH, LINE)
                    if not N:
                        print("Something's mega wrong here, bud:", repr(LINE))
                        break
                    ENDCHKN += ("chicken " * (int(N[1]) + 10))[:-1] + "\n"
        else:
            from vm import Machine
            VM = Machine(bbq_compat=False)
            VM.load_str(ENDCHKN)
            VM.load_input(input("Input: "))
            print(VM.run())
