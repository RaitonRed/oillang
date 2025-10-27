import re
from src.utils.global_vars import version
from src.utils.helpers import run_source
from src.exceptions import OilSyntaxError

def repl():
    print(f"OilLang {version} Type 'exit' to exit.")
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