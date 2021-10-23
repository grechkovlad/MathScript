import unittest

from parsing.Tokenizer import Tokenizer, Token, UnexpectedCharException, IllegalRollbackException, Location


class TestBases:
    class SuccessfulTokenizingTestBase(unittest.TestCase):
        def _get_input(self):
            raise NotImplementedError("Must define input string in derived test")

        def _get_expected(self):
            raise NotImplementedError("Must define expected tokens in derived test")

        def test_tokenization(self):
            tokenizer = Tokenizer(self._get_input())
            self.assertEqual(tokenizer.current(), Token("SOF", None, Location(1, 0, 0)))
            last_token = tokenizer.current()
            for expected_token in self._get_expected():
                tokenizer.advance()
                self.assertEqual(tokenizer.current(), expected_token)
                last_token = tokenizer.current()
            tokenizer.advance()
            self.assertEqual(tokenizer.current(),
                             Token("EOF",
                                   "\0",
                                   Location(last_token.location.line, last_token.location.column_end + 1,
                                            last_token.location.column_end + 1)))
            with self.assertRaises(EOFError):
                tokenizer.advance()

    class ExceptionTokenizingTestBase(unittest.TestCase):
        def _get_input(self):
            raise NotImplementedError("Must define input string in derived test")

        def _get_expected_tokens(self):
            raise NotImplementedError("Must define expected tokens in derived test")

        def _get_expected_exception(self):
            raise NotImplementedError("Must define expected exception in derived test")

        def test_tokenization(self):
            tokenizer = Tokenizer(self._get_input())
            self.assertEqual(tokenizer.current(), Token("SOF", None, Location(1, 0, 0)))
            for expected_token in self._get_expected_tokens():
                tokenizer.advance()
                self.assertEqual(tokenizer.current(), expected_token)
            with self.assertRaises(UnexpectedCharException) as cm:
                tokenizer.advance()
            self.assertEqual(self._get_expected_exception(), cm.exception)


class SimplestTest(TestBases.SuccessfulTokenizingTestBase):
    def _get_input(self):
        return "if"

    def _get_expected(self):
        return [Token("if", "if", Location(1, 1, 2))]


class SimpleTest(TestBases.SuccessfulTokenizingTestBase):
    def _get_input(self):
        return "if (cond) { return 1; } else {return -4;}"

    def _get_expected(self):
        return [Token("if", "if", Location(1, 1, 2)),
                Token("(", "(", Location(1, 4, 4)),
                Token("IDENT", "cond", Location(1, 5, 8)),
                Token(")", ")", Location(1, 9, 9)),
                Token("{", "{", Location(1, 11, 11)),
                Token("return", "return", Location(1, 13, 18)),
                Token("INT", 1, Location(1, 20, 20)),
                Token(";", ";", Location(1, 21, 21)),
                Token("}", "}", Location(1, 23, 23)),
                Token("else", "else", Location(1, 25, 28)),
                Token("{", "{", Location(1, 30, 30)),
                Token("return", "return", Location(1, 31, 36)),
                Token("-", "-", Location(1, 38, 38)),
                Token("INT", 4, Location(1, 39, 39)),
                Token(";", ";", Location(1, 40, 40)),
                Token("}", "}", Location(1, 41, 41))]


class MultilineTest(TestBases.SuccessfulTokenizingTestBase):
    def _get_input(self):
        return "if (c) {\n    return -1;\n} else { return 2;}\n\na = 2;"

    def _get_expected(self):
        return [Token("if", "if", Location(1, 1, 2)),
                Token("(", "(", Location(1, 4, 4)),
                Token("IDENT", "c", Location(1, 5, 5)),
                Token(")", ")", Location(1, 6, 6)),
                Token("{", "{", Location(1, 8, 8)),
                Token("return", "return", Location(2, 5, 10)),
                Token("-", "-", Location(2, 12, 12)),
                Token("INT", 1, Location(2, 13, 13)),
                Token(";", ";", Location(2, 14, 14)),
                Token("}", "}", Location(3, 1, 1)),
                Token("else", "else", Location(3, 3, 6)),
                Token("{", "{", Location(3, 8, 8)),
                Token("return", "return", Location(3, 10, 15)),
                Token("INT", 2, Location(3, 17, 17)),
                Token(";", ";", Location(3, 18, 18)),
                Token("}", "}", Location(3, 19, 19)),
                Token("IDENT", "a", Location(5, 1, 1)),
                Token("=", "=", Location(5, 3, 3)),
                Token("INT", 2, Location(5, 5, 5)),
                Token(";", ";", Location(5, 6, 6))]


class BoolExpr(TestBases.SuccessfulTokenizingTestBase):
    def _get_input(self):
        return "(c) | (b & (a < 3)) | !d"

    def _get_expected(self):
        return [Token("(", "(", Location(1, 1, 1)),
                Token("IDENT", "c", Location(1, 2, 2)),
                Token(")", ")", Location(1, 3, 3)),
                Token("|", "|", Location(1, 5, 5)),
                Token("(", "(", Location(1, 7, 7)),
                Token("IDENT", "b", Location(1, 8, 8)),
                Token("&", "&", Location(1, 10, 10)),
                Token("(", "(", Location(1, 12, 12)),
                Token("IDENT", "a", Location(1, 13, 13)),
                Token("<", "<", Location(1, 15, 15)),
                Token("INT", 3, Location(1, 17, 17)),
                Token(")", ")", Location(1, 18, 18)),
                Token(")", ")", Location(1, 19, 19)),
                Token("|", "|", Location(1, 21, 21)),
                Token("!", "!", Location(1, 23, 23)),
                Token("IDENT", "d", Location(1, 24, 24))]


class SimplestExceptionTest(TestBases.ExceptionTokenizingTestBase):
    def _get_input(self):
        return "! #"

    def _get_expected_tokens(self):
        return [Token("!", "!", Location(1, 1, 1))]

    def _get_expected_exception(self):
        return UnexpectedCharException('#', 1, 3)


class TabTest(TestBases.SuccessfulTokenizingTestBase):
    def _get_input(self):
        return "{\treturn";

    def _get_expected(self):
        return [Token("{", "{", Location(1, 1, 1)),
                Token("return", "return", Location(1, 6, 11))]


class KeywordTest(TestBases.SuccessfulTokenizingTestBase):
    def _get_input(self):
        return "if els elseif else"

    def _get_expected(self):
        return [Token("if", "if", Location(1, 1, 2)),
                Token("IDENT", "els", Location(1, 4, 6)),
                Token("IDENT", "elseif", Location(1, 8, 13)),
                Token("else", "else", Location(1, 15, 18))]


class ComparisonTest(TestBases.SuccessfulTokenizingTestBase):
    def _get_input(self):
        return "a < <= = == === ==== >= >"

    def _get_expected(self):
        return [Token("IDENT", "a", Location(1, 1, 1)),
                Token("<", "<", Location(1, 3, 3)),
                Token("<=", "<=", Location(1, 5, 6)),
                Token("=", "=", Location(1, 8, 8)),
                Token("==", "==", Location(1, 10, 11)),
                Token("==", "==", Location(1, 13, 14)),
                Token("=", "=", Location(1, 15, 15)),
                Token("==", "==", Location(1, 17, 18)),
                Token("==", "==", Location(1, 19, 20)),
                Token(">=", ">=", Location(1, 22, 23)),
                Token(">", ">", Location(1, 25, 25))]


class CallTest(TestBases.SuccessfulTokenizingTestBase):
    def _get_input(self):
        return "Foo(a, caBa+ d, -3*2, 0)"

    def _get_expected(self):
        return [Token("IDENT", "Foo", Location(1, 1, 3)),
                Token("(", "(", Location(1, 4, 4)),
                Token("IDENT", "a", Location(1, 5, 5)),
                Token(",", ",", Location(1, 6, 6)),
                Token("IDENT", "caBa", Location(1, 8, 11)),
                Token("+", "+", Location(1, 12, 12)),
                Token("IDENT", "d", Location(1, 14, 14)),
                Token(",", ",", Location(1, 15, 15)),
                Token("-", "-", Location(1, 17, 17)),
                Token("INT", 3, Location(1, 18, 18)),
                Token("*", "*", Location(1, 19, 19)),
                Token("INT", 2, Location(1, 20, 20)),
                Token(",", ",", Location(1, 21, 21)),
                Token("INT", 0, Location(1, 23, 23)),
                Token(")", ")", Location(1, 24, 24))]


class IntsTest(TestBases.SuccessfulTokenizingTestBase):
    def _get_input(self):
        return "1 10 001 -03 - 2 1x x1 --3"

    def _get_expected(self):
        return [Token("INT", 1, Location(1, 1, 1)),
                Token("INT", 10, Location(1, 3, 4)),
                Token("INT", 1, Location(1, 6, 8)),
                Token("-", "-", Location(1, 10, 10)),
                Token("INT", 3, Location(1, 11, 12)),
                Token("-", "-", Location(1, 14, 14)),
                Token("INT", 2, Location(1, 16, 16)),
                Token("INT", 1, Location(1, 18, 18)),
                Token("IDENT", "x", Location(1, 19, 19)),
                Token("IDENT", "x1", Location(1, 21, 22)),
                Token("-", "-", Location(1, 24, 24)),
                Token("-", "-", Location(1, 25, 25)),
                Token("INT", 3, Location(1, 26, 26))]


class SimplestRollbackTest(unittest.TestCase):
    def test_tokenization(self):
        tokenizer = Tokenizer("if\nelse\n\n0 -10")
        expected_tokens = [Token("SOF", None, Location(1, 0, 0)),
                           Token("if", "if", Location(1, 1, 2)),
                           Token("else", "else", Location(2, 1, 4)),
                           Token("INT", 0, Location(4, 1, 1)),
                           Token("-", "-", Location(4, 3, 3)),
                           Token("INT", 10, Location(4, 4, 5)),
                           Token("EOF", "\0", Location(4, 6, 6))]
        self.assertEqual(tokenizer.current(), expected_tokens[0])
        tokenizer.advance()
        self.assertEqual(tokenizer.current(), expected_tokens[1])
        tokenizer.rollback()
        self.assertEqual(tokenizer.current(), expected_tokens[0])
        tokenizer.advance()
        self.assertEqual(tokenizer.current(), expected_tokens[1])
        tokenizer.advance()
        self.assertEqual(tokenizer.current(), expected_tokens[2])
        tokenizer.advance()
        self.assertEqual(tokenizer.current(), expected_tokens[3])
        tokenizer.advance()
        self.assertEqual(tokenizer.current(), expected_tokens[4])
        tokenizer.rollback()
        self.assertEqual(tokenizer.current(), expected_tokens[3])
        tokenizer.advance()
        self.assertEqual(tokenizer.current(), expected_tokens[4])
        tokenizer.advance()
        self.assertEqual(tokenizer.current(), expected_tokens[5])
        tokenizer.advance()
        self.assertEqual(tokenizer.current(), expected_tokens[6])
        tokenizer.rollback()
        self.assertEqual(tokenizer.current(), expected_tokens[5])
        tokenizer.advance()
        self.assertEqual(tokenizer.current(), expected_tokens[6])
        with self.assertRaises(EOFError) as cm:
            tokenizer.advance()


class SimplestIllegalRollbackTest(unittest.TestCase):
    def test_tokenization(self):
        tokenizer = Tokenizer("if else")
        with self.assertRaises(IllegalRollbackException):
            tokenizer.rollback()


class IllegalRollbackTest(unittest.TestCase):
    def test_tokenization(self):
        tokenizer = Tokenizer("-1 if 3")
        expected_tokens = [Token("SOF", None, Location(1, 0, 0)),
                           Token("-", "-", Location(1, 1, 1)),
                           Token("INT", 1, Location(1, 2, 2)),
                           Token("if", "if", Location(1, 4, 5))]
        self.assertEqual(tokenizer.current(), expected_tokens[0])
        tokenizer.advance()
        tokenizer.rollback()
        self.assertEqual(tokenizer.current(), expected_tokens[0])
        tokenizer.advance()
        self.assertEqual(tokenizer.current(), expected_tokens[1])
        tokenizer.advance()
        self.assertEqual(tokenizer.current(), expected_tokens[2])
        tokenizer.advance()
        self.assertEqual(tokenizer.current(), expected_tokens[3])
        tokenizer.rollback()
        self.assertEqual(tokenizer.current(), expected_tokens[2])
        with self.assertRaises(IllegalRollbackException):
            tokenizer.rollback()


class TabTestTwo(TestBases.SuccessfulTokenizingTestBase):
    def _get_input(self):
        return "if c\n\treturn 1"

    def _get_expected(self):
        return [Token("if", "if", Location(1, 1, 2)),
                Token("IDENT", "c", Location(1, 4, 4)),
                Token("return", "return", Location(2, 5, 10)),
                Token("INT", 1, Location(2, 12, 12))]


class SimpleTabTest(TestBases.SuccessfulTokenizingTestBase):
    def _get_input(self):
        return "if\n\treturn\n\t\tx"

    def _get_expected(self):
        return [Token("if", "if", Location(1, 1, 2)),
                Token("return", "return", Location(2, 5, 10)),
                Token("IDENT", "x", Location(3, 9, 9))]


if __name__ == '__main__':
    unittest.main()
