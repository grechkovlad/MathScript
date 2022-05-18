import sys

from parsing.Parser import parse_script
from parsing.Tokenizer import Tokenizer
from backend.wasm.WASMCompiler import compile_script as compile_to_wasm, emit_module_code
from compilation.IRCompiler import compile_script as compile_to_ir


def main():
    source_path = sys.argv[1]
    target_path = sys.argv[2]

    with open(source_path) as source_file:
        source_text = source_file.read()
        tokenizer = Tokenizer(source_text)
        tokenizer.advance()
        compiled = emit_module_code(compile_to_wasm(compile_to_ir(parse_script(tokenizer))))
        with open(target_path, "w") as target_file:
            target_file.write(compiled)


if __name__ == "__main__":
    main()
