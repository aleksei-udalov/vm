/* This file generated by gen_opcodes.py script
Please edit opcodes.txt instead of this file */
#define OPCODES_COUNT 31
/* This is an array of handlers
Position corresponds to opcode 
This technique is called 'threaded code'*/
void (*handlers[OPCODES_COUNT])(void) = {
	nop,
	push,
	pop,
	print,
	add,
	sub,
	mult,
	divide,
	quit,
	jmp,
	cmp,
	je,
	jl,
	jg,
	jne,
	jle,
	jge,
	frommem,
	tomem,
	rfrommem,
	rtomem,
	call,
	ret,
	dup,
	randint,
	swap,
	inc,
	dec,
	afrommem,
	atomem,
	bp,
};