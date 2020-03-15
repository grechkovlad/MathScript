class Or:
    def __init__(self, list):
        self._list = list


class Concat:
    def __init__(self, list):
        self._list = list


class Star:
    def __init__(self, expr):
        self.expr = expr


class Question:
    def __init__(self, expr):
        self.expr = expr


class Terminal:
    pass


class Literal(Terminal):
    def __init__(self, str):
        self._str = str


class NonTerminal:
    def __init__(self, name):
        self.name = name
        self.rule = None


class NamedTerminal():
    def __init__(self, name):
        self.name = name
