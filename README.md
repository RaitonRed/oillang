# OilLang

A simple interpreted programming language implemented in Python, featuring a lexer, parser, compiler, and virtual machine.

## Overview

OilLang is an educational programming language that demonstrates the core components of language implementation:

- **Lexer**: Converts source code into tokens
- **Parser**: Builds an Abstract Syntax Tree (AST) from tokens
- **Compiler**: Transforms AST into bytecode
- **Virtual Machine**: Executes the compiled bytecode

## Features

- **Variables**: x = 5;
- **Arithmetic Operations**: ``+``, ``-``, ``*``, ``/``
- **Comparison Operations**: ``==``, ``!=``, ``<``, ``<=``, ``>``, ``>=``
- **Logical Operations**: ``&&``, ``||``, ``!``
- **Compound Assignments**: ``+=``, ``-=``, ``*=``, ``/=``
- **Control Structures**: ``if`` and ``while``
- **Output**: ``print`` statements
- **Comments**: Single-line comments with ``//``

## Example Programs

```oil
// Basic arithmetic and variables
x = 10;
y = 5;
result = x * y + 2;
print result;

// Conditional statements
if (x > y) {
    print "x is greater";
} else {
    print "y is greater or equal";
}

// While loop
counter = 0;
while (counter < 5) {
    print counter;
    counter += 1;
}
```

## Installation

```bash
git clone https://github.com/RaitonRed/oillang.git
cd oillang
```

## Usage

### REPL Mode

```bash
python main.py
```

### File Execution

```bash
python main.py program.oil
```

## Roadmap

### Phase 1: Core Language Enhancements

- Add support for string literals
- Implement arrays/lists
- Add functions and return statements
- Support for floating-point numbers
- Add modulo operator (``%``)

### Phase 2: Developer Experience

- Better error messages with line numbers and suggestions
- Syntax highlighting for editors
- Debug mode with step-by-step execution
- Bytecode disassembler
- Profiling and optimization tools

### Phase 3: Advanced Features

- Standard library functions (I/O, math, etc.)
- Import system for modular code
- Basic type system
- Garbage collection
- JIT compilation

### Phase 4: Ecosystem

- Package manager for libraries
- Language server protocol support
- Web-based playground
- Comprehensive documentation
- Performance benchmarking suite

## Contributing

Contributions are welcome! Please feel free to submit pull requests for:

- Bug fixes
- New language features
- Performance improvements
- Additional test cases
- Documentation enhancements

## License

This project is open source and available under the MIT License.