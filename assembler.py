#!/usr/bin/python3
"""Assembles bytecode file.

Source must be specified in first argument.
Assembled file saves in source directory with .zl extension"""
from opcodes import opcodes
import os, sys, struct, platform

command_length = 4

class Bytecode:
    """Describes bytecode"""
    # format for struct.pack function. Change '<' to '>' to change byte order
    fmt = '<i'
    def __init__(self):
        self.bytecode = bytearray()
        
    def append(self, value):
        self.bytecode += struct.pack(self.fmt, value)
        
    def save(self, source):
        filename = source + '.zl'
        with open(filename, 'bw') as output_file:
            output_file.write(self.bytecode)
        print('Bytecode size:', len(self))
        return filename
    	
    def __len__(self):
        return len(self.bytecode)

    def __setitem__(self, addr, value):
    	self.bytecode[addr : addr + command_length] = struct.pack(self.fmt, value)
        

class Label:
    """Describes one label"""
    def __init__(self, name):
        self.transitions = []
        self.address = None
        self.name = name
        
    def set_transitions(self, bytecode):
        if self.address == None:
            die('needs ' + self.name + ' label')
        for transition in self.transitions:
            bytecode[transition] = self.address

class Var():
    """Describes one global variable"""
    def __init__(self, size):
        self.links = []
        self.size = size

    def set_links(self, bytecode):
        for link in self.links:
            bytecode[link] = len(bytecode) // command_length

    def allocate_space(self, bytecode):
        for x in range(self.size):
            bytecode.append(0)
        
def die(message, linenum = None):
    """Print error message and exit with status 1"""
    if linenum == None:
        print('Error: ' + message + ', exiting')
    else:
        print('Error: ' + message + ' at line ' + str(linenum + 1) + ', exiting')    
    sys.exit(1)

if len(sys.argv) < 2:
    die('not specified input file, please specify it in first argument')
bytecode = Bytecode()
labels = {}
vars = {}
source = sys.argv[1]
print('Assembling...')
with open(source) as source_file:
    for linenum, line in enumerate(source_file):
        line = line.strip()
        if not line or line[0] in ('#', '/'):   # blank line or comment
            continue
        command, *arguments = line.split()
        command = command.upper()
        if command[0] == ':':   # label
            label_name = command[1:]
            if label_name not in labels:
                labels[label_name] = Label(label_name)
            # it's important to remember that addressing
            # in stack-machine performed by dwords, not by bytes.
            # the smallest element that can be addressed is dword (integer).
            # it's the reason why in next line offset divides by command len.
            labels[label_name].address = len(bytecode) // command_length
            continue
        if command == 'VAR':    # global variable declaration
            if len(arguments) < 1:
                die('need var name', linenum)
            var = arguments[0]
            if len(arguments) > 1:  # array
                try:
                    size = int(arguments[1])
                except ValueError:
                    die('bad array ' + var + ' size: must be int', linenum)
                if size < 1:
                    die(var + 'negative or zero size of array', linenum)
            else: # just a variable
            	size = 1
            vars[var] = Var(size)
            continue
        if command not in opcodes:
            die('Unknown command ' + command, linenum)
        # adding opcode to output
        # this line executes for all vm commands
        bytecode.append(opcodes.index(command))
        # opcode added to output and now time to do some additional steps
        if command in ('JMP', 'JE', 'JL', 'JG', 'JNE', 'JLE', 'JGE', 'CALL'):
            if not arguments:
                die(command + ' needs 1 argument', linenum)
            label_name = arguments[0].upper()
            if label_name[0] == ':':
                label_name = label_name[1:]
            if label_name not in labels:
                labels[label_name] = Label(label_name)
            labels[label_name].transitions.append(len(bytecode))
            bytecode.append(0) # temporarily add 0 instead of label address
        if command in ('PUSH', 'FROMMEM', 'TOMEM', 'AFROMMEM', 'ATOMEM'):
            if not arguments:
                die(command + ' needs 1 argument', linenum)
            if arguments[0].isnumeric():
                val = int(arguments[0])
                bytecode.append(val)
            else:
                var = arguments[0]
                if var not in vars:
                    die('undefined global variable ' + var, linenum)
                vars[var].links.append(len(bytecode))
                bytecode.append(0) # temporarily add 0 instead of variable address
        if command == 'DUP':
            if not arguments:
                bytecode.append(1)
            else:
                try:
                    bytecode.append(int(arguments[0]))
                except ValueError:
                    die(command + ' bad command argument', linenum)
    # explicitly quit when program ends
    bytecode.append(opcodes.index('QUIT'))
if labels:
    print('labels:')
    for x in labels:
        print('\t', x)
if vars:
    print('variables:')
    for x in vars:
        print('\t', x, '\t', vars[x].size)
# now we know all labels addresses and
# can write correct address to every j* and call command
for label in labels.values():
    label.set_transitions(bytecode)
# now we can allocate space for all global variables and arrays.
# this space will be allocated in bytecode file, after the code.
# and we can write correct variable address in all places where
# these variable requires
for var in vars.values():
    var.set_links(bytecode)
    var.allocate_space(bytecode)

filename = bytecode.save(source)
print('Launching...\n')

if platform.system() == 'Linux':
	command_to_launch = os.path.join(os.path.abspath(os.path.dirname( \
                     sys.argv[0])), 'stack_machine')
	os.system(command_to_launch + ' ' + filename + '')
else: # windows
	command_to_launch = os.path.join(os.path.abspath(os.path.dirname( \
                     sys.argv[0])), 'stack_machine.exe')
	os.system('""' + command_to_launch + '" "' + filename + '""')

