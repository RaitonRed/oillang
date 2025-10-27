import re
from src.lexer.tokens import Token, TOKEN_SPEC
from src.exceptions import OilSyntaxError
from typing import List

class Lexer:
    def __init__(self):
        self.master_re = re.compile('|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPEC))
        
    def lex(self, code: str) -> List[Token]:
        lines = code.split('\n')
        tokens = []
        for m in self.master_re.finditer(code):
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