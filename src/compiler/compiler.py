from src.parser.ast_nodes import *
from typing import Any, Tuple, List

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