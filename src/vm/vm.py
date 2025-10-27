from typing import List, Tuple, Any

class VM:
    def __init__(self, code: List[Tuple[str, Any]]):
        self.code = code 
        self.stack = [] 
        self.env = {} 
        self.ip = 0 
        self.output_lines = []
        
    def run(self):
        while self.ip < len(self.code):
            instr, arg = self.code[self.ip]
            self.ip += 1
            if instr == 'CONST': 
                self.stack.append(arg)
            elif instr == 'LOAD': 
                self.stack.append(self.env.get(arg,0))
            elif instr == 'STORE': 
                self.env[arg] = self.stack.pop()
            elif instr == 'ADD': 
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a+b)
            elif instr == 'SUB': 
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a-b)
            elif instr == 'MUL': 
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a*b)
            elif instr == 'DIV': 
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a//b if isinstance(a,int) and isinstance(b,int) else a/b)
            elif instr == 'EQ': 
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a==b else 0)
            elif instr == 'NE': 
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a!=b else 0)
            elif instr == 'LT': 
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a<b else 0)
            elif instr == 'LE': 
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a<=b else 0)
            elif instr == 'AND':
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a and b else 0)
            elif instr == 'OR':
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a or b else 0)
            elif instr == 'NOT':
                a = self.stack.pop()
                self.stack.append(1 if not a else 0)
            elif instr == 'GT': 
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a>b else 0)
            elif instr == 'GE': 
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a>=b else 0)
            elif instr == 'JUMP_IF_FALSE': 
                cond = self.stack.pop()
                self.ip = arg if not cond else self.ip
            elif instr == 'JUMP': 
                self.ip = arg
            elif instr == 'PRINT': 
                val = self.stack.pop()
                self.output_lines.append(str(val))
                print(val)
            elif instr == 'HALT': 
                break
            else: 
                raise RuntimeError(f'Unknown opcode {instr} at ip {self.ip-1}')