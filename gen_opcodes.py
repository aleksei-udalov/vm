"""Generates opcodes.h in current directory"""
from opcodes import opcodes

with open('opcodes.h', 'w') as opcodes_header:
    opcodes_header.write('/* This file generated by gen_opcodes.py script\n' +
                         'Please edit opcodes.txt instead of this file */\n') 
    opcodes_header.write('#define OPCODES_COUNT ' + str(len(opcodes)) + '\n')
    opcodes_header.write('/* This is an array of handlers\n' + \
                         'Position corresponds to opcode \n' + \
                         'This technique is called \'threaded code\'*/\n' +
                         'void (*handlers[OPCODES_COUNT])(void) = {\n')
    for num, opcode in enumerate(opcodes):
        opcodes_header.write('\t' + opcode.lower() + ',\t// ' + \
                             ("0x%x" % num) + '\n')
    opcodes_header.write('};\n')