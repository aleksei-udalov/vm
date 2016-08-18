#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define MEM_SIZE 4096        // bytecode loads in memory at 0 address, and 0 address takes control
#define ST_SIZE 2048         // separated stack to make calculations
#define CALL_ST_SIZE 2048    // call stack to store return addresses
#define COMMAND_LEN 4

int mem[MEM_SIZE];
int c_cur;                  // code cursor. "instruction pointer" in x86 terminology
int stack[ST_SIZE];         // real size in bytes is ST_SIZE * sizeof(int)
int st_cur;                 // stack cursor. x86 architecture don't have a similar concept
int call_stack[CALL_ST_SIZE];
int call_st_cur;            // call stack cursor. "stack pointer" in x86 terminology
int fl_eq;                  // equality flag
int fl_gr;                  // greater flag. These two partially simulates x86 FLAGS register
long long int tacts_counter;

void
die(char* message)
{
    printf("Error: %s at 0x%x, exiting\n", message, c_cur*COMMAND_LEN);
    exit(1);
}

void
inc_c_cur()
{
    if (c_cur + 1 >= MEM_SIZE)
        die("unexpected end of code");
    c_cur++;
}

void
inc_st_cur()
{
    if (st_cur == ST_SIZE - 1)
        die("stack overflow");
    st_cur++;
}

void
dec_st_cur()
{
    if (st_cur == -1)
        die("pop from empty stack");
    st_cur--;
}

void
push()
{
    inc_c_cur();
    inc_st_cur();
    stack[st_cur] = mem[c_cur];
}

void
pop()
{
    dec_st_cur();
}

void
print()
{
    if (st_cur == -1)
        printf("Stack is empty, continue...\n");
    else
        printf("Value: 0x%x or %i\n", stack[st_cur]);
}

void
add()
{
    if (st_cur < 1)
        die("not enough elements in stack for addition");
    stack[st_cur - 1] = stack[st_cur - 1] + stack[st_cur];
    dec_st_cur();
}

void
sub()
{
    if (st_cur < 1)
        die("not enough elements in stack for subtraction");
    stack[st_cur - 1] = stack[st_cur - 1] - stack[st_cur];
    dec_st_cur();
}

void
mult()
{

    if (st_cur < 1)
        die("not enough elements in stack for mult");
    stack[st_cur - 1] = stack[st_cur - 1] * stack[st_cur];
    dec_st_cur();
}

void
divide()
{

    if (st_cur < 1)
        die("not enough elements in stack for divide");
    stack[st_cur - 1] = stack[st_cur - 1] / stack[st_cur];
    dec_st_cur();
}

void
succ_exit()
{
    /* If you using gcc maybe you need to replace %I64i with %lli
    to correctly output tacts and time */
    printf("End of program, success\nTacts: %I64i, time: %.3f\n", \
           tacts_counter, (clock() * 1.0) / CLOCKS_PER_SEC);
    exit(0);
}

void
jmp()
{
    inc_c_cur();
    c_cur = mem[c_cur] - 1;
    if (c_cur >= MEM_SIZE || c_cur < -1)
        die("segmentation fault after jmp");
}

void
cmp()
{
    if (st_cur < 1)
        die("not enough elements in stack for cmp");
    if (stack[st_cur - 1] == stack[st_cur])
    {
        fl_eq = 1;
        fl_gr = 0;
    }
    else
    {
        fl_eq = 0;
        if (stack[st_cur - 1] > stack[st_cur])
            fl_gr = 1;
        else
            fl_gr = 0;
    }
}

void
je()
{
    inc_c_cur();
    if (fl_eq == 1)
    {
        c_cur = mem[c_cur] - 1;
        if (c_cur >= MEM_SIZE || c_cur < -1)
            die("Segmentation fault after je");
    }
}

void
jne()
{
    inc_c_cur();
    if (fl_eq == 0)
    {
        c_cur = mem[c_cur] - 1;
        if (c_cur >= MEM_SIZE || c_cur < -1)
            die("segmentation fault after jne");
    }
}

void
jl()
{
    inc_c_cur();
    if (fl_eq == 0 && fl_gr == 0)
    {
        c_cur = mem[c_cur] - 1;
        if (c_cur >= MEM_SIZE || c_cur < -1)
            die("segmentation fault after jl");
    }
}

void
jg()
{
    inc_c_cur();
    if (fl_gr == 1)
    {
        c_cur = mem[c_cur] - 1;
        if (c_cur >= MEM_SIZE || c_cur < -1)
            die("segmentation fault after jg");
    }
}

void
jle()
{
    inc_c_cur();
    if (fl_gr == 0)
    {
        c_cur = mem[c_cur] - 1;
        if (c_cur >= MEM_SIZE || c_cur < -1)
            die("segmentation fault after jle");
    }
}

void
jge()
{
    inc_c_cur();
    if (fl_eq == 1 || fl_gr == 1)
    {
        c_cur = mem[c_cur] - 1;
        if (c_cur >= MEM_SIZE || c_cur < -1)
            die("segmentation fault after jge");
    }
}

void
frommem()
{
    inc_c_cur();
    if (mem[c_cur] < 0 || mem[c_cur] >= MEM_SIZE)
        die("segmentation fault in frommem");
    inc_st_cur();
    stack[st_cur] = mem[mem[c_cur]];
}

void
tomem()
{
    inc_c_cur();
    if (mem[c_cur] < 0 || mem[c_cur] >= MEM_SIZE)
        die("segmentation fault in tomem");
    mem[mem[c_cur]] = stack[st_cur];
}

void
rfrommem()
{
    if (st_cur < 0)
        die("stack is empty, cannot rfrommem");
    if (stack[st_cur] < 0 || stack[st_cur] >= MEM_SIZE)
        die("segmentation fault in rfrommem");
    inc_st_cur();
    stack[st_cur] = mem[stack[st_cur -1]];
}

void
rtomem()
{
    if (st_cur < 1)
        die("Not enough elements in stack for rtomem");
    if (stack[st_cur -1] < 0 || stack[st_cur -1] >= MEM_SIZE)
        die("segmentation fault in rtomem");
    mem[stack[st_cur -1]] = stack[st_cur];
}

void
call()
{
    call_st_cur++;
    if (call_st_cur >= CALL_ST_SIZE)
        die("call stack overflow");
    call_stack[call_st_cur] = c_cur + 2;
    inc_c_cur();
    if (mem[c_cur] < 0 || mem[c_cur] >= MEM_SIZE)
        die("segmentation fault in call");
    c_cur = mem[c_cur] - 1;
}

void
ret()
{
    if (call_st_cur < 0)
        die("cannot ret: call stack is empty");
    if (call_stack[call_st_cur] < 0 || call_stack[call_st_cur] >= MEM_SIZE)
        die("segmentation fault in ret");
    c_cur = call_stack[call_st_cur] - 1;
    call_st_cur--;
}

void
dup()
{
    inc_c_cur();
    int num = mem[c_cur];
    if (num < 1)
        die("bad command dup argument");
    if (st_cur < num - 1)
        die("cannot dup: not enough values in stack");
    int i;
    for(i = 0; i < num; i++)
    {
        inc_st_cur();
        stack[st_cur]  = stack[st_cur - num];
    }
}

void
randint()
{
    inc_st_cur();
    stack[st_cur] = (rand() << 16) + rand() + rand() + rand() % 2;
}

void
swap()
{
    if (st_cur < 1)
        die("not enough elements in stack to swap");
    int t = stack[st_cur];
    stack[st_cur] = stack[st_cur - 1];
    stack[st_cur - 1] = t;
}

void
inc()
{
    if (st_cur < 0)
        die("cannot inc because stack is empty");
    stack[st_cur]++;
}

void
dec()
{
    if (st_cur < 0)
        die("cannot dec because stack is empty");
    stack[st_cur]--;
}

void
afrommem()
{
    if (st_cur < 0)
        die("stack is empty, cannot afrommem");
    inc_c_cur();
    if (stack[st_cur] + mem[c_cur] < 0 || stack[st_cur] + mem[c_cur] >= MEM_SIZE)
        die("segmentation fault in afrommem");
    inc_st_cur();
    stack[st_cur] = mem[stack[st_cur - 1] + mem[c_cur]];
}

void
atomem()
{
    if (st_cur < 1)
        die("Not enough elements in stack for atomem");
    inc_c_cur();
    if (stack[st_cur - 1] + mem[c_cur] < 0 || stack[st_cur - 1] + mem[c_cur] >= MEM_SIZE)
        die("segmentation fault in atomem");
    mem[stack[st_cur - 1] + mem[c_cur]] = stack[st_cur];
}

void
nop()
{
    ;
}

void
quit()
{
    succ_exit();
}

void
bp()
{
    printf("Breakpoint reached at 0x%x\n", c_cur);
    printf("Call stack depth: %i\n", call_st_cur + 1);
    printf("Stack depth: %i\n", st_cur + 1);
    printf("Stack content:\n");
    int i;
    for (i = st_cur; i >= 0; i--)
        printf("    0x%x\n", stack[i]);
    printf("Press enter to continue\n");
    getchar();
}

/* All handlers should be declared before including opcodes.h */
#include "opcodes.h"
int
main(int argc, char ** argv)
{
    FILE * bfile;
    srand(time(NULL));
    if (argc < 2)
        die("bytecode file not specified");
    printf("Bytecode file is: %s\n", argv[1]);
    bfile = fopen(argv[1], "r");
    if (bfile == NULL)
        die("cannot open bytecode file");
    fread(mem, COMMAND_LEN, MEM_SIZE, bfile);
    if (!feof(bfile))
        die("bytecode file too big");
    st_cur = -1;
    c_cur = 0;
    call_st_cur = -1;
    tacts_counter = 0;
    while (1)
    {
        tacts_counter++;
        int instruction = mem[c_cur];
        if (instruction < 0 || instruction >= OPCODES_COUNT)
            die("Unknown instruction");
        handlers[instruction]();
        inc_c_cur();
    }
}
