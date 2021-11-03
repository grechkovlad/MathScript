from enum import Enum


class Location:
    def __init__(self, line_start, column_start, line_end, column_end):
        self.line_start = line_start
        self.column_start = column_start
        self.line_end = line_end
        self.column_end = column_end

    def __eq__(self, other):
        if isinstance(other, Location):
            return self.line_start == other.line_start and \
                   self.column_start == other.column_start and \
                   self.line_end == other.line_end and \
                   self.column_end == other.column_end
        raise NotImplementedError()


class Node:
    def __init__(self, location: Location):
        self.location = location


class Identifier(Node):
    def __init__(self, name: str, location: Location):
        super(Identifier, self).__init__(location)
        self.name = name

    def __eq__(self, other):
        if isinstance(other, Identifier):
            return self.name == other.name and self.location == other.location
        raise NotImplementedError()


class Integer(Node):
    def __init__(self, val: int, location: Location):
        super(Integer, self).__init__(location)
        self.val = val

    def __eq__(self, other):
        if isinstance(other, Integer):
            return self.val == other.val and self.location == other.location
        raise NotImplementedError()


class ParametersList(Node):
    def __init__(self, parameters, location: Location):
        super(ParametersList, self).__init__(location)
        self.parameters = parameters

    def __eq__(self, other):
        if isinstance(other, ParametersList):
            return self.parameters == other.parameters and self.location == other.location
        raise NotImplementedError()


class ArgumentsList(Node):
    def __init__(self, arguments, location: Location):
        super(ArgumentsList, self).__init__(location)
        self.arguments = arguments

    def __eq__(self, other):
        if isinstance(other, ArgumentsList):
            return self.arguments == other.arguments and self.location == other.location
        raise NotImplementedError()


class Block(Node):
    def __init__(self, statements, location: Location):
        super(Block, self).__init__(location)
        self.statements = statements

    def __eq__(self, other):
        if isinstance(other, Block):
            return self.statements == other.statements and self.location == other.location
        raise NotImplementedError()


class Script:
    def __init__(self, statements):
        self.body = statements

    def __eq__(self, other):
        if isinstance(other, Script):
            return self.body == other.body
        raise NotImplementedError()


class SubroutineKind(Enum):
    FUNCTION = "function"
    PROCEDURE = "procedure"


class SubroutineDecl(Node):
    def __init__(self, kind: SubroutineKind, name: Identifier, parameters: ParametersList, body: Block,
                 location: Location):
        super(SubroutineDecl, self).__init__(location)
        self.kind = kind
        self.name = name
        self.parameters = parameters
        self.body = body

    def __eq__(self, other):
        if isinstance(other, SubroutineDecl):
            return self.kind == other.kind \
                   and self.name == other.name \
                   and self.parameters == other.parameters \
                   and self.body == other.body
        raise NotImplementedError()


class ReturnStatement(Node):
    def __init__(self, return_value, location: Location):
        super(ReturnStatement, self).__init__(location)
        self.return_value = return_value

    def __eq__(self, other):
        if isinstance(other, ReturnStatement):
            return self.return_value == other.return_value and self.location == other.location
        raise NotImplementedError()


class AssignStatement(Node):
    def __init__(self, var: Identifier, expr, location: Location):
        super(AssignStatement, self).__init__(location)
        self.var = var
        self.expr = expr

    def __eq__(self, other):
        if isinstance(other, AssignStatement):
            return self.var == other.var and self.expr == other.expr and self.location == other.location
        raise NotImplementedError()


class VariableDeclaration(Node):
    def __init__(self, var: Identifier, init_expr, location: Location):
        super(VariableDeclaration, self).__init__(location)
        self.var = var
        self.init_expr = init_expr

    def __eq__(self, other):
        if isinstance(other, VariableDeclaration):
            return self.var == other.var and self.init_expr == other.init_expr and self.location == other.location
        raise NotImplementedError()


class Call(Node):
    def __init__(self, subroutine: Identifier, arguments: ArgumentsList, location: Location):
        super(Call, self).__init__(location)
        self.function = subroutine
        self.arguments = arguments

    def __eq__(self, other):
        if isinstance(other, Call):
            return self.function == other.function and \
                   self.arguments == other.arguments and \
                   self.location == other.location
        raise NotImplementedError()


class CallStatement(Node):
    def __init__(self, call, location: Location):
        super(CallStatement, self).__init__(location)
        self.call = call

    def __eq__(self, other):
        if isinstance(other, CallStatement):
            return self.call == other.call and self.location == other.location
        raise NotImplementedError()


class IfStatement(Node):
    def __init__(self, condition, then_block: Block, else_block: Block, location: Location):
        super(IfStatement, self).__init__(location)
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

    def __eq__(self, other):
        if isinstance(other, IfStatement):
            return self.condition == other.condition \
                   and self.then_block == other.then_block \
                   and self.else_block == other.else_block \
                   and self.location == other.location
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


class BinaryOperation(Node):
    def __init__(self, kind: BinaryOperatorKind, left_operand, right_operand, location: Location):
        super(BinaryOperation, self).__init__(location)
        self.kind = kind
        self.left_operand = left_operand
        self.right_operand = right_operand

    def __eq__(self, other):
        if isinstance(other, BinaryOperation):
            return self.kind == other.kind \
                   and self.left_operand == other.left_operand \
                   and self.right_operand == other.right_operand \
                   and self.location == other.location
        raise NotImplementedError()


class UnaryOperation(Node):
    def __init__(self, kind: UnaryOperatorKind, operand, location: Location):
        super(UnaryOperation, self).__init__(location)
        self.kind = kind
        self.operand = operand

    def __eq__(self, other):
        if isinstance(other, UnaryOperation):
            return self.kind == other.kind and self.operand == other.operand and self.location == other.location
        raise NotImplementedError()
