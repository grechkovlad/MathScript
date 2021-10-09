import re


class Tokenizer:
    def __init__(self, text):
        self._text = text
        self._pos = -1
        self._line = 1
        self._column = 0
        self.current = Token("SOF", None, 1, 0, 0)

    def advance(self):
        if self.current.type == "EOF":
            raise EOFError()
        self._pos += 1
        self._column += 1
        self._update_current()

    def _update_current(self):
        self._eat_whitespaces()
        pos = self._pos
        if pos >= len(self._text):
            self.current = Token("EOF", '\0', self._line, self._column, self._column)
            return
        if self._text[pos] in ['(', ')', '{', '}', '!', '|', '&', '+', '-', '*', ',', ';']:
            self.current = Token(self._text[pos], self._text[pos], self._line, self._column, self._column)
            return
        if self._text[pos] in ['<', '>', '=']:
            if self._char_equals(pos + 1, '='):
                self.current = Token(self._text[pos: pos + 2], self._text[pos: pos + 2],
                                     self._line, self._column, self._column + 1)
                self._pos += 1
                self._column += 1
            else:
                self.current = Token(self._text[pos], self._text[pos], self._line, self._column, self._column)
            return
        word_match = re.match("[a-zA-Z][a-zA-Z0-9]*", self._text[pos:])
        if word_match:
            match_str = word_match.group(0)
            if match_str in ["if", "else", "function", "procedure", "return"]:
                self.current = Token(match_str, match_str, self._line, self._column, self._column + len(match_str) - 1)
            else:
                self.current = Token("IDENT", match_str, self._line, self._column,
                                     self._column + len(match_str) - 1)
            self._pos += len(match_str) - 1
            self._column += len(match_str) - 1
            return
        num_match = re.match(r"\d+", self._text[pos:])
        if num_match:
            match_str = num_match.group(0)
            self.current = Token("INT", int(match_str), self._line, self._column, self._column + len(match_str) - 1)
            self._pos += len(match_str) - 1
            self._column += len(match_str) - 1
            return
        raise TokenizerException(self._text[self._pos], self._line, self._column)

    def _char_equals(self, pos, c):
        return pos < len(self._text) and self._text[pos] == c

    def _eat_whitespaces(self):
        while self._pos < len(self._text) and (self._text[self._pos] in [' ', '\n']):
            if self._text[self._pos] == ' ':
                self._column += 1
            else:
                self._line += 1
                self._column = 1
            self._pos += 1


class Token:
    def __init__(self, type, value, line, column_start, column_end):
        self.type = type
        self.value = value
        self.line = line
        self.column_start = column_start
        self.column_end = column_end

    def __eq__(self, other):
        return self.type == other.type \
               and self.value == other.value \
               and self.line == other.line \
               and self.column_start == other.column_start \
               and self.column_end == other.column_end

    def __str__(self):
        return "type: %s val: %s line: %d column_start: %d column_end: %d" % (
            self.type, self.value, self.line, self.column_start, self.column_end)


class TokenizerException(Exception):
    def __init__(self, char, line, column):
        super(TokenizerException, self).__init__("Unexpected character '%s' at %d:%d" % (char, line, column))
        self.char = char
        self.line = line
        self.column = column

    def __eq__(self, other):
        return self.char == other.char and self.line == other.line and self.column == other.column
