from enum import Enum


class Script:
    def __init__(self, body):
        self.body = body

    def __eq__(self, other):
        if isinstance(other, Script):
            return self.body == other.body
        raise NotImplementedError()


class SubroutineDecl:
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body


class FunctionDecl(SubroutineDecl):
    def __init__(self, name, parameters, body):
        super(FunctionDecl, self).__init__(name, parameters, body)

    def __eq__(self, other):
        if isinstance(other, FunctionDecl):
            return self.name == other.name \
                   and self.parameters == self.parameters \
                   and self.body == other.body
        raise NotImplementedError()


class ProcedureDecl(SubroutineDecl):
    def __init__(self, name, parameters, body):
        super(ProcedureDecl, self).__init__(name, parameters, body)

    def __eq__(self, other):
        if isinstance(other, ProcedureDecl):
            return self.name == other.name \
                   and self.parameters == self.parameters \
                   and self.body == other.body
        raise NotImplementedError()


class ReturnStatement:
    def __init__(self, return_value=None):
        self.return_value = return_value

    def __eq__(self, other):
        if isinstance(other, ReturnStatement):
            return self.return_value == other.return_value
        raise NotImplementedError()


class AssignStatements:
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr

    def __eq__(self, other):
        if isinstance(other, AssignStatements):
            return self.var == other.var and self.expr == self.expr
        raise NotImplementedError()


class Call:
    def __init__(self, subroutine, arguments):
        self.function = subroutine
        self.arguments = arguments

    def __eq__(self, other):
        if isinstance(other, Call):
            return self.function == other.function and self.arguments == self.arguments
        raise NotImplementedError()


class CallStatement:
    def __init__(self, call):
        self.call = call

    def __eq__(self, other):
        if isinstance(other, CallStatement):
            return self.call == other.call
        raise NotImplementedError()


class IfStatement:
    def __init__(self, condition, then_block, else_block):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

    def __eq__(self, other):
        if isinstance(other, IfStatement):
            return self.condition == other.condition \
                   and self.then_block == self.then_block \
                   and self.else_block == other.else_block
        raise NotImplementedError()


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
        raise NotImplementedError()


class UnaryOperation:
    def __init__(self, kind: UnaryOperatorKind, operand):
        self.kind = kind
        self.operand = operand

    def __eq__(self, other):
        if isinstance(other, UnaryOperation):
            return self.kind == other.kind and self.operand == other.operand
        raise NotImplementedError()
