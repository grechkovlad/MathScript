import re


class Tokenizer:
    def __init__(self, text):
        self._text = text
        self._text_pos = -1
        self._line = 1
        self._column = 0
        self._currents = [Token("SOF", None, 1, 0, 0), None]
        self._currents_index = 0

    def current(self):
        return self._currents[self._currents_index]

    def advance(self):
        if self._currents_index == 0 and self._currents[1] is not None:
            self._currents_index = 1
            return
        if self.current().type == "EOF":
            raise EOFError()
        self._text_pos += 1
        self._column += 1
        next_token = self._read_next()
        if self._currents_index == 0:
            self._currents[1] = next_token
            self._currents_index = 1
        else:
            self._currents[0] = self._currents[1]
            self._currents[1] = next_token

    def rollback(self):
        if self._currents_index == 0:
            raise IllegalRollbackException()
        self._currents_index = 0

    def _read_next(self):
        self._eat_whitespaces()
        pos = self._text_pos
        if pos >= len(self._text):
            return Token("EOF", '\0', self._line, self._column, self._column)
        if self._text[pos] in ['(', ')', '{', '}', '!', '|', '&', '+', '-', '*', ',', ';']:
            return Token(self._text[pos], self._text[pos], self._line, self._column, self._column)
        if self._text[pos] in ['<', '>', '=']:
            if self._char_equals(pos + 1, '='):
                next_token = Token(self._text[pos: pos + 2], self._text[pos: pos + 2],
                                   self._line, self._column, self._column + 1)
                self._text_pos += 1
                self._column += 1
                return next_token
            else:
                return Token(self._text[pos], self._text[pos], self._line, self._column, self._column)
        word_match = re.match("[a-zA-Z][a-zA-Z0-9]*", self._text[pos:])
        if word_match:
            match_str = word_match.group(0)
            if match_str in ["if", "else", "function", "procedure", "return"]:
                next_token = Token(match_str, match_str, self._line, self._column, self._column + len(match_str) - 1)
            else:
                next_token = Token("IDENT", match_str, self._line, self._column,
                                   self._column + len(match_str) - 1)
            self._text_pos += len(match_str) - 1
            self._column += len(match_str) - 1
            return next_token
        num_match = re.match(r"\d+", self._text[pos:])
        if num_match:
            match_str = num_match.group(0)
            next_token = Token("INT", int(match_str), self._line, self._column, self._column + len(match_str) - 1)
            self._text_pos += len(match_str) - 1
            self._column += len(match_str) - 1
            return next_token
        raise UnexpectedCharException(self._text[self._text_pos], self._line, self._column)

    def _char_equals(self, pos, c):
        return pos < len(self._text) and self._text[pos] == c

    def _eat_whitespaces(self):
        while self._text_pos < len(self._text) and (self._text[self._text_pos] in [' ', '\n']):
            if self._text[self._text_pos] == ' ':
                self._column += 1
            else:
                self._line += 1
                self._column = 1
            self._text_pos += 1


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


class UnexpectedCharException(Exception):
    def __init__(self, char, line, column):
        super(UnexpectedCharException, self).__init__("Unexpected character '%s' at %d:%d" % (char, line, column))
        self.char = char
        self.line = line
        self.column = column

    def __eq__(self, other):
        return self.char == other.char and self.line == other.line and self.column == other.column


class IllegalRollbackException(Exception):
    def __init__(self):
        super(IllegalRollbackException, self).__init__("Must advance before rolling back")
