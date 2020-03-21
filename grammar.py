from grammar_nodes import *

IDENT = NamedTerminal("IDENT")
INTEGER = NamedTerminal("INTEGER")

MODULE = Literal("MODULE")
SEMICOLON = Literal(";")
BEGIN = Literal("BEGIN")
END = Literal("END")
DOT = Literal(".")
COMMA = Literal(",")
PLUS = Literal("+")
MINUS = Literal("-")
MULT = Literal("*")
OR = Literal("OR")
ARRAY = Literal("ARRAY")
OF = Literal("OF")
RECORD = Literal("RECORD")
PROCEDURE = Literal("PROCEDURE")
FUNCTION = Literal("FUNCTION")
COLON = Literal(":")
ASSIGN = Literal(":=")
IF = Literal("IF")
WHILE = Literal("WHILE")
THEN = Literal("THEN")
DO = Literal("DO")
ELSE = Literal("ELSE")
RETURN = Literal("RETURN")
DIV = Literal("DIV")
MOD = Literal("MOD")
AND = Literal("&")
OPEN_BRACKET = Literal("(")
CLOSE_BRACKET = Literal(")")
OPEN_SQUARE_BRACKET = Literal("[")
CLOSE_SQUARE_BRACKET = Literal("]")
NOT = Literal("~")
CONST = Literal("CONST")
VAR = Literal("VAR")
EQUALS = Literal("=")
TYPE = Literal("TYPE")
SHARP = Literal("#")
LESS = Literal("<")
LEQ = Literal("<=")
GREATER = Literal(">")
GEQ = Literal(">=")

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
actualParameters = NonTerminal("actualParameters")
constDeclarationBlock = NonTerminal("constDeclarationBlock")
typeDeclarationBlock = NonTerminal("typeDeclarationBlock")
varDeclarationBlock = NonTerminal("varDeclarationBlock")

module.rule = Concat([MODULE, IDENT, SEMICOLON, declarations, BEGIN, statementSequence, END, IDENT, DOT])
identList.rule = Concat([IDENT, Star(Concat([COMMA, IDENT]))])
statementSequence.rule = Star(Concat([statement, SEMICOLON]))
type.rule = Or([IDENT, arrayType, recordType])
procedureDeclaration.rule = Concat([procedureHeading, SEMICOLON, subroutineBody])
functionDeclaration.rule = Concat([functionHeading, SEMICOLON, subroutineBody])
statement.rule = Or([assignment, call, ifStatement, whileStatement, returnStatement])
simpleExpression.rule = Concat([Or([PLUS, MINUS]), term, Star(Concat([Or([PLUS, MINUS, OR]), term]))])
arrayType.rule = Concat([ARRAY, expression, OF, type])
recordType.rule = Concat([RECORD, Star(fieldList), END])
procedureHeading.rule = Concat([PROCEDURE, IDENT, formalParameters])
functionHeading.rule = Concat([FUNCTION, IDENT, formalParameters, COLON, type])
assignment.rule = Concat([IDENT, selector, ASSIGN, expression])
call.rule = Concat([IDENT, actualParameters])
ifStatement.rule = Concat([IF, expression, THEN, statementSequence, Question(Concat([ELSE, statementSequence])), END])
whileStatement.rule = Concat([WHILE, expression, DO, statementSequence, END])
returnStatement.rule = Concat([RETURN, Question(expression)])
term.rule = Concat([factor, Star(Concat([Or([MULT, DIV, MOD, AND]), factor]))])
factor.rule = Or(
    [Concat([IDENT, selector]),
     INTEGER,
     Concat([OPEN_BRACKET, expression, CLOSE_BRACKET]),
     Concat([NOT, factor])])
selector.rule = Star(Or([Concat([DOT, IDENT]), Concat([OPEN_BRACKET, expression, CLOSE_BRACKET])]))
fieldList.rule = Concat([identList, COLON, type])
declarations.rule = Concat(
    [Question(constDeclarationBlock),
     Question(typeDeclarationBlock),
     Question(varDeclarationBlock),
     Star(Concat([Or([procedureDeclaration, functionDeclaration]), SEMICOLON]))])
constDeclarationBlock.rule = Concat(
    [CONST, IDENT, EQUALS, expression, SEMICOLON, Star(Concat([IDENT, EQUALS, expression, SEMICOLON]))])
typeDeclarationBlock.rule = Concat(
    [TYPE, IDENT, EQUALS, type, SEMICOLON, Star(Concat([IDENT, EQUALS, type, SEMICOLON]))])
varDeclarationBlock.rule = Concat(
    [VAR, identList, COLON, type, SEMICOLON, Star(Concat([identList, COLON, type, SEMICOLON]))])
expression.rule = Concat(
    [simpleExpression, Question(Concat([Or([EQUALS, SHARP, LESS, LEQ, GREATER, GEQ]), simpleExpression]))])
subroutineBody.rule = Concat(
    [Question(Concat([VAR, identList, COLON, type, SEMICOLON, Star(Concat([identList, COLON, type, SEMICOLON]))])),
     BEGIN, statementSequence, END, IDENT])
formalParameters.rule = Concat([OPEN_BRACKET,
                                Question(Concat([VAR, identList, COLON, type, SEMICOLON,
                                                 Star(Concat([identList, COLON, type, SEMICOLON]))])),
                                CLOSE_BRACKET])
actualParameters.rule = Concat([OPEN_BRACKET,
                                Question(Concat([expression, Star(Concat([COMMA, expression]))])),
                                CLOSE_BRACKET])
