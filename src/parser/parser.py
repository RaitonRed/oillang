from src.parser.ast_nodes import *
from src.lexer.tokens import Token
from src.exceptions import OilSyntaxError

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