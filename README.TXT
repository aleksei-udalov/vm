A simple stack-based virtual machine.
See opcodes.txt for supported commands.

=================== About: =================== 

Language consists some instructions from x86 assembly, forth, and java bytecode. It hasn't strict architecture. Some commands are not necessary now. Some needful command are still not implemented. 

Assembler only converts mnemonics to opcodes and calculates labels and variables adresses.

Next stage is writing C subset compiler.

=================== Internals: =================== 

Machine has a call stack to save return addresses, a general stack to calculating, and the RAM. These two stacks and memory are implemented as 3 independent C arrays. All memory are writable and executable. All commands expect 'call' and 'ret' does not affect call stack. Bytecode loads in RAM at offset 0x0. Entry point at 0x0 too. Attempts to access addresses outside memory, and stacks overflows are trackes and intercepts, but integer overflows not. There no exceptions and exceptions handling - machine only terminates when any memory error occurred.
Only one data type supports for the present: signed integer.
Speed about 17 millions operations in second (tested at bubble_sort with 3000 elements and disabled output) on 1.6 GHz Intel Atom CPU.

=================== How to use: =================== 

Write some program (see below) and assemble it:

python assembler.py your_program.txt

assembler.py saves assembled code in file your_program.txt.zl and automatically launches:

STACK_MACHINE.exe your_program.txt.zl

or you can launch it manually.

If you have added any opcodes in opcodes.txt and have added relevant functions (with same name) in 
STACK_MACHINE.c you need to launch:

python gen_opcodes.py

to generate opcodes.h. Now you can recompile STACK_MACHINE.c. Possibly all old
programs (.zl) requires to be reassembled.

=================== Tests: =================== 

bubble_sort_vars, recursive_facktorial and quick_sort is available completed programs and tests for virtual machine and assembler. TODO: write a universal test program.

=================== Docs: =================== 

See opcodes.txt and this file.
'var' to declare a global variable. Variable must be declared before using.
'var x' or 'var x 1' to declare global signed integer variable x.
'var a 10' to declare array a which contains 10 signed integers. Virtual machine does not controls bounds of arrays.
':' to declare a label with symbol name. Label can be used as a function entry or as a label to transition. In the first case you possible needs ret command at the end of the fuction. For example:
:func
...
ret
call func
# or
call :func
:label
jmp label

Assembler automatically adds 'quit' at the end of the bytecode.

Comments must starts with '#' or '/' symbol. Or, if the comment placed after any instruction, it can starts with any symbol. For example:
# comment
/ comment
pop 		comment
print 		comment
var x 		comment	- it does not works!
var x 1 	comment	- it works
Comments often uses to show stack status in test programs.

Some examples:
var x
push 7		stack contains 7
tomem x		global value x = 7
pop		stack is empty
frommem x	stack contains 7
pop
push x		stack contains address of x in memory, not 7

var a 10
push 4		4
afrommem a	4, a[4]




