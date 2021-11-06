import unittest

from compilation.IRCompiler import *
from parsing.Parser import *


class TestBases:
    class SuccessfulCompilationTestBase(unittest.TestCase):
        def _get_input(self):
            raise NotImplementedError()

        def _get_compilation_rule(self):
            raise NotImplementedError()

        def _get_parsing_rule(self):
            raise NotImplementedError()

        def _get_expected(self):
            raise NotImplementedError()

        def _pass_subroutine_context(self):
            return True

        def test_compilation(self):
            tokenizer = Tokenizer(self._get_input()[0])
            tokenizer.advance()
            input_ast_node = self._get_parsing_rule()(tokenizer)
            input_script_context = self._get_input()[1]
            input_subroutine_context = self._get_input()[2]
            expected_node = self._get_expected()[0]
            expected_script_context = self._get_expected()[1]
            expected_subroutine_context = self._get_expected()[2]
            if self._get_compilation_rule() == compile_script:
                actual_node = self._get_compilation_rule()(input_ast_node)
            else:
                if self._pass_subroutine_context():
                    actual_node = self._get_compilation_rule()(input_ast_node, input_script_context,
                                                               input_subroutine_context)
                else:
                    actual_node = self._get_compilation_rule()(input_ast_node, input_script_context)
            self.assertEqual(expected_node, actual_node)
            self.assertEqual(expected_script_context, input_script_context)
            self.assertEqual(expected_subroutine_context, input_subroutine_context)


class SimplestGlobalVariableDeclarationTest(TestBases.SuccessfulCompilationTestBase):
    def _get_input(self):
        return "var x = 1;", ScriptContext(), None

    def _get_parsing_rule(self):
        return parse_variable_declaration

    def _get_compilation_rule(self):
        return compile_variable_decl

    def _get_expected(self):
        var = GlobalVariableDeclarationIR(index=0, init_value=IntegerIR(1))
        script_context = ScriptContext()
        script_context.variables["x"] = var
        return var, script_context, None


class SimplestLocalVariableDeclarationTest(TestBases.SuccessfulCompilationTestBase):
    def _get_input(self):
        return "var y = 2;", ScriptContext(), SubroutineContext(SubroutineKind.FUNCTION)

    def _get_parsing_rule(self):
        return parse_variable_declaration

    def _get_compilation_rule(self):
        return compile_variable_decl

    def _get_expected(self):
        var = LocalVariableDeclarationIR(index=0, init_value=IntegerIR(2))
        script_context = ScriptContext()
        subroutine_context = SubroutineContext(SubroutineKind.FUNCTION)
        subroutine_context.variables["y"] = var
        return var, script_context, subroutine_context


class GlobalVariableReferenceTest(TestBases.SuccessfulCompilationTestBase):
    def _get_input(self):
        global_var = GlobalVariableDeclarationIR(0, IntegerIR(42))
        script_context = ScriptContext()
        script_context.variables["z"] = global_var
        return "z", script_context, SubroutineContext(SubroutineKind.PROCEDURE)

    def _get_parsing_rule(self):
        return parse_identifier

    def _get_compilation_rule(self):
        return compile_variable_reference

    def _get_expected(self):
        var = GlobalVariableDeclarationIR(0, IntegerIR(42))
        script_context = ScriptContext()
        script_context.variables["z"] = var
        return VariableReferenceIR(var), script_context, SubroutineContext(SubroutineKind.PROCEDURE)


class ParameterReferenceTest(TestBases.SuccessfulCompilationTestBase):
    def _get_input(self):
        subroutine_context = SubroutineContext(SubroutineKind.FUNCTION)
        subroutine_context.variables["param"] = ParameterDeclarationIR(0)
        return "param", ScriptContext(), subroutine_context

    def _get_parsing_rule(self):
        return parse_identifier

    def _get_compilation_rule(self):
        return compile_variable_reference

    def _get_expected(self):
        var = ParameterDeclarationIR(0)
        subroutine_context = SubroutineContext(SubroutineKind.FUNCTION)
        subroutine_context.variables["param"] = var
        return VariableReferenceIR(var), ScriptContext(), subroutine_context


class ParametersTest(TestBases.SuccessfulCompilationTestBase):
    def _get_input(self):
        return "(x, y)", ScriptContext(), SubroutineContext(SubroutineKind.FUNCTION)

    def _get_parsing_rule(self):
        return parse_parameters

    def _get_compilation_rule(self):
        return compile_parameters

    def _get_expected(self):
        x_param = ParameterDeclarationIR(0)
        y_param = ParameterDeclarationIR(1)
        subroutine_context = SubroutineContext(SubroutineKind.FUNCTION)
        subroutine_context.variables["x"] = x_param
        subroutine_context.variables["y"] = y_param
        return [x_param, y_param], ScriptContext(), subroutine_context


class ReturnVoidTest(TestBases.SuccessfulCompilationTestBase):
    def _get_input(self):
        return "return;", ScriptContext(), SubroutineContext(SubroutineKind.PROCEDURE)

    def _get_parsing_rule(self):
        return parse_return

    def _get_compilation_rule(self):
        return compile_return

    def _get_expected(self):
        return ReturnStatementIR(return_value=None), ScriptContext(), SubroutineContext(SubroutineKind.PROCEDURE)


class ScriptReturnTest(TestBases.SuccessfulCompilationTestBase):
    def _get_input(self):
        return "return 42;", ScriptContext(), None

    def _get_parsing_rule(self):
        return parse_return

    def _get_compilation_rule(self):
        return compile_return

    def _get_expected(self):
        return ReturnStatementIR(IntegerIR(42)), ScriptContext(), None


class FunctionReturnTest(TestBases.SuccessfulCompilationTestBase):
    def _get_input(self):
        return "return 42;", ScriptContext(), SubroutineContext(SubroutineKind.FUNCTION)

    def _get_parsing_rule(self):
        return parse_return

    def _get_compilation_rule(self):
        return compile_return

    def _get_expected(self):
        return ReturnStatementIR(IntegerIR(42)), ScriptContext(), SubroutineContext(SubroutineKind.FUNCTION)


class SimpleFunctionTest(TestBases.SuccessfulCompilationTestBase):
    def _get_input(self):
        return "function sum(x, y) {return x + y;}", ScriptContext(), None

    def _get_parsing_rule(self):
        return parse_subroutine

    def _get_compilation_rule(self):
        return compile_subroutine_declaration

    def _pass_subroutine_context(self):
        return False

    def _get_expected(self):
        x_param = ParameterDeclarationIR(0)
        y_param = ParameterDeclarationIR(1)
        subroutine_decl = SubroutineDeclarationIR(SubroutineKind.FUNCTION,
                                                  [x_param, y_param],
                                                  [ReturnStatementIR(BinaryOperationIR(VariableReferenceIR(x_param),
                                                                                       VariableReferenceIR(y_param),
                                                                                       BinaryOperatorKind.PLUS))])
        script_context = ScriptContext()
        script_context.subroutines["sum"] = subroutine_decl
        return subroutine_decl, script_context, None


class SimpleIfStatementTest(TestBases.SuccessfulCompilationTestBase):
    def _get_input(self):
        return "if (1 > 0) {return 1;} else {return 2;}", ScriptContext(), None

    def _get_parsing_rule(self):
        return parse_if

    def _get_compilation_rule(self):
        return compile_if

    def _get_expected(self):
        if_statement = IfStatementIR(BinaryOperationIR(IntegerIR(1), IntegerIR(0), BinaryOperatorKind.GREATER),
                                     [ReturnStatementIR(IntegerIR(1))],
                                     [ReturnStatementIR(IntegerIR(2))])
        return if_statement, ScriptContext(), None


class SimpleFunctionCallTest(TestBases.SuccessfulCompilationTestBase):
    def _get_input(self):
        x_var = GlobalVariableDeclarationIR(0, IntegerIR(42))
        script_context = ScriptContext()
        script_context.variables["x"] = x_var
        script_context.subroutines["f"] = SubroutineDeclarationIR(SubroutineKind.FUNCTION,
                                                                  [ParameterDeclarationIR(0),
                                                                   ParameterDeclarationIR(1)],
                                                                  [ReturnStatementIR(IntegerIR(42))])
        return "f(1, x)", script_context, None

    def _get_parsing_rule(self):
        return parse_call

    def _get_compilation_rule(self):
        return compile_call

    def _get_expected(self):
        x_var = GlobalVariableDeclarationIR(0, IntegerIR(42))
        script_context = ScriptContext()
        script_context.variables["x"] = x_var
        f_decl = SubroutineDeclarationIR(SubroutineKind.FUNCTION,
                                         [ParameterDeclarationIR(0), ParameterDeclarationIR(1)],
                                         [ReturnStatementIR(IntegerIR(42))])
        script_context.subroutines["f"] = f_decl
        return (CallIR(SubroutineReferenceIR(f_decl), [IntegerIR(1), VariableReferenceIR(x_var)]),
                Type.INT), script_context, None


class SimpleProcedureCallStatementTest(TestBases.SuccessfulCompilationTestBase):
    def _get_input(self):
        script_context = ScriptContext()
        script_context.subroutines["proc"] = SubroutineDeclarationIR(SubroutineKind.PROCEDURE,
                                                                     [ParameterDeclarationIR(0)],
                                                                     [])
        return "proc(1);", script_context, None

    def _get_parsing_rule(self):
        return parse_call_statement

    def _get_compilation_rule(self):
        return compile_call_statement

    def _get_expected(self):
        script_context = ScriptContext()
        procedure_decl = SubroutineDeclarationIR(SubroutineKind.PROCEDURE,
                                                 [ParameterDeclarationIR(0)],
                                                 [])
        script_context.subroutines["proc"] = procedure_decl
        call_statement = CallStatementIR(CallIR(SubroutineReferenceIR(procedure_decl), [IntegerIR(1)]))
        return call_statement, script_context, None


class AssignTest(TestBases.SuccessfulCompilationTestBase):
    def _get_input(self):
        x_decl = GlobalVariableDeclarationIR(0, IntegerIR(42))
        script_context = ScriptContext()
        script_context.variables["x"] = x_decl
        return "x = 3;", script_context, None

    def _get_parsing_rule(self):
        return parse_assign

    def _get_compilation_rule(self):
        return compile_assign

    def _get_expected(self):
        x_decl = GlobalVariableDeclarationIR(0, IntegerIR(42))
        script_context = ScriptContext()
        script_context.variables["x"] = x_decl

        return AssignStatementIR(VariableReferenceIR(x_decl), IntegerIR(3)), script_context, None


class FullScriptTest(TestBases.SuccessfulCompilationTestBase):
    def _get_input(self):
        with open('resources/fact7.mas') as file:
            return file.read(), None, None

    def _get_parsing_rule(self):
        return parse_script

    def _get_compilation_rule(self):
        return compile_script

    def _get_expected(self):
        input_var_decl = GlobalVariableDeclarationIR(0, IntegerIR(0))

        get_three_local_var_decl = LocalVariableDeclarationIR(0, IntegerIR(3))
        get_three_decl = SubroutineDeclarationIR(SubroutineKind.FUNCTION,
                                                 [],
                                                 [get_three_local_var_decl,
                                                  ReturnStatementIR(VariableReferenceIR(get_three_local_var_decl))])
        get_three_ref = SubroutineReferenceIR(get_three_decl)
        init_n_six_local_var_decl = LocalVariableDeclarationIR(0,
                                                               BinaryOperationIR(BinaryOperationIR(CallIR(get_three_ref,
                                                                                                          []),
                                                                                                   IntegerIR(2),
                                                                                                   BinaryOperatorKind.MUL),
                                                                                 IntegerIR(1),
                                                                                 BinaryOperatorKind.MINUS))
        init_n_six_decl = SubroutineDeclarationIR(SubroutineKind.PROCEDURE,
                                                  [],
                                                  [init_n_six_local_var_decl,
                                                   AssignStatementIR(VariableReferenceIR(input_var_decl),
                                                                     VariableReferenceIR(init_n_six_local_var_decl))])

        n_param = ParameterDeclarationIR(0)
        fact_decl = SubroutineDeclarationIR(SubroutineKind.FUNCTION,
                                            [n_param],
                                            [])
        fact_body = [IfStatementIR(BinaryOperationIR(VariableReferenceIR(n_param),
                                                     IntegerIR(0),
                                                     BinaryOperatorKind.GEQ),
                                   [IfStatementIR(BinaryOperationIR(VariableReferenceIR(n_param),
                                                                    IntegerIR(0),
                                                                    BinaryOperatorKind.EQ),
                                                  [ReturnStatementIR(IntegerIR(1))],
                                                  None),
                                    ReturnStatementIR(BinaryOperationIR(VariableReferenceIR(n_param),
                                                                        CallIR(SubroutineReferenceIR(fact_decl),
                                                                               [BinaryOperationIR(
                                                                                   VariableReferenceIR(n_param),
                                                                                   IntegerIR(1),
                                                                                   BinaryOperatorKind.MINUS)]),
                                                                        BinaryOperatorKind.MUL))],
                                   [ReturnStatementIR(UnaryOperationIR(IntegerIR(1), UnaryOperatorKind.MINUS))])]
        fact_decl.body = fact_body

        init_n_six_call = CallStatementIR(CallIR(SubroutineReferenceIR(init_n_six_decl), []))

        script_return = ReturnStatementIR(
            CallIR(SubroutineReferenceIR(fact_decl), [VariableReferenceIR(input_var_decl)]))

        script = ScriptIR([get_three_decl, init_n_six_decl, fact_decl],
                          [input_var_decl, init_n_six_call, script_return])

        return script, None, None
