class Or:
    pass


class Concat:
    def __init__(self, list):
        self._list = list


class Star:
    pass


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


MODULE = Literal("MODULE")
IDENT = Terminal("IDENT")
SEMICOLON = Literal(";")
BEGIN = Literal("BEGIN")
END = Literal("END")
DOT = Literal(".")
COMMA = Literal(",")
PLUS = Literal("+")
MINUS = Literal("-")
OR = Literal("OR")

module = NonTerminal("module")
identList = NonTerminal("identList")
declarations = NonTerminal("declarations")
statementSequence = NonTerminal("statementSequence")
expression = NonTerminal("expression")
type = NonTerminal("type")
procedureDeclaration = NonTerminal("procedureDeclaration")
functionDeclaration = NonTerminal("functionDeclaration")
statement = NonTerminal("statement")
simpleExpression = NonTerminal("simpleExpression")
arrayType = NonTerminal("arrayType")
recordType = NonTerminal("recordType")
procedureHeading = NonTerminal("procedureHeading")
subroutineBody = NonTerminal("subroutineBody")
functionHeading = NonTerminal("functionHeading")
assignment = NonTerminal("assignment")
call = NonTerminal("call")
ifStatement = NonTerminal("ifStatement")
whileStatement = NonTerminal("whileStatement")
returnStatement = NonTerminal("returnStatement")
term = NonTerminal("term")
factor = NonTerminal("factor")
selector = NonTerminal("selector")
fieldList = NonTerminal("fieldList")
formalParameters = NonTerminal("formalParameters")

module.rule = Concat([MODULE, IDENT, SEMICOLON, declarations, BEGIN, statementSequence, END, IDENT, DOT])
identList.rule = Concat([IDENT, Star(Concat(COMMA, IDENT))])
statementSequence.rule = Star(Concat(statement, SEMICOLON))
type.rule = Or([IDENT, arrayType, recordType])
procedureDeclaration.rule = Concat([procedureHeading, SEMICOLON, subroutineBody])
functionDeclaration.rule = Concat(functionHeading, SEMICOLON, subroutineBody)
statement.rule = Or(assignment, call, ifStatement, whileStatement, returnStatement)
simpleExpression.rule = Concat([Or(PLUS, MINUS), term, Star(Concat(Or([PLUS, MINUS, OR]), term))])
