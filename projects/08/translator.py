#coding: utf-8
"""
"""

import os
import argparse
from pathlib import PurePath
from enum import Enum, auto

class LineCode:
    def __init__(self, line, lineNum, filename):
        self.line = line
        self.lineNum = lineNum
        self.filename = filename
    
    def getLine(self):
        return self.line
    
    def __str__(self):
        return f"[{self.lineNum}]  {self.line.strip()}" 

class CmdType(Enum):
    C_COMMENT = auto()
    C_ARITHMETIC = auto()

    C_PUSH = auto()
    C_POP = auto()

    C_LABEL = auto()
    C_IF = auto()
    C_GOTO = auto()

    C_CALL = auto()
    C_FUNCTION = auto()
    C_RETRUN = auto()


_ARITHMETIC_CMD = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']
_TypeInstructionMap = {
    'push': lambda *args: PushInstruction(*args),
    'pop' : lambda *args: PopInstruction(*args),
    'label': lambda *args: BranchInstruction(*args),
    'goto': lambda *args: BranchInstruction(*args),
    'if-goto': lambda *args: BranchInstruction(*args),
    'call': lambda *args: CallInstruction(*args),
    'function': lambda *args: FunctionInstruction(*args)
}

class Instruction:
    """指令"""
    def __init__(self, parts, lineCode):
        self.parts = parts # 指令的不同部分
        self.lineCode = lineCode
        self.validate()

    def validate(self):
        return

    def type(self):
        """ 指令类型"""
        return self.type

    def translate(self, **funcs):
        pass

    @classmethod
    def create(cls, line, lineNum, filename):
        """ 创建具体的指令，包含注释 """
        striped = line.strip()
        if len(striped) == 0 or striped.startswith("//") or striped.startswith("#"):
            return Comment([], LineCode(line, lineNum, filename))

        # 处理 inline 注释
        idx = striped.find("//")
        if idx != -1:
            striped = striped[0:idx]
        
        parts = striped.split()
        if parts[0] in _ARITHMETIC_CMD:
            return ArithmeticInstruction(parts, LineCode(line, lineNum, filename))

        l = _TypeInstructionMap.get(parts[0])
        if l is None:
            raise Exception(f"Not supported instruction")

        return l(parts, LineCode(line, lineNum, filename))

# 目前的 Hack 指令生成放在 instruction 类里面，应该放到 writer 里面，让 writer 去面向 hack
class Comment(Instruction):
    def __init__(self, parts, lineCode):
        super().__init__(parts, lineCode)
    
    def translate(self, **funcs):
        return self.lineCode.getLine()

class ArithmeticInstruction(Instruction):
    def __init__(self, parts, lineCode):
        super().__init__(parts, lineCode)
        self.type = CmdType.C_ARITHMETIC

    def translate(self, **funcs):
        _map = {'add': '+', 'sub': '-', 'and': '&', 'or': '|', 'eq': '-', 'gt': '-', 'lt': '-'}
        if self.parts[0] in _map.keys():
            return f"""
                // {self.lineCode}
                @SP     // sp--
                M=M-1
                @SP     // D = *sp
                A=M
                D=M
                @SP     // *(sp-1) = x - y
                A=M-1   
                M=M{_map[self.parts[0]]}D
            """
        
        if self.parts[0] == 'not':
            return f"""
                // {self.lineCode}
                @SP     // D = *sp
                A=M
                D=M
                @SP     // *(sp-1) = x - y
                A=M-1   
                M=!D
            """
        
        if self.parts[0] == 'neg':
            return f"""
                // {self.lineCode}
                @SP     // D = *sp
                A=M
                D=M
                @SP     // *(sp-1) = x - y
                A=M-1   
                M=-D
            """

class PushInstruction(Instruction):
    def __init__(self, parts, lineCode):
        super().__init__(parts, lineCode)
        self.type = CmdType.C_PUSH

    def validate(self):
        if len(self.parts) < 2:
            raise Exception(f"Invalid push, {self.lineCode}")

    def translate(self, **funcs):
        if self.parts[1] == 'constant':
            return f"""
                // {self.lineCode}
                @{self.parts[2]}
                D=A
                @SP
                A=M
                M=D
                @SP
                M=M+1
            """
        
        _map = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that': 'THAT'}
        if self.parts[1] in _map.keys():
            return f"""
                // {self.lineCode}
                @{_map[self.parts[1]]}
                A=M+{self.parts[2]}
                D=M
                @SP
                A=M
                M=D
                @SP // sp = sp + 1
                M=M+1
            """

        if self.parts[1] == 'static':
            func = funcs['static_symbol']
            sym = func(self.lineCode.filename)
            return f"""
                // {self.lineCode}
                @{sym}
                D=M
                @SP
                A=M
                M=D
                @SP
                M=M+1
            """
        if self.parts[1] == 'temp':
            return f"""
                // {self.lineCode}
                @{self.parts[2]}
                A=M+5
                D=M
                @SP
                A=M
                M=D
                @SP
                M=M+1
            """
        # TODO: pointer


class PopInstruction(Instruction):
    def __init__(self, parts, lineCode):
        super().__init__(parts, lineCode)
        self.type = CmdType.C_POP
    
    def validate(self):
        if len(self.parts) < 2:
            raise Exception(f"Invalid push, {self.lineCode}")

        if self.parts[1] == 'constant':
            return Exception(f"Invalid pop, {self.lineCode}")
    
    def translate(self, **funcs):    
        _map = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that': 'THAT'}
        if self.parts[1] in _map.keys():
            return f"""
                // {self.lineCode}
                @SP
                A=M
                D=M
                @{_map[self.parts[1]]}
                A=M+{self.parts[2]}
                M=D
                @SP // sp = sp - 1
                M=M-1
            """

        if self.parts[1] == 'static':
            func = funcs['static_symbol']
            sym = func(self.lineCode.filename)
            return f"""
                // {self.lineCode}
                @SP
                A=M
                D=M
                @{sym}
                M=D
                @SP
                M=M-1
            """
        if self.parts[1] == 'temp':
            return f"""
                // {self.lineCode}
                @SP
                A=M
                D=M
                @{self.parts[2]}
                A=M+5
                M=D
                @SP
                M=M-1
            """
        # TODO: pointer

class BranchInstruction(Instruction):
    def __init__(self, parts, lineCode):
        super().__init__(parts, lineCode)

class CallInstruction(Instruction):
    def __init__(self, parts, lineCode):
        super().__init__(parts, lineCode)

class ReturnInstruction(Instruction):
    def __init__(self, parts, lineCode):
        super().__init__(parts, lineCode)

class FunctionInstruction(Instruction):
    def __init__(self, parts, lineCode):
        super().__init__(parts, lineCode)


class Parser:
    """ 解析文件，每个文件对应一个 parser"""
    def __init__(self, file):
        self.file = file
        self.lines = None
        self.index = 0
    
    def load(self):
        with open(self.file) as f:
            self.lines = f.readlines()
            self.lines = [l.strip() for l in self.lines]
    
    def __len__(self):
        return len(self.lines)
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index >= len(self.lines):
             raise StopIteration()
        
        line = self.lines[self.index]
        instr = Instruction.create(line, self.index, PurePath(self.file).name)
        self.index += 1
        return instr
    
class CodeWriter:
    def __init__(self):
        pass
    

def main(args):
    if args.input:
        parser = Parser(args.input)
        parser.load()
        for inst in parser:
            print(inst.translate())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='VM translator')
    parser.add_argument('--debug', action='store_true', help='output debug info')
    parser.add_argument('-i', '--input', help="input file")
    parser.add_argument('-d', '--dir', help="input dir") # 遍历目录下所有的 .vm 文件
    parser.add_argument('-o', '--output', help="output file") # 输出文件名
    args = parser.parse_args()

    main(args)
