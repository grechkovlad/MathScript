from compilation.WASMCompiler import compile_script as compile_to_wasm, emit_module_code
from compilation.IRCompiler import compile_script as compile_to_ir
from parsing.Tokenizer import Tokenizer
from parsing.Parser import parse_script

with open('resources/fact7.mas') as file:
    text = file.read()
    tokenizer = Tokenizer(text)
    tokenizer.advance()
    ast = parse_script(tokenizer)
    ir = compile_to_ir(ast)
    module = compile_to_wasm(ir)
    print(emit_module_code(module))
