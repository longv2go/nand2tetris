#coding: utf-8
""" HACK language assembler
    Usage: Assembler input.asm > output.hack
"""

import sys
from enum import Enum
from predefines import predefined_symbols, dest_instruction_map, jump_instruction_map, comp_instruction_map_a0, comp_instruction_map_a1
import argparse

# SYMBOL TABLE 
_symbal_table = dict(predefined_symbols)
_current_variable_assign_addr = 16

class LineCode:
    def __init__(self, lineContent, lineNum):
        self.content = lineContent
        self.lineNum = lineNum
        self.striped = self.content.strip()

        self.code = None
        self.symbol = None   # (SSS) -> SSS
        self.parse()

    def getCode(self):
        return self.code
    
    def getSymbol(self):
        return self.symbol
    
    def getContent(self):
        return self.content
    
    def isEmpty(self):
        return len(self.striped) == 0
    
    def isComment(self):
        return self.striped.startswith("//") or self.striped.startswith("#")
    
    def isSymbolDef(self):
        return self.striped.startswith("(")

    def parse(self):
        if self.isComment():
            return
        
        # 处理 inline 注释
        idx = self.striped.find("//")
        code = str(self.striped)
        if idx != -1:
            code = self.striped[0:idx]
        self.code = code.strip()

        if self.isSymbolDef():
            self.symbol = self.code.strip("()")

    def __str__(self):
        return f"[{self.lineNum}]  {self.content.strip()}"

class Instruction:
    def __init__(self, lineCode):
        self.lineCode = lineCode
        self.code = lineCode.getCode()

        # c-instruction
        self.dest = ''
        self.comp = ''
        self.jump = ''

        # a-instruction
        self.addr = ''

        self.parse()

    def isAinstr(self):
        return self.code.startswith("@")
    
    def parse(self):
        # first: 处理 inline 注释
        idx = self.code.find("//")
        if idx != -1:
            self.code = self.code[0:idx]
        self.code = self.code.strip()

        # second: TODO: 处理 err， 不合法指令情况
        
        # parse
        if self.isAinstr():
            self.parseA()
        else:
            self.parseC()

    def parseA(self):
        self.addr = str(self.code).strip('@')
    
    def parseC(self):
        splited = self.code.split('=')
        if len(splited) != 1:
            self.dest = splited[0]
        else:
            self.dest = 'null'

        splited = splited[-1].split(';')
        if len(splited) != 1:
            self.jump = splited[1]
        else:
            self.jump = 'null'

        self.comp = splited[0]
        self.comp.replace(' ', '')
        
    def gen_code(self):
        """ 生成二进制 """
        global _current_variable_assign_addr
        if self.isAinstr():
            addr = self.addr
            if not addr.isnumeric():   # 查表
                if self.addr not in _symbal_table.keys():
                    # 处理 variables
                    _symbal_table[self.addr] = _current_variable_assign_addr
                    _current_variable_assign_addr += 1
                addr = _symbal_table.get(self.addr)

            # f-string 填充， 223 -> 0000000011011111
            # TODO: validate
            return f"{bin(int(addr))[2:]:0>16}"
        else: # c-instruction
            dest_key = ''.join(sorted(self.dest)) if self.dest != 'null' else self.dest
            dest = dest_instruction_map.get(dest_key) 
            if dest is None:
                raise Exception(f"Not found dest for {self.dest}, {self.lineCode}")
            
            jump = jump_instruction_map.get(self.jump)
            if jump is None:
                raise Exception(f"Not found jump for {self.jump}, {self.lineCode}")
            
            comp = comp_instruction_map_a0.get(self.comp)
            a = '0'
            if comp is None:
                a = '1'
                comp = comp_instruction_map_a1.get(self.comp)
                if comp is None:
                    raise Exception(f"Not found comp for '{self.comp}', {self.lineCode}")
                
            return f"111{a}{comp}{dest}{jump}"



###############################################################################
#                               Parse Stage
###############################################################################

def parse0(lines):
    """ 解析跳转符号，处理注释等等 """
    lineCodes = [LineCode(line, idx + 1) for idx, line in enumerate(lines)]

    # 使用 len(out) 当做当前执行的 command 行数
    def _get_current_pc():
        return len(out)
    
    out = []
    for code in lineCodes:
        if code.isComment() or code.isEmpty():
            continue
        if code.isSymbolDef():
            _symbal_table[code.getSymbol()] = _get_current_pc()
            continue
        out.append(code)
    
    return out

def parse1(lines):
    """ 解析每一行 instr  """
    return [Instruction(l) for l in lines]


###############################################################################
#                               Generate Stage
##############################################################################

def gen_codes(instrs, debug=False):
    """ 翻译二进制代码 """
    return [f"{inst.gen_code()}        ;{inst.lineCode}" if debug else inst.gen_code() for inst in instrs]

def print_symbol_table():
    print("\n")
    print("#################################")
    print("         Symbol Talbe            ")
    print("#################################")

    # 过滤常规的
    table = {k:v for k, v in _symbal_table.items() if not k.startswith('R') or not k[1:].isnumeric()}
    for k, v in table.items():
        print(f"{k:32}{str(v):>16}")

def main():
    parser = argparse.ArgumentParser(description='HACK assembler')
    parser.add_argument('--debug', action='store_true', default=False, help='output debug info')
    parser.add_argument('input', help="input file")
    args = parser.parse_args()
    
    with open(args.input) as f:
        lines = f.readlines()
        lines = parse0(lines)
        insts = parse1(lines)
        codes = gen_codes(insts, args.debug)

        # output to stdout
        for l in codes:
            print(l)
        if args.debug:
            print_symbol_table()

if __name__ == '__main__':
    main()
