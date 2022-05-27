import unittest
import os

from parsing.Parser import parse_script
from parsing.Tokenizer import Tokenizer
from compilation.IRCompiler import compile_script as compile_to_ir
from backend.jvm.JVMCompiler import Compiler as JvmCompiler
from backend.jvm.bytecodewriter.bytecompiler import ClassFile

PACKAGE = "test"
CLASS_NAME = "Main"
OUT_DIR = "out"

QUALIFIED_CLASS_NAME_JVM = "%s/%s" % (PACKAGE, CLASS_NAME)
CLASS_FILE_PATH = "%s/%s/%s.class" % (OUT_DIR, PACKAGE, CLASS_NAME)
JSHELL_RUN_CMD = "jshell --class-path %s" % OUT_DIR
JSHELL_CALL = "System.out.println(%s.%s.main())" % (PACKAGE, CLASS_NAME)
JSHELL_CODE = "%s;\n" % JSHELL_CALL
JSHELL_OUT = "'jshell> %s" % JSHELL_CALL


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
            ir = compile_to_ir(parse_script(tokenizer))
            jvm_compiler = JvmCompiler(QUALIFIED_CLASS_NAME_JVM)
            clazz = jvm_compiler.compile(ir)
            _dump_class_to_disk(clazz)
            actual = int(_run())
            self.assertEqual(self._get_expected(), actual)


def _dump_class_to_disk(clazz: ClassFile):
    os.makedirs(os.path.dirname(CLASS_FILE_PATH), exist_ok=True)
    with open(CLASS_FILE_PATH, "wb") as f:
        f.write(clazz.serialize())


def _run():
    import subprocess
    process = subprocess.Popen(JSHELL_RUN_CMD, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    out_lines = process.communicate(str.encode(JSHELL_CODE))[0].decode("utf-8").split("\n")
    return out_lines[3][len(JSHELL_OUT) - 1:]


class SimplestTest(TestBases.SuccessfulCompilationTestBase):
    def _get_input(self):
        with open('resources/simplest.mas') as file:
            return file.read()

    def _get_expected(self):
        return 0


class FactSevenTest(TestBases.SuccessfulCompilationTestBase):
    def _get_input(self):
        with open('resources/fact7.mas') as file:
            return file.read()

    def _get_expected(self):
        return 5040


class NumberOfRootsTest(TestBases.SuccessfulCompilationTestBase):
    def _get_input(self):
        with open('resources/number_of_roots.mas') as file:
            return file.read()

    def _get_expected(self):
        return 2


class SumFrom1ToNTest(TestBases.SuccessfulCompilationTestBase):
    def _get_input(self):
        with open('resources/sum_from_1_to_n.mas') as file:
            return file.read()

    def _get_expected(self):
        return 55


class CountIntersectionsTest(TestBases.SuccessfulCompilationTestBase):
    def _get_input(self):
        with open('resources/count_intersections.mas') as file:
            return file.read()

    def _get_expected(self):
        return 3
