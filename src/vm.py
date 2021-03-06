# All code in this file is from https://github.com/auscompgeek/chickenpie
# The only modifications I plan to make to this file are to better emulate
# all the Javascript functionality and nuances as to better emulate the
# original Chicken interpreter, and to handle Python errors such as
# IndexError more like Javascript would. (where Python would raise an
# IndexError, Javascript would simply return undefined)

import re, time

EXIT = 0
CHICKEN = 1
ADD = 2
FOX = SUBTRACT = 3
ROOSTER = MULTIPLY = 4
COMPARE = 5
PICK = LOAD = 6
PECK = STORE = 7
FR = JUMP = 8
BBQ = CHAR = 9

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

def get_name(opcode):
    return names[opcode] if opcode < 10 else 'push %d' % (opcode - 10)

def parse(prog):
    """Parse a Chicken program into bytecode."""

    OPs = []
    prog = prog.split('\n')
    for line in prog:
        OPs.append(line.count("chicken"))

    return OPs

try:
    input = raw_input
except NameError:
    pass


class Machine(object):
    """A Chicken VM.
    Attributes:
    - ip - instruction pointer
    - sp - stack pointer
    - stack
    - bbq_compat - whether BBQ internally uses HTML encoding like chicken.js
    - input_compat - False to dynamically read stdin when input is fetched
    """

    ip = None  # type: int
    sp = -1

    def __init__(self, input=None, code=None, bbq_compat=True, input_compat=True):
        self.stack = []
        self.push(self.stack)
        self.push(input)

        if code:
            self.load_str(code)

        self.bbq_compat = bbq_compat
        self.input_compat = input_compat

    def __iter__(self):
        return self

    def __next__(self):
        x = self.step()
        if x is None:
            raise StopIteration
        return x

    next = __next__

    def exec_op(self, opcode):
        """Execute an opcode."""

        if opcode == CHICKEN:
            self.push('chicken')

        elif opcode == ADD:
            a, b = self.pop(), self.pop()

            # JavaScript's + operator coerces to string if either operand is string
            if isinstance(a, str):
                b = stringify(b)
            elif isinstance(b, str):
                a = stringify(a)

            self.push(b + a)

        elif opcode == FOX:
            a, b = self.pop(), self.pop()

            # JavaScript's - operator coerces both operands to numbers

            if isinstance(b, str):
                b = numberify(b)
            if isinstance(a, str):
                a = numberify(a)

            # when JavaScript's ParseInt function fails to coerce the
            # string to an integer, it will return NaN, instead.
            if a == "NaN" or b == "NaN":
                self.push("NaN")
            else:
                self.push(b - a)

        elif opcode == ROOSTER:
            a, b = self.pop(), self.pop()
            self.push(a * b)
        elif opcode == COMPARE:
            a, b = self.pop(), self.pop()
            self.push(a == b)

        elif opcode == PICK:
            where = self.next_op()
            if where == 1:
                source = self.get_input()
            else:
                try:
                    source = self.stack[where]
                except IndexError:
                    source = "undefined"
            addr = self.pop()

            #self.push(source[addr])
            try:
                if source is self.stack and addr == 1:
                    self.push(self.get_input())
                elif source != "undefined":
                    self.push(source[addr])
                else:
                    self.push(source)
            except (IndexError, TypeError):
                self.push(None)

        elif opcode == PECK:
            addr = self.pop()
            self.set(addr, self.pop())

        elif opcode == FR:
            offset = self.pop()
            if self.pop():
                self.ip += offset

        elif opcode == BBQ:
            v = self.pop()
            if v == "NaN":
                self.push(" ")
            else:
                try:
                    self.push(chr(v))
                except TypeError:
                    print("RuntimeError: %s cannot be BBQ'd" % (repr(v)))

        else:
            self.push(opcode - 10)

    def get_input(self):
        """Get input, either previously loaded or from stdin."""

        if not self.input_compat and self.stack[1] is None:
            self.stack[1] = input()
        return self.stack[1]

    def get_output(self):
        """Get the program's output, if the program has finished."""

        out = self.look()
        if self.bbq_compat and isinstance(out, str) and '&#' in out:
            out = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), out)

        return out

    def has_loaded(self):
        """Check whether a Chicken program has been loaded."""
        return self.ip is not None

    def is_end(self):
        """Check whether we have finished executing."""
        return self.ip >= len(self.stack) or not self.peek()

    def load_file(self, filename):
        """Load a Chicken program from a file."""

        with open(filename) as f:
            self.load_str(f.read())

    def load_input(self, inp):
        """Load input from a string."""
        self.stack[1] = inp

    def load_str(self, code):
        """Load a Chicken program from a string."""

        bytecode = parse(code)
        self.stack += bytecode
        self.sp = len(self.stack)
        if self.ip is None:
            self.ip = 2

    def look(self):
        """Get the top value on the stack."""
        return self.stack[self.sp]

    def next_op(self):
        """Get the next instruction, advancing the instruction pointer."""

        opcode = self.peek()
        self.ip += 1
        return opcode

    def peek(self):
        """Get the next instruction."""
        return self.stack[self.ip]

    def push(self, val):
        """Push a value onto the stack."""

        self.sp += 1
        self.set(self.sp, val)

    def pop(self):
        """Pop a value off the stack."""

        val = self.stack[self.sp]
        self.sp -= 1
        return val

    def run(self):
        """Execute the loaded Chicken program."""
        try:
            while self.step():
                pass
        except Exception as e:
            print("Exception on line %d: %s" % (self.ip, e.__class__.__name__))
            print(self.stack[self.sp - 1], self.stack[self.sp], self.stack[self.sp + 1])
        finally:
            return self.get_output()

    def set(self, addr, value):
        l = len(self.stack)
        if addr == l:
            self.stack.append(value)
        elif addr > l:
            self.stack += [None] * (addr - l + 1)
            self.stack[addr] = value
        else:
            self.stack[addr] = value

    def step(self):
        """Execute the next instruction.
        Returns the advanced IP and the last executed opcode.
        """

        if not self.has_loaded():
            raise RuntimeError('No Chicken program has been loaded.')

        if self.is_end():
            return None

        opcode = self.next_op()
        self.exec_op(opcode)
        return self.ip, opcode


def stringify(o):
    if o is None:
        return 'undefined'
    return str(o)

INTEGER = re.compile(r"\s*([+-]?\d+)\s*")
def numberify(o):
    try:
        return int(o)
    except:
        try:
            return float(o)
        except:
            return "NaN"
