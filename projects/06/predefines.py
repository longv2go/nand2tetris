#coding: utf-8
""" 请参考 nand2tetirs 06 文档 """

predefined_symbols = {
    'SP': 0,
    'LCL': 1,
    'ARG': 2,
    'THIS': 3,
    'THAT': 4,
    'SCREEN': 0x4000,
    'KBD': 0x6000
}

# R0-R15 = 0-15
for i in range(16):
    key = str(i)
    predefined_symbols['R' + key] = i

# dest map, 如果 key 是多个字符，按照字母顺序，方便以后查找
dest_instruction_map = {
    'null': '000',
    'M': '001',
    'D': '010',
    'DM': '011',
    'A': '100',
    'AM': '101',
    'AD': '110',
    'ADM': '111'
}

# jump map
jump_instruction_map = {
    'null': '000',
    'JGT': '001',
    'JEQ': '010',
    'JGE': '011',
    'JLT': '100',
    'JNE': '101',
    'JLE': '110',
    'JMP': '111'
}

# for a=0
comp_instruction_map_a0 = {
    '0': '101010',
    '1': '111111',
    '-1': '111010',
    'D': '001100',
    'A': '110000',
    '!D': '001101',
    '!A': '110001',
    '-D': '001111',
    '-A': '110011',
    'D+1': '011111',
    'A+1': '110111',
    'D-1': '001110',
    'A-1': '110010',
    'D+A': '000010',
    'D-A': '010011',
    'A-D': '000111',
    'D&A': '000000',
    'D|A': '010101'
}

# 只是为了实现简便
comp_instruction_map_a0.update({
    '1+D': '011111',
    '1+A': '110111',
    'A+D': '000010',
    'A&D': '000000',
    'A|D': '010101'
})

# for a=1
comp_instruction_map_a1 = {k.replace('A', 'M'): v for (k, v) in comp_instruction_map_a0.items() if k.find('A') != -1}
