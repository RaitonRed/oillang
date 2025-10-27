from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.compiler.compiler import Compiler
from src.exceptions import OilSyntaxError
from src.vm.vm import VM
from typing import List, Tuple, Any

def compile_source(source: str) -> List[Tuple[str, Any]]:
    try:
        lexer = Lexer()
        tokens = lexer.lex(source)
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