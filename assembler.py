#!/usr/bin/python3

"""Assembles bytecode file.

Source must be specified in first argument.
Assembled file saves in source directory with .zl extension"""
from opcodes import opcodes
import os, sys, struct

# format for struct.pack function. Change '<' to '>' to change byte order
fmt = '<i'
command_length = 4

def die(message, linenum = None):
    """Print error message and exit with status 1"""
    print('Error: ' + message + \
          (' at line ' + str(linenum + 1) if linenum != None else '') + \
          ', exiting')
    sys.exit(1)

if len(sys.argv) < 2:
    die('not specified input file, please specify it in first argument')

output = bytearray()

class Label:
    """Describes one label"""
    def __init__(self):
        self.transitions = []
        self.address = -1
        
labels = {}

class Var():
    """Describes one global variable"""
    def __init__(self, size):
        self.links = []
        self.size = size

vars_dict = {}

print('Assembling...')
with open(sys.argv[1]) as source_file:
    for linenum, line in enumerate(source_file):
        line = line.strip()
        if not line:
            continue
        if line[0] in ('#', '/'):   # comment
            continue
        command, *arguments = line.split()
        command = command.upper()
        # print('command = ' + command + ' arguments[0] = ' + \
        #       (arguments[0] if len(arguments) > 0 else  ''))
        if command[0] == ':':   # label
            label_name = command[1:]
            if label_name not in labels:
                labels[label_name] = Label()
            # it's important to remember that addressing
            # in stack-machine performed by dwords, not by bytes.
            # the smallest element that can be addressed is dword (integer).
            # it's the reason why in next line offset divides by command len.
            labels[label_name].address = len(output) // command_length
            continue
        if command == 'VAR':    # global variable declaration
            if len(arguments) < 1:
                die('need var name', linenum)
            var = arguments[0]
            size = 1
            if len(arguments) > 1:  # array
                try:
                    size = int(arguments[1])
                except ValueError:
                    die('bad array ' + var + ' size: must be int', linenum)
                if size < 1:
                    die(var + 'negative or zero size of array', linenum)
            vars_dict[var] = Var(size)
            continue
        if command not in opcodes:
            die('Unknown command ' + command, linenum)
        # adding opcode to output
        # this line executes for all vm commands
        output += struct.pack(fmt, opcodes.index(command))
        # opcode added to output and now time to do some additional steps
        if command in ('JMP', 'JE', 'JL', 'JG', 'JNE', 'JLE', 'JGE', 'CALL'):
            if not arguments:
                die(command + ' needs 1 argument', linenum)
            label_name = arguments[0].upper()
            if label_name[0] == ':':
                label_name = label_name[1:]
            if label_name not in labels:
                labels[label_name] = Label()
            labels[label_name].transitions.append(len(output))
            output += struct.pack(fmt, 0) # temporarily add 0 instead of addr
        if command in ('PUSH', 'FROMMEM', 'TOMEM', 'AFROMMEM', 'ATOMEM'):
            if not arguments:
                die(command + ' needs 1 argument', linenum)
            if arguments[0][0].isnumeric():
                try:
                    val = int(arguments[0])
                except ValueError:
                    die(command + ' bad command argument', linenum)
                output += struct.pack(fmt, val)
            else:
                var = arguments[0]
                if var not in vars_dict:
                    die('undefined global variable ' + var, linenum)
                vars_dict[var].links.append(len(output))
                output += struct.pack(fmt, 0) # temporarily add 0
        if command == 'DUP':
            if not arguments:
                output += struct.pack(fmt, 1)
            else:
                try:
                    output += struct.pack(fmt, int(arguments[0]))
                except ValueError:
                    die(command + ' bad command argument', linenum)
    # explicitly quit when program ends
    output += struct.pack(fmt, opcodes.index('QUIT'))
if labels:
    print('labels:')
    for x in labels:
        print('\t', x)
if vars_dict:
    print('variables:')
    for x in vars_dict:
        print('\t', x, '\t', vars_dict[x].size)
# now we know all labels addresses and
# can write correct address to every j* and call command
for label in labels:
    if labels[label].address == -1:
        die('needs ' + label + ' label')
    for transition in labels[label].transitions:
        output[transition : transition + command_length] = \
                          struct.pack(fmt, labels[label].address)
# now we can allocate space for all global variables and arrays.
# this space will be allocated in bytecode file, after the code.
# and we can write correct variable address in all places where
# these variable requires
for var in vars_dict:
    for link in vars_dict[var].links:
        output[link : link + command_length] = \
                    struct.pack(fmt, len(output) // command_length)
    for x in range(vars_dict[var].size):
        output += struct.pack(fmt, 0)
        
out_file = sys.argv[1] + '.zl'

with open(out_file, 'bw') as output_file:
    output_file.write(output)
    
print('Bytecode size:', len(output))
print('Launching...\n')

import platform
if platform.system() == 'Linux':
	command_to_launch = os.path.join(os.path.abspath(os.path.dirname( \
                     sys.argv[0])), 'stack_machine')
	os.system(command_to_launch + ' ' + out_file + '')
else: # windows
	command_to_launch = os.path.join(os.path.abspath(os.path.dirname( \
                     sys.argv[0])), 'stack_machine.exe')
	os.system('""' + command_to_launch + '" "' + out_file + '""')

