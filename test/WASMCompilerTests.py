import io
import unittest

from compilation.WASMCompiler import compile_script as compile_to_wasm, emit_module_code
from compilation.IRCompiler import compile_script as compile_to_ir
from parsing.Tokenizer import Tokenizer
from parsing.Parser import parse_script
from wasmtime import wat2wasm
import pywasm


class TestBases:
    class SuccessfulCompilationTestBase(unittest.TestCase):
        def _get_input(self):
            raise NotImplementedError()

        def _get_expected(self):
            raise NotImplementedError()

        def test_compilation(self):
            text = self._get_input()
            tokenizer = Tokenizer(text)
            tokenizer.advance()
            wasm_bytecode = wat2wasm(emit_module_code(compile_to_wasm(compile_to_ir(parse_script(tokenizer)))))
            module = pywasm.binary.Module.from_reader(io.BytesIO(wasm_bytecode))
            runtime = pywasm.Runtime(module)
            res = runtime.exec('main', [])
            self.assertEqual(self._get_expected(), res)


class FactSevenTest(TestBases.SuccessfulCompilationTestBase):
    def _get_input(self):
        with open('resources/fact7.mas') as file:
            return file.read()

    def _get_expected(self):
        return 5040
