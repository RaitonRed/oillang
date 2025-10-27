import sys
from src.repl import repl
from src.utils.helpers import run_source

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