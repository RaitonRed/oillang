from dataclasses import dataclass
from typing import List, Optional

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