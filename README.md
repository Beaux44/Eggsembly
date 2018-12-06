# Eggsembly
A multi-platform interpreter for the Eggsembly language, with comments added


## Standard Eggsembly commands
|   Name   |                                                                          Description                                                                           |
|:--------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|   axe    |                                              Execute all chickens, saves the front one and gives it to the user.                                               |
| chicken  |                                                             Push a "chicken" chicken into the pen.                                                             |
|   add    |                                                                    Add two front chickens.                                                                     |
|   fox    |                                                                  Subtract two front chickens.                                                                  |
| rooster  |                                                                  Multiply two front chickens.                                                                  |
| compare  |                                      Compare two front chickens for equality, push truthy or falsy chicken into the pen.                                       |
|   pick   |Double wide instruction. Next instruction indicates source to load from. 0 loads from pen, 1 loads from user input. Top chicken points to area to load into pen.|
|   peck   |                                         Top chicken points to area to place at. The chicken below that will be moved.                                          |
|    fr    |              Front chickens are a relative offset to jump to. The chicken below that is the condition. Jump only happens if condition is truthy.               |
|   bbq    |                            Interprets the front chicken as ASCII and places the corresponding character chicken into front of pen.                             |
|  push n  |                                                          Pushes the literal n chickens into the pen.                                                           |
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## Non-standard Eggsembly commands
|                   Name                      |                               Description                                 |
|:-------------------------------------------:|:-------------------------------------------------------------------------:|
|                    hatch                    |Call Eggsembly code from a function or another script, code is run on cluck|
|                   push x                    |         Pushes x onto the stack, x is either a string or integer          |
|caseSensitiveVariable([n])(="string"\|x\|Top)|               assign or push caseSensitiveVariable to stack               |
|                   a as b                    |                     Replace "a" with "b" in the code                      |
|             build roostName {}              |              Build [roost](TERMINOLOGY.md) named "roostName"              |
---------------------------------------------------------------------------------------------------------------------------

## Ideas for some things that could be done
|                       Todo                      |
|:-----------------------------------------------:|
|                  ~~Functions~~                  |
|                   ~~Imports~~                   |
|Eggsembly Shell (obviously to be called Eggshell)|
|             ~~Rewrite HelloWorld~~              |
|                 Package Manager                 |
|               ~~String Literals~~               |
|                    Division                     |
|                  ~~Variables~~                  |
|            ~~Variable Suggestions~~             |
|                   ~~Macros~~                    |
|                  If Statements                  |
|               Online Interpreter                |
