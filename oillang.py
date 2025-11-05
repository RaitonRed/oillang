import re
import sys
from dataclasses import dataclass
from typing import List, Any, Tuple, Dict, Optional

# SyntaxError
class OilSyntaxError(Exception):
    def __init__(self, message, line_num=None, source_line=None):
        self.message = message
        self.line_num = line_num
        self.source_line = source_line
        super().__init__(self.format_error())
    
    def format_error(self):
        if self.line_num is not None and self.source_line is not None:
            return f"SyntaxError at line {self.line_num}:\n  {self.source_line}\n  {self.message}"
        else:
            return f"SyntaxError: {self.message}"

# -------------------- Lexer --------------------
TOKEN_SPEC = [
    ('WHILE',    r'\bwhile\b'),
    ('IF',       r'\bif\b'),
    ('ELSE',     r'\belse\b'),
    ('PRINT',    r'\bprint\b'),
    ('NUMBER',   r'\d+'),
    ('ID',       r'[A-Za-z_][A-Za-z0-9_]*'),
    ('COMPOUND_OP', r'\+=|-=|\*=|/=|%=|&=|\|=|\^='),
    ('OP',       r'==|!=|<=|>=|=\<|[+\-*/<>=]'),
    ('LOGICAL_OP', r'&&|\|\|'),
    ('NOT',      r'!'),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('LBRACE',   r'\{'),
    ('RBRACE',   r'\}'),
    ('SEMI',     r';'),
    ('SKIP',     r'[ \t\r\n]+'),
    ('MISMATCH', r'.'),
]

MASTER_RE = re.compile('|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPEC))

@dataclass
class Token:
    type: str
    value: Any

def lex(code: str) -> List[Token]:
    lines = code.split('\n')
    tokens = []
    for m in MASTER_RE.finditer(code):
        typ = m.lastgroup
        val = m.group()
        start_pos = m.start()

        # Calculate line number and source line
        line_num = 1
        current_pos = 0
        source_line = ""
        for i, line in enumerate(lines, 1):
            line_length = len(line) + 1  # +1 for newline
            if current_pos <= start_pos < current_pos + line_length:
                line_num = i
                source_line = line
                break
            current_pos += line_length
        
        if typ == 'NUMBER':
            tokens.append(Token('NUMBER', int(val)))
        elif typ in ('ID', 'WHILE', 'IF', 'ELSE', 'PRINT'):
            tokens.append(Token(typ, val))
        elif typ == "COMPOUND_OP":
            tokens.append(Token('COMPOUND_OP', val))
        elif typ == 'OP':
            tokens.append(Token('OP', val))
        elif typ == 'LOGICAL_OP':
            tokens.append(Token('LOGICAL_OP', val))
        elif typ == 'NOT':
            tokens.append(Token('NOT', val))
        elif typ in ('LPAREN','RPAREN','LBRACE','RBRACE','SEMI'):
            tokens.append(Token(typ, val))
        elif typ == 'SKIP':
            continue
        elif typ == 'MISMATCH':
            raise OilSyntaxError(f'Unexpected character: {val!r}', line_num, source_line)
    return tokens

# -------------------- Parser --------------------
@dataclass
class ASTNode: pass

@dataclass
class While(ASTNode):
    cond: ASTNode
    body: List[ASTNode]

@dataclass
class Number(ASTNode): 
    value: int

@dataclass
class Var(ASTNode): 
    name: str

@dataclass
class BinOp(ASTNode): 
    op: str
    left: ASTNode
    right: ASTNode

@dataclass
class UnOp(ASTNode):
    op: str
    expr: ASTNode

@dataclass
class Assign(ASTNode): 
    name: str
    expr: ASTNode

@dataclass
class Print(ASTNode): 
    expr: ASTNode

@dataclass
class If(ASTNode): 
    cond: ASTNode
    then_block: List[ASTNode]
    else_block: Optional[List[ASTNode]]=None
    
@dataclass
class CompoundAssign(ASTNode):
    name: str
    op: str
    expr: ASTNode

class Parser:
    def __init__(self, tokens: List[Token], source_code: str): 
        self.tokens = tokens
        self.pos = 0
        self.token_lines = {}
        self.source_lines = source_code.split('\n')
        for i, token in enumerate(tokens):
            self.token_lines[i] = i
    
    def get_current_line(self):
        if self.pos < len(self.tokens):
            pass
        return None
    
    def get_line_num(self):
        return self.token_lines.get(self.pos, 0)
    
    def peek(self): 
        return self.tokens[self.pos] if self.pos<len(self.tokens) else None
    
    def consume(self, expected_type=None, expected_val=None):
        tok = self.peek()
        if tok is None: 
            line_num = self.get_line_num()
            source_line = self.source_lines[line_num-1] if line_num <= len(self.source_lines) else ""
            raise OilSyntaxError('Unexpected end of input', line_num, source_line)
        if expected_type and tok.type != expected_type: 
            line_num = self.get_line_num()
            source_line = self.source_lines[line_num-1] if line_num <= len(self.source_lines) else ""
            raise OilSyntaxError(f'Expected {expected_type}, got {tok.type}', line_num, source_line)
        if expected_val and tok.value != expected_val: 
            line_num = self.get_line_num()
            source_line = self.source_lines[line_num-1] if line_num <= len(self.source_lines) else ""
            raise OilSyntaxError(f'Expected {expected_val}, got {tok.value}', line_num, source_line)
        self.pos += 1
        return tok

    def parse(self) -> List[ASTNode]:
        stmts = []
        while self.peek() is not None:
            stmts.append(self.parse_stmt())
        return stmts

    def parse_stmt(self) -> ASTNode:
        tok = self.peek()
        if tok is None:
            raise SyntaxError('Unexpected EOF')

        if tok.type == 'WHILE':
            return self.parse_while()
        elif tok.type == 'PRINT':
            self.consume('PRINT')
            expr = self.parse_expr()
            self.consume('SEMI')
            return Print(expr)
        elif tok.type == 'IF':
            return self.parse_if()
        elif tok.type == 'ID':
            next_tok = self.tokens[self.pos+1] if self.pos+1 < len(self.tokens) else None
            if next_tok and next_tok.type == 'OP' and next_tok.value == '=':
                name = self.consume('ID').value
                self.consume('OP', '=')
                expr = self.parse_expr()
                self.consume('SEMI')
                return Assign(name, expr)
            elif next_tok and next_tok.type == 'COMPOUND_OP':
                name = self.consume('ID').value
                compound_op = self.consume('COMPOUND_OP').value
                expr = self.parse_expr()
                self.consume('SEMI')
                return CompoundAssign(name, compound_op, expr)
            else:
                line_num = self.get_line_num()
                source_line = self.source_lines[line_num-1] if line_num <= len(self.source_lines) else ""
                raise OilSyntaxError(f'Unexpected identifier {tok.value}, expected assignment', line_num, source_line)
        else:
            line_num = self.get_line_num()
            source_line = self.source_lines[line_num-1] if line_num <= len(self.source_lines) else ""
            raise OilSyntaxError(f'Unexpected token {tok}', line_num, source_line)

    def parse_if(self) -> If:
        self.consume('IF')
        self.consume('LPAREN')
        cond = self.parse_expr()
        self.consume('RPAREN')
        self.consume('LBRACE')
        then_block = []
        while self.peek() and self.peek().type != 'RBRACE':
            then_block.append(self.parse_stmt())
        self.consume('RBRACE')
        else_block = None
        if self.peek() and self.peek().type == 'ELSE':
            self.consume('ELSE')
            self.consume('LBRACE')
            else_block = []
            while self.peek() and self.peek().type != 'RBRACE':
                else_block.append(self.parse_stmt())
            self.consume('RBRACE')
        return If(cond, then_block, else_block)

    # Expression parsing with precedence
    def parse_expr(self) -> ASTNode: 
        return self.parse_comparison()
    
    def parse_while(self) -> While:
        self.consume('WHILE')
        self.consume('LPAREN')
        cond = self.parse_expr()
        self.consume('RPAREN')
        self.consume('LBRACE')
        body = []
        while self.peek() and self.peek().type != 'RBRACE':
            body.append(self.parse_stmt())
        self.consume('RBRACE')
        return While(cond, body)
    
    def parse_expr(self) -> ASTNode:
        return self.parse_logic()
        
    def parse_logic(self) -> ASTNode:
        node = self.parse_comparison()
        while True:
            tok = self.peek()
            if tok and tok.type == 'LOGICAL_OP' and tok.value in ('&&', '||'):
                op = self.consume('LOGICAL_OP').value
                right = self.parse_comparison()
                node = BinOp(op, node, right)
            else: 
                break
        return node
    
    def parse_comparison(self) -> ASTNode:
        node = self.parse_sum()
        while True:
            tok = self.peek()
            if tok and tok.type == 'OP' and tok.value in ('==','!=','<','<=','>','>='):
                op = self.consume('OP').value
                right = self.parse_sum()
                node = BinOp(op, node, right)
            else: 
                break
        return node
        
    def parse_sum(self) -> ASTNode:
        node = self.parse_term()
        while True:
            tok = self.peek()
            if tok and tok.type == 'OP' and tok.value in ('+','-'):
                op = self.consume('OP').value
                right = self.parse_term()
                node = BinOp(op, node, right)
            else: 
                break
        return node
        
    def parse_term(self) -> ASTNode:
        node = self.parse_factor()
        while True:
            tok = self.peek()
            if tok and tok.type == 'OP' and tok.value in ('*','/'):
                op = self.consume('OP').value
                right = self.parse_factor()
                node = BinOp(op, node, right)
            else: 
                break
        return node
        
    def parse_factor(self) -> ASTNode:
        tok = self.peek()
        if tok is None: 
            raise SyntaxError('Unexpected EOF in factor')
        if tok.type == 'NOT':
            self.consume('NOT')
            expr = self.parse_factor()
            return UnOp('!', expr)
        if tok.type == 'NUMBER': 
            val = self.consume('NUMBER').value
            return Number(val)
        elif tok.type == 'ID': 
            name = self.consume('ID').value
            return Var(name)
        elif tok.type == 'LPAREN': 
            self.consume('LPAREN')
            node = self.parse_expr()
            self.consume('RPAREN')
            return node
        else: 
            raise SyntaxError(f'Line {self.get_line_num()}: Unexpected token in factor: {tok}')

# -------------------- Compiler --------------------
class Compiler:
    def __init__(self): 
        self.code: List[Tuple[str, Any]] = []
        self.line_info = {}
        
    def emit(self, instr: Tuple[str, Any], line_num: int = 0): 
        self.code.append(instr)
        self.line_info[len(self.code)-1] = line_num
        
    def patch(self, pos: int, target: int): 
        op,_ = self.code[pos]
        self.code[pos] = (op, target)
        
    def compile_program(self, nodes: List[ASTNode]):
        for n in nodes: 
            self.compile_node(n)
        self.emit(('HALT', None))
        return self.code, self.line_info
        
    def compile_node(self, node: ASTNode):
        if isinstance(node, Number): 
            self.emit(('CONST', node.value))
        elif isinstance(node, Var): 
            self.emit(('LOAD', node.name))
        elif isinstance(node, BinOp):
            self.compile_node(node.left)
            self.compile_node(node.right)
            op = node.op
            op_map = {
                '+' : 'ADD', '-' : 'SUB', '*' : 'MUL', '/' : 'DIV',
                '==' : 'EQ', '!=' : 'NE', '<' : 'LT', '<=' : 'LE', '>' : 'GT', '>=' : 'GE',
                '&&' : 'AND', '||' : 'OR'
            }
            self.emit((op_map[op], None))
        elif isinstance(node, UnOp):
            self.compile_node(node.expr)
            if node.op == '!':
                self.emit(('NOT', None))
        elif isinstance(node, Assign): 
            self.compile_node(node.expr)
            self.emit(('STORE', node.name))
        elif isinstance(node, CompoundAssign):
            self.emit(('LOAD', node.name))
            self.compile_node(node.expr)
            op_map = {
                '+=' : 'ADD',
                '-=' : 'SUB', 
                '*=' : 'MUL',
                '/=' : 'DIV'
            }
            self.emit((op_map[node.op], None))
            self.emit(('STORE', node.name))
        elif isinstance(node, Print): 
            self.compile_node(node.expr)
            self.emit(('PRINT', None))
        elif isinstance(node, While):
            loop_start = len(self.code)
            self.compile_node(node.cond)
            jmp_false_pos = len(self.code)
            self.emit(('JUMP_IF_FALSE', None))
            for stmt in node.body:
                self.compile_node(stmt)
            self.emit(('JUMP', loop_start))
            self.patch(jmp_false_pos, len(self.code))
        elif isinstance(node, If):
            self.compile_node(node.cond)
            jif_pos = len(self.code)
            self.emit(('JUMP_IF_FALSE', None))
            for s in node.then_block: 
                self.compile_node(s)
            if node.else_block is not None:
                jmp_pos = len(self.code)
                self.emit(('JUMP', None))
                else_start = len(self.code)
                self.patch(jif_pos, else_start)
                for s in node.else_block: 
                    self.compile_node(s)
                self.patch(jmp_pos, len(self.code))
            else: 
                self.patch(jif_pos, len(self.code))
        else: 
            raise RuntimeError(f'Unknown AST node: {node}')

# -------------------- VM --------------------
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

# -------------------- REPL --------------------
def repl():
    print("OilLang PreAlpha0.0.1 Type 'exit' to exit.")
    while True:
        try:
            source = input(">> ")
            if source.strip() == "exit":
                break
            if not source.strip():
                continue
            
            # Remove comments
            source_no_comments = re.sub(r'//.*', '', source)
            
            try:
                code, output = run_source(source_no_comments)
            except OilSyntaxError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"Error during execution: {e}")
                
        except EOFError:
            print("\nExiting...")
            break
        except KeyboardInterrupt:
            print("\nExiting...")
            break

# -------------------- Helper --------------------
def compile_source(source: str) -> List[Tuple[str, Any]]:
    try:
        tokens = lex(source)
        parser = Parser(tokens, source)
        
        ast = parser.parse()
        comp = Compiler()
        
        return comp.compile_program(ast)
    except OilSyntaxError:
        raise
    except Exception as e:
        raise OilSyntaxError(str(e)) from e

def run_source(source: str):
    code, line_info = compile_source(source)
    print('=== Bytecode ===')
    for idx, instr in enumerate(code):
        print(f'{idx:03}: {instr}')
    print('=== Running VM ===')
    vm = VM(code)
    vm.run()
    return code, vm.output_lines

def main():
    if len(sys.argv) == 1:
        repl()
    elif len(sys.argv) == 2:
        source_file = sys.argv[1]
        
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except FileNotFoundError:
            print(f"Error: File '{source_file}' not found.")
            sys.exit(1)
        
        # Remove comments
        source_code_no_comments = re.sub(r'//.*', '', source_code)
        
        try:
            code, output = run_source(source_code_no_comments)
        except OilSyntaxError as e:
            print(f"Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error during execution: {e}")
            sys.exit(1)
    else:
        print("Usage: python oillang.py [source_file.oil]")
        print("If no file is provided, starts REPL mode.")
        sys.exit(1)

if __name__ == "__main__":
    main()
