class Or:
    def __init__(self, list):
        self.list = list


class Concat:
    def __init__(self, list):
        self.list = list


class Star:
    def __init__(self, expr):
        self.expr = expr


class Question:
    def __init__(self, expr):
        self.expr = expr


class Terminal:
    pass


class Literal(Terminal):
    def __init__(self, name):
        self.name = name


class NonTerminal:
    def __init__(self, name):
        self.name = name
        self.rule = None


class NamedTerminal(Terminal):
    def __init__(self, name):
        self.name = name
