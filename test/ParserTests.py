import unittest

from parsing.Tokenizer import Tokenizer
from parsing.Parser import parse_a
from parsing.Ast import *


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
        return parse_a


class SimpleExpressionTestOne(TestBases.SuccessfulParsingTestBase):
    def _get_input(self):
        return "(x + 3) < 3 & 3 * x | x < y"

    def _get_rule(self):
        return parse_a

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
        return parse_a

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
        return parse_a

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
