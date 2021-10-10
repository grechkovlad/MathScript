from enum import Enum


class Script:
    def __init__(self, body):
        self.body = body


class SubroutineDecl:
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body


class FunctionDecl(SubroutineDecl):
    def __init__(self, name, parameters, body):
        super(FunctionDecl, self).__init__(name, parameters, body)


class ProcedureDecl(SubroutineDecl):
    def __init__(self, name, parameters, body):
        super(ProcedureDecl, self).__init__(name, parameters, body)


class ReturnStatement:
    def __init__(self, return_value=None):
        self.return_value = return_value


class AssignStatements:
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr


class CallStatement:
    def __init__(self, function, arguments):
        self.function = function
        self.arguments = arguments


class IfStatement:
    def __init__(self, condition, then_block, else_block):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block


class BinaryOperatorKind(Enum):
    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    EQ = "=="
    LESS = "<"
    LEQ = "<="
    GREATER = ">"
    GEQ = ">="
    AND = "&"
    OR = "|"


class UnaryOperatorKind(Enum):
    MINUS = "-"
    NOT = "!"


class BinaryOperation:
    def __init__(self, kind: BinaryOperatorKind, left_operand, right_operand):
        self.kind = kind
        self.left_operand = left_operand
        self.right_operand = right_operand

    def __eq__(self, other):
        if isinstance(other, BinaryOperation):
            return self.kind == other.kind \
                   and self.left_operand == other.left_operand \
                   and self.right_operand == other.right_operand


class UnaryOperation:
    def __init__(self, kind: UnaryOperatorKind, operand):
        self.kind = kind
        self.operand = operand

    def __eq__(self, other):
        if isinstance(other, UnaryOperation):
            return self.kind == other.kind and self.operand == other.operand
