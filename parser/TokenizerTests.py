import unittest

from parser.Tokenizer import Tokenizer, Token, TokenizerException


class TestBases:
    class SuccessfulTokenizingTestBase(unittest.TestCase):
        def _get_input(self):
            raise NotImplementedError("Must define input string in derived test")

        def _get_expected(self):
            raise NotImplementedError("Must define expected tokens in derived test")

        def test_tokenization(self):
            tokenizer = Tokenizer(self._get_input())
            self.assertEqual(tokenizer.current, Token("SOF", None, 1, 0, 0))
            last_token = tokenizer.current
            for expected_token in self._get_expected():
                tokenizer.advance()
                self.assertEqual(tokenizer.current, expected_token)
                last_token = tokenizer.current
            tokenizer.advance()
            self.assertEqual(tokenizer.current,
                             Token("EOF", "\0", last_token.line, last_token.column_end + 1,
                                   last_token.column_end + 1))

    class ExceptionTokenizingTestBase(unittest.TestCase):
        def _get_input(self):
            raise NotImplementedError("Must define input string in derived test")

        def _get_expected_tokens(self):
            raise NotImplementedError("Must define expected tokens in derived test")

        def _get_expected_exception(self):
            raise NotImplementedError("Must define expected tokens in derived test")

        def test_tokenization(self):
            tokenizer = Tokenizer(self._get_input())
            self.assertEqual(tokenizer.current, Token("SOF", None, 1, 0, 0))
            for expected_token in self._get_expected_tokens():
                tokenizer.advance()
                self.assertEqual(tokenizer.current, expected_token)
            with self.assertRaises(TokenizerException) as cm:
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
        return TokenizerException('#', 1, 3)


if __name__ == '__main__':
    unittest.main()
