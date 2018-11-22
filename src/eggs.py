import argparse

parser = argparse.ArgumentParser(description="Take Eggsembly file (.eggs) and run it.")
parser.add_argument("-t", "--transpile", type=str, metavar="file", default="",
                    help="A file name. If specified, a Chicken file (.chkn) equivalent to the Eggsembly file given will be generated and saved instead.")
parser.add_argument("-c", "--compile", type=str, metavar="file", default="",
                    help="A file name. If specified, a Chicken bytecode file (.chkc) equivalent to the Eggsembly file given will be compiled and saved instead. (this can be used to be run by the standalone chkc executable without compiling.)")
parser.add_argument("file", metavar="file", type=str, nargs=1,
                    help="Eggsembly file to run.")

args = parser.parse_args()

import re, os.path

COMMENT = re.compile(
    r"""(?<![A-Za-z0-9\ \"\'])([\ \t]*//.*?\n)|([\ \t]*//.*?(?=\n))|(?<![A-Za-z0-9\ \"\']])([\ \t]*/\*.*?(?:(?=\*/)\*/|$)\n*)|([\ \t]*/\*.*?(?:(?=\*/)\*/|$))(?=\n*)|(?<![A-Za-z0-9\ \"\'])([\ \t]*~~\[==.*?(?:(?===\]~~)==\]~~|$)\n*)|([\ \t]*~~\[==.*?(?:(?===\]~~)==\]~~|$))(?=\n*)""",
    re.S)
try:
    FILE = open(args.file[0], "r")
except FileNotFoundError:
    print(repr(args.file[0]), "does not exist.")
else:
    FULLTXT = FILE.read()
    ENDEGGS = re.sub(COMMENT, "", FULLTXT)

    if len(ENDEGGS.strip()) == 0:
        print("\nEmpty file given:", repr(args.file[0]))
    else:
        import eggs2chkn
        ROOT = "/".join(args.file[0].split("/")[:-1]) + "/"
        valid = eggs2chkn.validate(ENDEGGS, args.file[0], ROOT)
        ENDCHKN = eggs2chkn.transpile(ENDEGGS, args.file[0], ROOT)
        if ENDCHKN:
            if args.transpile:
                CHKNFILE = open(args.transpile + [".chkn", ""][args.transpile.endswith(".chkn")], 'w')
                CHKNFILE.write(ENDCHKN)
                CHKNFILE.close()
            #
            # from bytes import randomFile, parse
            # import os
            # OPs = parse(ENDCHKN)
            # if OPs:
            #     if args.compile:
            #         with open(args.compile + [".chkc", ""][args.compile.endswith(".chkc")], 'wb') as f:
            #             f.write(OPs.encode('utf-8'))
            #             f.close()
            #     else:
            #         try:
            #             inp =  input("Input: ")
            #             with randomFile('wb') as f:
            #                 fileName = f.name
            #                 f.write(OPs.encode('utf-8'))
            #                 f.close()
            #         finally:
            #             import os.path, inspect
            #             os.system("./" + "\\".join(inspect.getfile(inspect.currentframe()).split("/")[:-1]) + "/chkc %r %r" % (fileName, inp))
            #             os.remove(fileName)
            else:
                if valid and ENDEGGS:
                    from vm import Machine
                    VM = Machine(bbq_compat=False)
                    VM.load_str(ENDCHKN)
                    VM.load_input(input("Input: "))
                    print(VM.run())
                    print(VM.stack)
