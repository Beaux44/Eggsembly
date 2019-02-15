from eggs2chkn import *
from vm import Machine

if __name__ != "__main__":
    print("tf m9")
    exit()

VM = Machine()
print("Have 3 consecutive empty lines to run.\n")
ENDCHKN = ""
lastLines = [" ", " "]


while True:
    line = input(">>> ")
    if line == "" and not any(lastLines):
        VM.load_str(ENDCHKN)
        VM.load_input(input("Input: "))
        if ENDCHKN:
            print(VM.run(), "\n", sep="")
        else:
            print()
        lastLines = [" ", " "]
        ENDCHKN   = ""
        SKIP      = 0
        VARS      = {"input": 1}
        MACROS    = {}
        ROOSTS    = {}
        VM        = Machine()
        continue

    Chicken = transpile(line, "<stdin>", "/")
    ENDCHKN += Chicken
    lastLines.pop(0)
    lastLines += [line]
