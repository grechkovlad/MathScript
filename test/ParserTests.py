import unittest

from parsing.Parser import *


class TestBases:
    class SuccessfulParsingTestBase(unittest.TestCase):
        def _get_input(self):
            raise NotImplementedError()

        def _get_rule(self):
            raise NotImplementedError()

        def _get_expected(self):
            raise NotImplementedError()

        def test_parsing(self):
            tokenizer = Tokenizer(self._get_input())
            tokenizer.advance()
            self.assertEqual(self._get_expected(), self._get_rule()(tokenizer))


class SimplestExpressionTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "2*(1+3)"

    def _get_expected(self):
        return BinaryOperation(BinaryOperatorKind.MUL, 2, BinaryOperation(BinaryOperatorKind.PLUS, 1, 3))

    def _get_rule(self):
        return parse_expr


class SimpleExpressionTestOne(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "(x + 3) < 3 & 3 * x | x < y"

    def _get_rule(self):
        return parse_expr

    def _get_expected(self):
        return BinaryOperation(BinaryOperatorKind.OR,
                               BinaryOperation(BinaryOperatorKind.AND,
                                               BinaryOperation(BinaryOperatorKind.LESS,
                                                               BinaryOperation(BinaryOperatorKind.PLUS, "x", 3),
                                                               3),
                                               BinaryOperation(BinaryOperatorKind.MUL, 3, "x")),
                               BinaryOperation(BinaryOperatorKind.LESS, "x", "y"))


class SimpleExpressionTestTwo(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "!(x<y)&(-(a+3)>3*(x-y))"

    def _get_rule(self):
        return parse_expr

    def _get_expected(self):
        return BinaryOperation(BinaryOperatorKind.AND,
                               UnaryOperation(UnaryOperatorKind.NOT,
                                              BinaryOperation(BinaryOperatorKind.LESS, "x", "y")),
                               BinaryOperation(BinaryOperatorKind.GREATER,
                                               UnaryOperation(UnaryOperatorKind.MINUS,
                                                              BinaryOperation(BinaryOperatorKind.PLUS, "a", 3)),
                                               BinaryOperation(BinaryOperatorKind.MUL,
                                                               3,
                                                               BinaryOperation(BinaryOperatorKind.MINUS, "x", "y"))))


class SimpleExpressionTestThree(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "x>=3&3*y<=0|z==x+y"

    def _get_rule(self):
        return parse_expr

    def _get_expected(self):
        return BinaryOperation(BinaryOperatorKind.OR,
                               BinaryOperation(BinaryOperatorKind.AND,
                                               BinaryOperation(BinaryOperatorKind.GEQ, "x", 3),
                                               BinaryOperation(BinaryOperatorKind.LEQ,
                                                               BinaryOperation(BinaryOperatorKind.MUL, 3, "y"),
                                                               0)),
                               BinaryOperation(BinaryOperatorKind.EQ,
                                               "z",
                                               BinaryOperation(BinaryOperatorKind.PLUS, "x", "y")))


class SimplestCallExpressionTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "f(x, y)"

    def _get_rule(self):
        return parse_expr

    def _get_expected(self):
        return Call("f", ["x", "y"])


class ComplexExpressionParsingTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "f(g(x,y),z)<=t()+1|-t(-r())<=0"

    def _get_rule(self):
        return parse_expr

    def _get_expected(self):
        return BinaryOperation(BinaryOperatorKind.OR,
                               BinaryOperation(BinaryOperatorKind.LEQ,
                                               Call("f", [Call("g", ["x", "y"])]),
                                               BinaryOperation(BinaryOperatorKind.PLUS,
                                                               Call("t", []),
                                                               1)),
                               BinaryOperation(BinaryOperatorKind.LEQ,
                                               UnaryOperation(UnaryOperatorKind.MINUS,
                                                              Call("t", [UnaryOperation(UnaryOperatorKind.MINUS,
                                                                                        Call("r", []))])),
                                               0))


class SimplestAssignParsingTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "x = f(y);"

    def _get_expected(self):
        return AssignStatement("x", Call("f", ["y"]))

    def _get_rule(self):
        return parse_assign


class TrivialParseParametersTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "()"

    def _get_rule(self):
        return parse_parameters

    def _get_expected(self):
        return []


class SimpleParseParametersTestOne(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "(x)"

    def _get_rule(self):
        return parse_parameters

    def _get_expected(self):
        return ["x"]


class SimpleParseParametersTestTwo(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "(x, z, ab)"

    def _get_rule(self):
        return parse_parameters

    def _get_expected(self):
        return ["x", "z", "ab"]


class SimpleParseCallStatementTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "proc(f(g(x - 1)), y + 1, 2);"

    def _get_rule(self):
        return parse_call_statement

    def _get_expected(self):
        return CallStatement(Call("proc",
                                  [Call("f",
                                        [Call("g",
                                              [BinaryOperation(BinaryOperatorKind.MINUS,
                                                               "x",
                                                               1)])]),
                                   BinaryOperation(BinaryOperatorKind.PLUS,
                                                   "y",
                                                   1),
                                   2]))


class SimplestParseReturnStatementTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "return;"

    def _get_rule(self):
        return parse_return

    def _get_expected(self):
        return ReturnStatement()


class SimpleParseReturnStatementTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "return -x;"

    def _get_rule(self):
        return parse_return

    def _get_expected(self):
        return ReturnStatement(UnaryOperation(UnaryOperatorKind.MINUS, "x"))


class SimpleParseIfStatementTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "if (x < 0) {return -x;}"

    def _get_rule(self):
        return parse_if

    def _get_expected(self):
        return IfStatement(BinaryOperation(BinaryOperatorKind.LESS, "x", 0),
                           [ReturnStatement(UnaryOperation(UnaryOperatorKind.MINUS, "x"))])


class SimpleParseIfElseStatementTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "if (z >= 0) {res = 1;} else {throw(z);}"

    def _get_rule(self):
        return parse_if

    def _get_expected(self):
        return IfStatement(BinaryOperation(BinaryOperatorKind.GEQ, "z", 0),
                           [AssignStatement("res", 1)],
                           [CallStatement(Call("throw", ["z"]))])


class SimpleParseBlockTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "{x = 2; y = x; if (c < 0) {return y;}}"

    def _get_rule(self):
        return parse_block

    def _get_expected(self):
        return [AssignStatement("x", 2),
                AssignStatement("y", "x"),
                IfStatement(BinaryOperation(BinaryOperatorKind.LESS, "c", 0),
                            [ReturnStatement("y")])]


class SimpleParseFunctionTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "function foo() {return 42;}"

    def _get_rule(self):
        return parse_function

    def _get_expected(self):
        return FunctionDecl("foo",
                            [],
                            [ReturnStatement(42)])


class SimpleParseProcedureTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "procedure doSomething(x, y) {z = x + y;}"

    def _get_rule(self):
        return parse_procedure

    def _get_expected(self):
        return ProcedureDecl("doSomething",
                             ["x", "y"],
                             [AssignStatement("z", BinaryOperation(BinaryOperatorKind.PLUS, "x", "y"))])


class FullScriptParsingTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        with open('resources/fact7.ms') as file:
            return file.read()

    def _get_rule(self):
        return parse_script

    def _get_expected(self):
        return Script([AssignStatement("n", 0),
                       FunctionDecl("getThree", [], [ReturnStatement(3)]),
                       ProcedureDecl("initNSix", [], [AssignStatement("n", BinaryOperation(BinaryOperatorKind.MINUS,
                                                                                           BinaryOperation(
                                                                                               BinaryOperatorKind.MUL,
                                                                                               Call("getThree", []),
                                                                                               2),
                                                                                           1))]),
                       FunctionDecl("fact", ["n"], [IfStatement(BinaryOperation(BinaryOperatorKind.GEQ,
                                                                                "n",
                                                                                0),
                                                                [IfStatement(BinaryOperation(BinaryOperatorKind.EQ,
                                                                                             "n",
                                                                                             0),
                                                                             [ReturnStatement(1)]),
                                                                 ReturnStatement(BinaryOperation(BinaryOperatorKind.MUL,
                                                                                                 "n",
                                                                                                 Call("fact", [
                                                                                                     BinaryOperation(
                                                                                                         BinaryOperatorKind.MINUS,
                                                                                                         "n",
                                                                                                         1)])))],
                                                                [ReturnStatement(
                                                                    UnaryOperation(UnaryOperatorKind.MINUS, 1))])]),
                       CallStatement(Call("initNSix", [])),
                       ReturnStatement(Call("fact", ["n"]))])
