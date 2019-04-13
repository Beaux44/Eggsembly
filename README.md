# Eggsembly
An interpreter for the Eggsembly language.

## FAQ
### What is Eggsembly?
Eggsembly is a programming language that aims to make programming in [Chicken](https://esolangs.org/wiki/chicken) easier, by providing built-in looping, conditional statements, and strings, along with other higher-level language functionality.

### How does it work?
Eggsembly code is compiled into equivalent Chicken code which can then be run using either the interpreter that's along side the compiler, or the [original version](http://web.archive.org/web/20180420010853/http://torso.me/chicken). The ability for the compiled code to be run by either version is not handled by the compiler, so you will need to design your code for the version you want to be able to run it. Some examples can be run on the original, some can only run on the packaged interpreter.

### How can I run an Eggsembly program?
You can either use the [Online Interpreter/IDE](https://eggsembly-online-interpreter--sheep44.repl.co) (currently with nearly 0% uptime!), [here](https://eggsembly-online-interpreter--sheep44.repl.co/?code=7dd4936e19785db7b61aca31d271eabf03c8db639f7f32e87c2d4e20)'s an example of a program I made using it; or, assuming you have a compatible version of Python *(tested and developed with 3.7)* and required modules, you can copy the [/src/](/src/) directory and use the `eggs.py` file to run or compile your program. You can run `py eggs.py -h` for help using it.

### How often is this updated?
Regular development is temporarily on hiatus while I revamp the parser, however it's generally whenever I want to update it; I'm not sure how often that is.

### What do you mean when you say "chickens?"
I have created a number of different terms regarding Eggsembly to make it ~~more confusing~~ easier to talk about. They can be found [here](TERMINOLOGY.md).

### What are the limits of Eggsembly?
Eggsembly is capable of doing anything theoretically possible to do in Chicken.

### Why?
Chicken

---

## Standard Eggsembly commands
|    Name    |                                                                          Description                                                                           |
|:----------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|   `axe`    |                                              Execute all chickens, saves the front one and gives it to the user.                                               |
| `chicken`  |                                                             Push a "chicken" chicken into the pen.                                                             |
|   `add`    |                                                                    Add two front chickens.                                                                     |
|   `fox`    |                                                                  Subtract two front chickens.                                                                  |
| `rooster`  |                                                                  Multiply two front chickens.                                                                  |
| `compare`  |                                      Compare two front chickens for equality, push truthy or falsy chicken into the pen.                                       |
|   `pick`   |Double wide instruction. Next instruction indicates source to load from. 0 loads from pen, 1 loads from user input. Top chicken points to area to load into pen.|
|   `peck`   |                                         Top chicken points to area to place at. The chicken below that will be moved.                                          |
|    `fr`    |              Front chickens are a relative offset to jump to. The chicken below that is the condition. Jump only happens if condition is truthy.               |
|   `bbq`    |                            Interprets the front chicken as ASCII and places the corresponding character chicken into front of pen.                             |
|  `push n`  |                                                          Pushes the literal n chickens into the pen.                                                           |


## Non-standard Eggsembly commands
|                    Name                       |                               Description                                 |
|:---------------------------------------------:|:-------------------------------------------------------------------------:|
|                    `hatch`                    |Call Eggsembly code from a function or another script, code is run on cluck|
|                   `push x`                    |         Pushes x onto the stack, x is either a string or integer          |
|`caseSensitiveVariable([n])(="string"\|x\|Top)`|               assign or push caseSensitiveVariable to stack               |
|                   `a as b`                    |                     Replace "a" with "b" in the code                      |
|             `build roostName {}`              |                       Build roost named "roostName"                       |


## Todo
- ~~Comments~~
- ~~Functions~~
- ~~Imports~~
- ~~Eggshell~~
- ~~Rewrite HelloWorld x4~~
- Package Manager
- ~~String Literals~~
- Float Literals *(being added with the new parser)*
- Division *(being added with new parser, kind of)*
- ~~Variables~~
- ~~Variable Suggestions~~
- ~~Macros~~
- If Statements *(being added with the new parser)*
- While Statements *(being added with the new parser)*
- ~~Online Interpreter~~
- Bytecode compilation
- Whatever else I want?

The online Interpreter/IDE can be found [here](https://eggsembly-online-interpreter--sheep44.repl.co) during the time in which
I bother to have it up; I'm working on getting a proper host for it. The current BNF syntax description can be found
[here](Eggsembly.bnf) if you care about it.
