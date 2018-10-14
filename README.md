# Eggsembly 1.0
A multi-platform interpreter for the Eggsembly language, with comments added


|   Name   | Description |
|:--------:|:-----------:|
|   axe    |Stop execution.|
| chicken  |Push the string "chicken" onto the stack._
|   add    |Add two top stack values.|
|   fox    |Subtract two top stack values.|
| rooster  |Multiply two top stack values.|
| compare  |Compare two top stack values for equality, push truthy or falsy result onto the stack|
|   pick   |Double wide instruction. Next instruction indicates source to load from. 0 loads from stack, 1 loads from user input. Top of stack points to address/index to load onto stack.|
|   peck   |Top of stack points to address/index to store to. The value below that will be popped and stored.|
|    fr    |Top of stack is a relative offset to jump to. The value below that is the condition. Jump only happens if condition is truthy.|
|   bbq    |Interprets the top of the stack as ascii and pushes the corresponding character.|
|   push   |Pushes the literal number n-10 onto the stack.|
--------------------------------

### Ideas for some things that could be done
|         Todo         |
|:--------------------:|
|       Functions      |
|        Imports       |
| Imports as Functions |
|    Eggsembly Shell   |
|~~Rewrite HelloWorld~~|
|    Package Manager   |
