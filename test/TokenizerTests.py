import unittest

from parsing.Tokenizer import Tokenizer, Token, UnexpectedCharException, IllegalRollbackException


class TestBases:
    class SuccessfulTokenizingTestBase(unittest.TestCase):
        def _get_input(self):
            raise NotImplementedError("Must define input string in derived test")

        def _get_expected(self):
            raise NotImplementedError("Must define expected tokens in derived test")

        def test_tokenization(self):
            tokenizer = Tokenizer(self._get_input())
            self.assertEqual(tokenizer.current(), Token("SOF", None, 1, 0, 0))
            last_token = tokenizer.current()
            for expected_token in self._get_expected():
                tokenizer.advance()
                self.assertEqual(tokenizer.current(), expected_token)
                last_token = tokenizer.current()
            tokenizer.advance()
            self.assertEqual(tokenizer.current(),
                             Token("EOF", "\0", last_token.line, last_token.column_end + 1,
                                   last_token.column_end + 1))
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
            self.assertEqual(tokenizer.current(), Token("SOF", None, 1, 0, 0))
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
        return [Token("if", "if", 1, 1, 2)]


class SimpleTest(TestBases.SuccessfulTokenizingTestBase):
    def _get_input(self):
        return "if (cond) { return 1; } else {return -4;}"

    def _get_expected(self):
        return [Token("if", "if", 1, 1, 2),
                Token("(", "(", 1, 4, 4),
                Token("IDENT", "cond", 1, 5, 8),
                Token(")", ")", 1, 9, 9),
                Token("{", "{", 1, 11, 11),
                Token("return", "return", 1, 13, 18),
                Token("INT", 1, 1, 20, 20),
                Token(";", ";", 1, 21, 21),
                Token("}", "}", 1, 23, 23),
                Token("else", "else", 1, 25, 28),
                Token("{", "{", 1, 30, 30),
                Token("return", "return", 1, 31, 36),
                Token("-", "-", 1, 38, 38),
                Token("INT", 4, 1, 39, 39),
                Token(";", ";", 1, 40, 40),
                Token("}", "}", 1, 41, 41)]


class MultilineTest(TestBases.SuccessfulTokenizingTestBase):
    def _get_input(self):
        return "if (c) {\n    return -1;\n} else { return 2;}\n\na = 2;"

    def _get_expected(self):
        return [Token("if", "if", 1, 1, 2),
                Token("(", "(", 1, 4, 4),
                Token("IDENT", "c", 1, 5, 5),
                Token(")", ")", 1, 6, 6),
                Token("{", "{", 1, 8, 8),
                Token("return", "return", 2, 5, 10),
                Token("-", "-", 2, 12, 12),
                Token("INT", 1, 2, 13, 13),
                Token(";", ";", 2, 14, 14),
                Token("}", "}", 3, 1, 1),
                Token("else", "else", 3, 3, 6),
                Token("{", "{", 3, 8, 8),
                Token("return", "return", 3, 10, 15),
                Token("INT", 2, 3, 17, 17),
                Token(";", ";", 3, 18, 18),
                Token("}", "}", 3, 19, 19),
                Token("IDENT", "a", 5, 1, 1),
                Token("=", "=", 5, 3, 3),
                Token("INT", 2, 5, 5, 5),
                Token(";", ";", 5, 6, 6)]


class BoolExpr(TestBases.SuccessfulTokenizingTestBase):
    def _get_input(self):
        return "(c) | (b & (a < 3)) | !d"

    def _get_expected(self):
        return [Token("(", "(", 1, 1, 1),
                Token("IDENT", "c", 1, 2, 2),
                Token(")", ")", 1, 3, 3),
                Token("|", "|", 1, 5, 5),
                Token("(", "(", 1, 7, 7),
                Token("IDENT", "b", 1, 8, 8),
                Token("&", "&", 1, 10, 10),
                Token("(", "(", 1, 12, 12),
                Token("IDENT", "a", 1, 13, 13),
                Token("<", "<", 1, 15, 15),
                Token("INT", 3, 1, 17, 17),
                Token(")", ")", 1, 18, 18),
                Token(")", ")", 1, 19, 19),
                Token("|", "|", 1, 21, 21),
                Token("!", "!", 1, 23, 23),
                Token("IDENT", "d", 1, 24, 24)]


class SimplestExceptionTest(TestBases.ExceptionTokenizingTestBase):
    def _get_input(self):
        return "! #"

    def _get_expected_tokens(self):
        return [Token("!", "!", 1, 1, 1)]

    def _get_expected_exception(self):
        return UnexpectedCharException('#', 1, 3)


class TabTest(TestBases.SuccessfulTokenizingTestBase):
    def _get_input(self):
        return "{\treturn";

    def _get_expected(self):
        return [Token("{", "{", 1, 1, 1),
                Token("return", "return", 1, 6, 11)]


class KeywordTest(TestBases.SuccessfulTokenizingTestBase):
    def _get_input(self):
        return "if els elseif else"

    def _get_expected(self):
        return [Token("if", "if", 1, 1, 2),
                Token("IDENT", "els", 1, 4, 6),
                Token("IDENT", "elseif", 1, 8, 13),
                Token("else", "else", 1, 15, 18)]


class ComparisonTest(TestBases.SuccessfulTokenizingTestBase):
    def _get_input(self):
        return "a < <= = == === ==== >= >"

    def _get_expected(self):
        return [Token("IDENT", "a", 1, 1, 1),
                Token("<", "<", 1, 3, 3),
                Token("<=", "<=", 1, 5, 6),
                Token("=", "=", 1, 8, 8),
                Token("==", "==", 1, 10, 11),
                Token("==", "==", 1, 13, 14),
                Token("=", "=", 1, 15, 15),
                Token("==", "==", 1, 17, 18),
                Token("==", "==", 1, 19, 20),
                Token(">=", ">=", 1, 22, 23),
                Token(">", ">", 1, 25, 25)]


class CallTest(TestBases.SuccessfulTokenizingTestBase):
    def _get_input(self):
        return "Foo(a, caBa+ d, -3*2, 0)"

    def _get_expected(self):
        return [Token("IDENT", "Foo", 1, 1, 3),
                Token("(", "(", 1, 4, 4),
                Token("IDENT", "a", 1, 5, 5),
                Token(",", ",", 1, 6, 6),
                Token("IDENT", "caBa", 1, 8, 11),
                Token("+", "+", 1, 12, 12),
                Token("IDENT", "d", 1, 14, 14),
                Token(",", ",", 1, 15, 15),
                Token("-", "-", 1, 17, 17),
                Token("INT", 3, 1, 18, 18),
                Token("*", "*", 1, 19, 19),
                Token("INT", 2, 1, 20, 20),
                Token(",", ",", 1, 21, 21),
                Token("INT", 0, 1, 23, 23),
                Token(")", ")", 1, 24, 24)]


class IntsTest(TestBases.SuccessfulTokenizingTestBase):
    def _get_input(self):
        return "1 10 001 -03 - 2 1x x1 --3"

    def _get_expected(self):
        return [Token("INT", 1, 1, 1, 1),
                Token("INT", 10, 1, 3, 4),
                Token("INT", 1, 1, 6, 8),
                Token("-", "-", 1, 10, 10),
                Token("INT", 3, 1, 11, 12),
                Token("-", "-", 1, 14, 14),
                Token("INT", 2, 1, 16, 16),
                Token("INT", 1, 1, 18, 18),
                Token("IDENT", "x", 1, 19, 19),
                Token("IDENT", "x1", 1, 21, 22),
                Token("-", "-", 1, 24, 24),
                Token("-", "-", 1, 25, 25),
                Token("INT", 3, 1, 26, 26)]


class SimplestRollbackTest(unittest.TestCase):
    def test_tokenization(self):
        tokenizer = Tokenizer("if\nelse\n\n0 -10")
        expected_tokens = [Token("SOF", None, 1, 0, 0),
                           Token("if", "if", 1, 1, 2),
                           Token("else", "else", 2, 1, 4),
                           Token("INT", 0, 4, 1, 1),
                           Token("-", "-", 4, 3, 3),
                           Token("INT", 10, 4, 4, 5),
                           Token("EOF", "\0", 4, 6, 6)]
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
        expected_tokens = [Token("SOF", None, 1, 0, 0),
                           Token("-", "-", 1, 1, 1),
                           Token("INT", 1, 1, 2, 2),
                           Token("if", "if", 1, 4, 5)]
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
        return [Token("if", "if", 1, 1, 2),
                Token("IDENT", "c", 1, 4, 4),
                Token("return", "return", 2, 5, 10),
                Token("INT", 1, 2, 12, 12)]


class SimpleTabTest(TestBases.SuccessfulTokenizingTestBase):
    def _get_input(self):
        return "if\n\treturn\n\t\tx"

    def _get_expected(self):
        return [Token("if", "if", 1, 1, 2),
                Token("return", "return", 2, 5, 10),
                Token("IDENT", "x", 3, 9, 9)]


if __name__ == '__main__':
    unittest.main()
