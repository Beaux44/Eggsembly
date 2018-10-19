import argparse

parser = argparse.ArgumentParser(description="Take Eggsembly file (.eggs) and run it.")
parser.add_argument("-t", "--transpile", type=str, metavar="file", default="",
                    help="A file name. If specified, a Chicken file (.chkn) equivalent to the Eggsembly file given will be generated and saved instead.")
parser.add_argument("file", metavar="file", type=str, nargs=1,
                    help="Eggsembly file to run.")

args = parser.parse_args()

import re

COMMENT = re.compile(
    r"""(?<![A-z0-9\ ])([\ \t]*//.*?\n)|([\ \t]*//.*?(?=\n))|(?<![A-z0-9\ ])([\ \t]*/\*.*?(?:(?=\*/)\*/|$)\n*)|([\ \t]*/\*.*?(?:(?=\*/)\*/|$))(?=\n*)|(?<![A-z0-9\ ])([\ \t]*~~\[==.*?(?:(?===\]~~)==\]~~|$)\n*)|([\ \t]*~~\[==.*?(?:(?===\]~~)==\]~~|$))(?=\n*)""",
    re.S)
try:
    FILE = open(args.file[0], "r")
except FileNotFoundError:
    print(repr(args.file[0]), "does not exist.")
else:
    FULLTXT = FILE.read()
    ENDEGGS = re.sub(COMMENT, "", FULLTXT)
    INCOM = False

    if len(ENDEGGS.strip()) == 0:
        print("\nEmpty file given:", repr(args.file[0]))
    else:
        import eggs2chkn
        ROOT = "/".join(args.file[0].split("/")[:-1]) + "/"
        if eggs2chkn.validate(FULLTXT, args.file[0], ROOT):
            ENDCHKN = eggs2chkn.transpile(ENDEGGS, args.file[0], ROOT)
            if ENDCHKN:
                if args.transpile:
                    CHKNFILE = open((args.transpile if args.transpile.endswith(".chkn") else args.transpile + ".chkn"), 'w')
                    CHKNFILE.write(ENDCHKN)
                    CHKNFILE.close()
                else:
                    from vm import Machine
                    VM = Machine()
                    VM.load_str(ENDCHKN)
                    VM.load_input(input("Input: "))
                    print(VM.run())
