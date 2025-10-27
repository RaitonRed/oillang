from dataclasses import dataclass
from typing import Any

@dataclass
class Token:
    type: str
    value: Any

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