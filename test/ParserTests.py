import unittest

from parsing.Parser import *
from parsing.Tokenizer import Location as TokenLocation


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

    class FailedParsingTestBase(unittest.TestCase):
        def _get_input(self):
            raise NotImplementedError()

        def _get_rule(self):
            raise NotImplementedError()

        def _get_expected_exception(self):
            raise NotImplementedError()

        def test_parsing(self):
            tokenizer = Tokenizer(self._get_input())
            tokenizer.advance()
            with self.assertRaises(ParserException) as cm:
                self._get_rule()(tokenizer)
            self.assertEqual(self._get_expected_exception(), cm.exception)


class SimplestExpressionTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "2*(1+3)"

    def _get_expected(self):
        return BinaryOperation(BinaryOperatorKind.MUL,
                               Integer(2, Location(1, 1, 1, 1)),
                               BinaryOperation(BinaryOperatorKind.PLUS,
                                               Integer(1, Location(1, 4, 1, 4)),
                                               Integer(3, Location(1, 6, 1, 6)),
                                               Location(1, 3, 1, 7)),
                               Location(1, 1, 1, 7))

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
                                                               BinaryOperation(BinaryOperatorKind.PLUS,
                                                                               Identifier("x", Location(1, 2, 1, 2)),
                                                                               Integer(3, Location(1, 6, 1, 6)),
                                                                               Location(1, 1, 1, 7)),
                                                               Integer(3, Location(1, 11, 1, 11)),
                                                               Location(1, 1, 1, 11)),
                                               BinaryOperation(BinaryOperatorKind.MUL,
                                                               Integer(3, Location(1, 15, 1, 15)),
                                                               Identifier("x", Location(1, 19, 1, 19)),
                                                               Location(1, 15, 1, 19)),
                                               Location(1, 1, 1, 19)),
                               BinaryOperation(BinaryOperatorKind.LESS,
                                               Identifier("x", Location(1, 23, 1, 23)),
                                               Identifier("y", Location(1, 27, 1, 27)),
                                               Location(1, 23, 1, 27)),
                               Location(1, 1, 1, 27))


class SimpleExpressionTestTwo(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "!(x<y)&(-(a+3)>3*(x-y))"

    def _get_rule(self):
        return parse_expr

    def _get_expected(self):
        return BinaryOperation(BinaryOperatorKind.AND,
                               UnaryOperation(UnaryOperatorKind.NOT,
                                              BinaryOperation(BinaryOperatorKind.LESS,
                                                              Identifier("x", Location(1, 3, 1, 3)),
                                                              Identifier("y", Location(1, 5, 1, 5)),
                                                              Location(1, 2, 1, 6)),
                                              Location(1, 1, 1, 6)),
                               BinaryOperation(BinaryOperatorKind.GREATER,
                                               UnaryOperation(UnaryOperatorKind.MINUS,
                                                              BinaryOperation(BinaryOperatorKind.PLUS,
                                                                              Identifier("a", Location(1, 11, 1, 11)),
                                                                              Integer(3, Location(1, 13, 1, 13)),
                                                                              Location(1, 10, 1, 14)),

                                                              Location(1, 9, 1, 14)),
                                               BinaryOperation(BinaryOperatorKind.MUL,
                                                               Integer(3, Location(1, 16, 1, 16)),
                                                               BinaryOperation(BinaryOperatorKind.MINUS,
                                                                               Identifier("x", Location(1, 19, 1, 19)),
                                                                               Identifier("y",
                                                                                          Location(1, 21, 1, 21)),
                                                                               Location(1, 18, 1, 22)),
                                                               Location(1, 16, 1, 22)),
                                               Location(1, 8, 1, 23)),
                               Location(1, 1, 1, 23))


class SimpleExpressionTestThree(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "x>=3&3*y<=0|z==x+y"

    def _get_rule(self):
        return parse_expr

    def _get_expected(self):
        return BinaryOperation(BinaryOperatorKind.OR,
                               BinaryOperation(BinaryOperatorKind.AND,
                                               BinaryOperation(BinaryOperatorKind.GEQ,
                                                               Identifier("x", Location(1, 1, 1, 1)),
                                                               Integer(3, Location(1, 4, 1, 4)),
                                                               Location(1, 1, 1, 4)),
                                               BinaryOperation(BinaryOperatorKind.LEQ,
                                                               BinaryOperation(BinaryOperatorKind.MUL,
                                                                               Integer(3, Location(1, 6, 1, 6)),
                                                                               Identifier("y", Location(1, 8, 1, 8)),
                                                                               Location(1, 6, 1, 8)),
                                                               Integer(0, Location(1, 11, 1, 11)),
                                                               Location(1, 6, 1, 11)),
                                               Location(1, 1, 1, 11)),
                               BinaryOperation(BinaryOperatorKind.EQ,
                                               Identifier("z", Location(1, 13, 1, 13)),
                                               BinaryOperation(BinaryOperatorKind.PLUS,
                                                               Identifier("x", Location(1, 16, 1, 16)),
                                                               Identifier("y", Location(1, 18, 1, 18)),
                                                               Location(1, 16, 1, 18)),
                                               Location(1, 13, 1, 18)),
                               Location(1, 1, 1, 18))


class SimplestCallExpressionTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "f(x, y)"

    def _get_rule(self):
        return parse_expr

    def _get_expected(self):
        return Call(Identifier("f", Location(1, 1, 1, 1)),
                    ArgumentsList([Identifier("x", Location(1, 3, 1, 3)),
                                   Identifier("y", Location(1, 6, 1, 6))],
                                  Location(1, 2, 1, 7)),
                    Location(1, 1, 1, 7))


class ComplexExpressionParsingTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "f(g(x,y),z)<=t()+1|-t(-r())<=0"

    def _get_rule(self):
        return parse_expr

    def _get_expected(self):
        return BinaryOperation(BinaryOperatorKind.OR,
                               BinaryOperation(BinaryOperatorKind.LEQ,
                                               Call(Identifier("f", Location(1, 1, 1, 1)),
                                                    ArgumentsList([Call(Identifier("g", Location(1, 3, 1, 3)),
                                                                        ArgumentsList([
                                                                            Identifier("x", Location(1, 5, 1, 5)),
                                                                            Identifier("y", Location(1, 7, 1, 7))
                                                                        ], Location(1, 4, 1, 8)),
                                                                        Location(1, 3, 1, 8)),
                                                                   Identifier("z", Location(1, 10, 1, 10))],
                                                                  Location(1, 2, 1, 11)),
                                                    Location(1, 1, 1, 11)),
                                               BinaryOperation(BinaryOperatorKind.PLUS,
                                                               Call(Identifier("t", Location(1, 14, 1, 14)),
                                                                    ArgumentsList([], Location(1, 15, 1, 16)),
                                                                    Location(1, 14, 1, 16)),
                                                               Integer(1, Location(1, 18, 1, 18)),
                                                               Location(1, 14, 1, 18)),
                                               Location(1, 1, 1, 18)),
                               BinaryOperation(BinaryOperatorKind.LEQ,
                                               UnaryOperation(UnaryOperatorKind.MINUS,
                                                              Call(Identifier("t", Location(1, 21, 1, 21)),
                                                                   ArgumentsList([UnaryOperation(
                                                                       UnaryOperatorKind.MINUS,
                                                                       Call(Identifier("r", Location(1, 24, 1, 24)),
                                                                            ArgumentsList([],
                                                                                          Location(1, 25, 1, 26)),
                                                                            Location(1, 24, 1, 26)),
                                                                       Location(1, 23, 1, 26))],
                                                                       Location(1, 22, 1, 27)),
                                                                   Location(1, 21, 1, 27)),
                                                              Location(1, 20, 1, 27)),
                                               Integer(0, Location(1, 30, 1, 30)),
                                               Location(1, 20, 1, 30)),
                               Location(1, 1, 1, 30))


class SimplestAssignParsingTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "x = f(y);"

    def _get_expected(self):
        return AssignStatement(Identifier("x", Location(1, 1, 1, 1)),
                               Call(Identifier("f", Location(1, 5, 1, 5)),
                                    ArgumentsList([Identifier("y", Location(1, 7, 1, 7))],
                                                  Location(1, 6, 1, 8)),
                                    Location(1, 5, 1, 8)),
                               Location(1, 1, 1, 9))

    def _get_rule(self):
        return parse_assign


class TrivialParseParametersTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "()"

    def _get_rule(self):
        return parse_parameters

    def _get_expected(self):
        return ParametersList([], Location(1, 1, 1, 2))


class SimpleParseParametersTestOne(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "(x)"

    def _get_rule(self):
        return parse_parameters

    def _get_expected(self):
        return ParametersList([Identifier("x", Location(1, 2, 1, 2))], Location(1, 1, 1, 3))


class SimpleParseParametersTestTwo(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "(x, z, ab)"

    def _get_rule(self):
        return parse_parameters

    def _get_expected(self):
        return ParametersList([Identifier("x", Location(1, 2, 1, 2)),
                               Identifier("z", Location(1, 5, 1, 5)),
                               Identifier("ab", Location(1, 8, 1, 9))],
                              Location(1, 1, 1, 10))


class SimpleParseCallStatementTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "proc(f(g(x - 1)), y + 1, 2);"

    def _get_rule(self):
        return parse_call_statement

    def _get_expected(self):
        return CallStatement(Call(Identifier("proc", Location(1, 1, 1, 4)),
                                  ArgumentsList([Call(Identifier("f", Location(1, 6, 1, 6)),
                                                      ArgumentsList([Call(Identifier("g", Location(1, 8, 1, 8)),
                                                                          ArgumentsList(
                                                                              [BinaryOperation(BinaryOperatorKind.MINUS,
                                                                                               Identifier("x",
                                                                                                          Location(1,
                                                                                                                   10,
                                                                                                                   1,
                                                                                                                   10)),
                                                                                               Integer(1,
                                                                                                       Location(1, 14,
                                                                                                                1,
                                                                                                                14)),
                                                                                               Location(1, 10, 1,
                                                                                                        14))],
                                                                              Location(1, 9, 1, 15)),
                                                                          Location(1, 8, 1, 15))],
                                                                    Location(1, 7, 1, 16)),
                                                      Location(1, 6, 1, 16)),
                                                 BinaryOperation(BinaryOperatorKind.PLUS,
                                                                 Identifier("y", Location(1, 19, 1, 19)),
                                                                 Integer(1, Location(1, 23, 1, 23)),
                                                                 Location(1, 19, 1, 23)),
                                                 Integer(2, Location(1, 26, 1, 26))],
                                                Location(1, 5, 1, 27)),
                                  Location(1, 1, 1, 27)),
                             Location(1, 1, 1, 28))


class SimplestParseReturnStatementTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "return;"

    def _get_rule(self):
        return parse_return

    def _get_expected(self):
        return ReturnStatement(None, Location(1, 1, 1, 7))


class SimpleParseReturnStatementTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "return -x;"

    def _get_rule(self):
        return parse_return

    def _get_expected(self):
        return ReturnStatement(UnaryOperation(UnaryOperatorKind.MINUS,
                                              Identifier("x", Location(1, 9, 1, 9)),
                                              Location(1, 8, 1, 9)),
                               Location(1, 1, 1, 10))


class SimpleParseIfStatementTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "if (x < 0) {return -x;}"

    def _get_rule(self):
        return parse_if

    def _get_expected(self):
        return IfStatement(BinaryOperation(BinaryOperatorKind.LESS,
                                           Identifier("x", Location(1, 5, 1, 5)),
                                           Integer(0, Location(1, 9, 1, 9)),
                                           Location(1, 4, 1, 10)),
                           Block([ReturnStatement(UnaryOperation(UnaryOperatorKind.MINUS,
                                                                 Identifier("x", Location(1, 21, 1, 21)),
                                                                 Location(1, 20, 1, 21)),
                                                  Location(1, 13, 1, 22))],
                                 Location(1, 12, 1, 23)),
                           None,
                           Location(1, 1, 1, 23))


class SimpleParseIfElseStatementTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "if (z >= 0) {res = 1;} else {throw(z);}"

    def _get_rule(self):
        return parse_if

    def _get_expected(self):
        return IfStatement(BinaryOperation(BinaryOperatorKind.GEQ,
                                           Identifier("z", Location(1, 5, 1, 5)),
                                           Integer(0, Location(1, 10, 1, 10)),
                                           Location(1, 4, 1, 11)),
                           Block([AssignStatement(
                               Identifier("res", Location(1, 14, 1, 16)),
                               Integer(1, Location(1, 20, 1, 20)),
                               Location(1, 14, 1, 21))],
                               Location(1, 13, 1, 22)),
                           Block([CallStatement(Call(Identifier("throw", Location(1, 30, 1, 34)),
                                                     ArgumentsList([Identifier("z", Location(1, 36, 1, 36))],
                                                                   Location(1, 35, 1, 37)),
                                                     Location(1, 30, 1, 37)),
                                                Location(1, 30, 1, 38))],
                                 Location(1, 29, 1, 39)),
                           Location(1, 1, 1, 39))


class SimpleParseBlockTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "{x = 2; y = x; if (c < 0) {return y;}}"

    def _get_rule(self):
        return parse_block

    def _get_expected(self):
        return Block([
            AssignStatement(
                Identifier("x", Location(1, 2, 1, 2)),
                Integer(2, Location(1, 6, 1, 6)),
                Location(1, 2, 1, 7)),
            AssignStatement(
                Identifier("y", Location(1, 9, 1, 9)),
                Identifier("x", Location(1, 13, 1, 13)),
                Location(1, 9, 1, 14)),
            IfStatement(BinaryOperation(BinaryOperatorKind.LESS,
                                        Identifier("c", Location(1, 20, 1, 20)),
                                        Integer(0, Location(1, 24, 1, 24)),
                                        Location(1, 19, 1, 25)),
                        Block([ReturnStatement(Identifier("y", Location(1, 35, 1, 35)),
                                               Location(1, 28, 1, 36))],
                              Location(1, 27, 1, 37)),
                        None,
                        Location(1, 16, 1, 37))
        ],
            Location(1, 1, 1, 38))


class SimpleParseFunctionTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "function foo() {return 42;}"

    def _get_rule(self):
        return parse_subroutine

    def _get_expected(self):
        return SubroutineDecl(SubroutineKind.FUNCTION,
                              Identifier("foo", Location(1, 10, 1, 12)),
                              ParametersList([], Location(1, 13, 1, 14)),
                              Block([ReturnStatement(Integer(42, Location(1, 24, 1, 25)),
                                                     Location(1, 17, 1, 26))],
                                    Location(1, 16, 1, 27)),
                              Location(1, 1, 1, 27))


class SimpleParseProcedureTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "procedure doSomething(x, y) {z = x + y;}"

    def _get_rule(self):
        return parse_subroutine

    def _get_expected(self):
        return SubroutineDecl(SubroutineKind.PROCEDURE,
                              Identifier("doSomething", Location(1, 11, 1, 21)),
                              ParametersList([
                                  Identifier("x", Location(1, 23, 1, 23)),
                                  Identifier("y", Location(1, 26, 1, 26))],
                                  Location(1, 22, 1, 27)),
                              Block([
                                  AssignStatement(Identifier("z", Location(1, 30, 1, 30)),
                                                  BinaryOperation(BinaryOperatorKind.PLUS,
                                                                  Identifier("x", Location(1, 34, 1, 34)),
                                                                  Identifier("y", Location(1, 38, 1, 38)),
                                                                  Location(1, 34, 1, 38)),
                                                  Location(1, 30, 1, 39))],
                                  Location(1, 29, 1, 40)),
                              Location(1, 1, 1, 40))


class SimpleVariableDeclarationTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "var x = 1;"

    def _get_rule(self):
        return parse_variable_declaration

    def _get_expected(self):
        return VariableDeclaration(Identifier("x", Location(1, 5, 1, 5)),
                                   Integer(1, Location(1, 9, 1, 9)),
                                   Location(1, 1, 1, 10))


class FullScriptParsingTest(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        with open('resources/fact7.mas') as file:
            return file.read()

    def _get_rule(self):
        return parse_script

    def _get_expected(self):
        input_var_decl = VariableDeclaration(Identifier("inputVariable", Location(2, 5, 2, 17)),
                                             Integer(0, Location(2, 21, 2, 21)),
                                             Location(2, 1, 2, 22))

        get_three_decl = SubroutineDecl(SubroutineKind.FUNCTION,
                                        Identifier("getThree", Location(4, 10, 4, 17)),
                                        ParametersList([], Location(4, 18, 4, 19)),
                                        Block([VariableDeclaration(Identifier("localVar", Location(5, 9, 5, 16)),
                                                                   Integer(3, Location(5, 20, 5, 20)),
                                                                   Location(5, 5, 5, 21)),
                                               ReturnStatement(Identifier("localVar", Location(6, 12, 6, 19)),
                                                               Location(6, 5, 6, 20))],
                                              Location(4, 21, 7, 1)),
                                        Location(4, 1, 7, 1))

        init_n_six_local_var_init_expr = BinaryOperation(BinaryOperatorKind.PLUS,
                                                         BinaryOperation(BinaryOperatorKind.MUL,
                                                                         Call(Identifier("getThree",
                                                                                         Location(9, 20, 9, 27)),
                                                                              ArgumentsList([], Location(9, 28, 9, 29)),
                                                                              Location(9, 20, 9, 29)),
                                                                         Integer(2, Location(9, 33, 9, 33)),
                                                                         Location(9, 20, 9, 33)),
                                                         Integer(1, Location(9, 37, 9, 37)),
                                                         Location(9, 20, 9, 37))

        init_n_six_local_var_decl = VariableDeclaration(Identifier("localVar", Location(9, 9, 9, 16)),
                                                        init_n_six_local_var_init_expr,
                                                        Location(9, 5, 9, 38))

        input_var_assign = AssignStatement(Identifier("inputVariable", Location(10, 5, 10, 17)),
                                           Identifier("localVar", Location(10, 21, 10, 28)),
                                           Location(10, 5, 10, 29))

        init_n_six_decl = SubroutineDecl(SubroutineKind.PROCEDURE,
                                         Identifier("initNSeven", Location(8, 11, 8, 20)),
                                         ParametersList([], Location(8, 21, 8, 22)),
                                         Block([init_n_six_local_var_decl, input_var_assign],
                                               Location(8, 24, 11, 1)),
                                         Location(8, 1, 11, 1))

        init_n_six_call = CallStatement(Call(Identifier("initNSeven", Location(24, 1, 24, 10)),
                                             ArgumentsList([], Location(24, 11, 24, 12)),
                                             Location(24, 1, 24, 10)),
                                        Location(24, 1, 24, 11))
        ret = ReturnStatement(Call(Identifier("fact", Location(25, 8, 25, 11)),
                                   ArgumentsList([Identifier("inputVariable", Location(25, 13, 25, 25))],
                                                 Location(25, 12, 25, 26)),
                                   Location(25, 8, 25, 26)),
                              Location(25, 1, 25, 27))
        n_zero_if = IfStatement(BinaryOperation(BinaryOperatorKind.EQ,
                                                Identifier("n", Location(14, 13, 14, 13)),
                                                Integer(0, Location(14, 18, 14, 18)),
                                                Location(14, 12, 14, 19)),
                                Block([ReturnStatement(Integer(1, Location(15, 20, 15, 20)),
                                                       Location(15, 13, 15, 21))],
                                      Location(14, 21, 16, 9)),
                                None,
                                Location(14, 9, 16, 9))
        return_rec_call = ReturnStatement(BinaryOperation(BinaryOperatorKind.MUL,
                                                          Identifier("n", Location(17, 16, 17, 16)),
                                                          Call(Identifier("fact", Location(17, 20, 17, 23)),
                                                               ArgumentsList([BinaryOperation(BinaryOperatorKind.MINUS,
                                                                                              Identifier("n",
                                                                                                         Location(17,
                                                                                                                  25,
                                                                                                                  17,
                                                                                                                  25)),
                                                                                              Integer(1,
                                                                                                      Location(17, 29,
                                                                                                               17, 29)),
                                                                                              Location(17, 25, 17,
                                                                                                       29))],
                                                                             Location(17, 24, 17, 30)),
                                                               Location(17, 20, 17, 30)),
                                                          Location(17, 16, 17, 30)),
                                          Location(17, 9, 17, 31))
        fact_main_if_then = Block([n_zero_if, return_rec_call],
                                  Location(13, 17, 18, 5))
        fact_main_if_else = Block([ReturnStatement(UnaryOperation(UnaryOperatorKind.MINUS,
                                                                  Integer(1, Location(19, 17, 19, 17)),
                                                                  Location(19, 16, 19, 17)),
                                                   Location(19, 9, 19, 18))],
                                  Location(18, 12, 20, 5))
        fact_main_if = IfStatement(BinaryOperation(BinaryOperatorKind.GEQ,
                                                   Identifier("n", Location(13, 9, 13, 9)),
                                                   Integer(0, Location(13, 14, 13, 14)),
                                                   Location(13, 8, 13, 15)),
                                   fact_main_if_then,
                                   fact_main_if_else,
                                   Location(13, 5, 20, 5))
        fact_body = Block([fact_main_if], Location(12, 18, 21, 1))
        fact_decl = SubroutineDecl(SubroutineKind.FUNCTION,
                                   Identifier("fact", Location(12, 10, 12, 13)),
                                   ParametersList([Identifier("n", Location(12, 15, 12, 15))],
                                                  Location(12, 14, 12, 16)),
                                   fact_body,
                                   Location(12, 1, 21, 1))
        return Script([input_var_decl, get_three_decl, init_n_six_decl, fact_decl, init_n_six_call, ret],
                      Location(25, 28, 25, 28))


class AssignErrorTest(TestBases.FailedParsingTestBase):
    def _get_input(self):
        return "x == 2;"

    def _get_rule(self):
        return parse_assign

    def _get_expected_exception(self):
        return ParserException(Token("==", "==", TokenLocation(1, 3, 4)), ["="])


class VariableDeclarationErrorTest(TestBases.FailedParsingTestBase):
    def _get_input(self):
        return "var x;"

    def _get_rule(self):
        return parse_variable_declaration

    def _get_expected_exception(self):
        return ParserException(Token(";", ";", TokenLocation(1, 6, 6)), ["="])


class MissingBlockErrorTest(TestBases.FailedParsingTestBase):
    def _get_input(self):
        return "if 1>0 x = 1;"

    def _get_rule(self):
        return parse_if

    def _get_expected_exception(self):
        return ParserException(Token("IDENT", "x", TokenLocation(1, 8, 8)), ["{"])


class AccidentalAssignErrorTest(TestBases.FailedParsingTestBase):
    def _get_input(self):
        return "if (x=0) {return 1;}"

    def _get_rule(self):
        return parse_if

    def _get_expected_exception(self):
        return ParserException(Token("=", "=", TokenLocation(1, 6, 6)), [")"])


class MissingSemicolonErrorTest(TestBases.FailedParsingTestBase):
    def _get_input(self):
        return "return 1"

    def _get_rule(self):
        return parse_return

    def _get_expected_exception(self):
        return ParserException(Token("EOF", "\0", TokenLocation(1, 9, 9)), [";"])


class IllegalInnerFunction(TestBases.FailedParsingTestBase):
    def _get_input(self):
        return "function f() {function g() {}}"

    def _get_rule(self):
        return parse_subroutine

    def _get_expected_exception(self):
        return ParserException(Token("function", "function", TokenLocation(1, 15, 22)), ["return", "if", "IDENT"])


class MissingRightOperandTest(TestBases.FailedParsingTestBase):
    def _get_input(self):
        return "(x>=)"

    def _get_rule(self):
        return parse_expr

    def _get_expected_exception(self):
        return ParserException(Token(")", ")", TokenLocation(1, 5, 5)), ["(", "IDENT", "INT"])
