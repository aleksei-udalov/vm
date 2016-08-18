"""Reads opcodes from opcodes.txt file at script directory"""
import os, sys
        
opcodes = []

fname = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),
                     'opcodes.txt')

with open(fname) as opcodes_file:
    for line in opcodes_file:
        if not line.strip():
            continue
        name = line.split()[0]
        opcodes.append(name)

