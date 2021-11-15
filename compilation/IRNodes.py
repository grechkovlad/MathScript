from parsing.Ast import *


class IntegerIR:
    def __init__(self, val: int):
        self.val = val

    def __eq__(self, other):
        return _equals(self, other)


class LocalVariableDeclarationIR:
    def __init__(self, index: int, init_value):
        self.index = index
        self.init_value = init_value

    def __eq__(self, other):
        return _equals(self, other)


class ParameterDeclarationIR:
    def __init__(self, index: int):
        self.index = index

    def __eq__(self, other):
        return _equals(self, other)


class BinaryOperationIR:
    def __init__(self, left_op, right_op, kind: BinaryOperatorKind):
        self.left_op = left_op
        self.right_op = right_op
        self.kind = kind

    def __eq__(self, other):
        return _equals(self, other)


class UnaryOperationIR:
    def __init__(self, operand, kind: UnaryOperatorKind):
        self.operand = operand
        self.kind = kind

    def __eq__(self, other):
        return _equals(self, other)


class IfStatementIR:
    def __init__(self, condition, then_block, else_block):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

    def __eq__(self, other):
        return _equals(self, other)


class ReturnStatementIR:
    def __init__(self, return_value):
        self.return_value = return_value

    def __eq__(self, other):
        return _equals(self, other)


class VariableReferenceIR:
    def __init__(self, declaration):
        self.declaration = declaration

    def __eq__(self, other):
        return _equals(self, other)


class AssignStatementIR:
    def __init__(self, var: VariableReferenceIR, value):
        self.var = var
        self.value = value

    def __eq__(self, other):
        return _equals(self, other)


class GlobalVariableDeclarationIR:
    def __init__(self, index: int, init_value):
        self.index = index
        self.init_value = init_value

    def __eq__(self, other):
        return _equals(self, other)


class SubroutineDeclarationIR:
    def __init__(self, subroutine_kind: SubroutineKind,
                 parameters: list, statements: list,
                 index: int,
                 local_variables_count: int):
        self.subroutine_kind = subroutine_kind
        self.parameters = parameters
        self.statements = statements
        self.index = index
        self.local_variables_count = local_variables_count

    def __eq__(self, other):
        return _equals(self, other)


class SubroutineReferenceIR:
    def __init__(self, declaration: SubroutineDeclarationIR):
        self.declaration = declaration

    def __eq__(self, other):
        return _equals(self, other)


class CallIR:
    def __init__(self, subroutine: SubroutineReferenceIR, arguments: list):
        self.subroutine = subroutine
        self.args = arguments

    def __eq__(self, other):
        return _equals(self, other)


class CallStatementIR:
    def __init__(self, call: CallIR):
        self.call = call

    def __eq__(self, other):
        return _equals(self, other)


class ScriptIR:
    def __init__(self, subroutines: list, statements: list, global_variables_count: int):
        self.subroutines = subroutines
        self.statements = statements
        self.global_variables_count = global_variables_count

    def __eq__(self, other):
        return _equals(self, other)


class _NodeRef:
    def __init__(self, node):
        self.node = node

    def __eq__(self, other):
        if isinstance(other, _NodeRef):
            return self.node is other.node

    def __hash__(self):
        return id(self.node)


def _nodes_lists_equals(list_one: list, list_two: list, visited):
    if list_one is list_two:
        return True
    if list_one is None or list_two is None:
        return False
    if len(list_one) != len(list_two):
        return False
    for (node, other) in zip(list_one, list_two):
        if not _equality_traverse(node, other, visited):
            return False
    return True


def _equality_traverse(node, other, visited):
    if node is other:
        return True
    if node is None or other is None:
        return False
    node_ref = _NodeRef(node)
    if node_ref in visited:
        return other is visited[node_ref]
    visited[node_ref] = other
    if type(node) != type(other):
        return False
    if isinstance(node, IntegerIR):
        return node.val == other.val
    if isinstance(node, LocalVariableDeclarationIR):
        return node.index == other.index and _equality_traverse(node.init_value, other.init_value, visited)
    if isinstance(node, ParameterDeclarationIR):
        return node.index == other.index
    if isinstance(node, BinaryOperationIR):
        return node.kind == other.kind and _equality_traverse(node.left_op, other.left_op,
                                                              visited) and _equality_traverse(node.right_op,
                                                                                              other.right_op, visited)
    if isinstance(node, UnaryOperationIR):
        return node.kind == other.kind and _equality_traverse(node.operand, other.operand, visited)
    if isinstance(node, IfStatementIR):
        return _equality_traverse(node.condition, other.condition, visited) and \
               _nodes_lists_equals(node.then_block, other.then_block, visited) and \
               _nodes_lists_equals(node.else_block, other.else_block, visited)
    if isinstance(node, ReturnStatementIR):
        return _equality_traverse(node.return_value, other.return_value, visited)
    if isinstance(node, AssignStatementIR):
        return _equality_traverse(node.var, other.var, visited) and _equality_traverse(node.value, other.value, visited)
    if isinstance(node, GlobalVariableDeclarationIR):
        return node.index == other.index and _equality_traverse(node.init_value, other.init_value, visited)
    if isinstance(node, VariableReferenceIR):
        return _equality_traverse(node.declaration, other.declaration, visited)
    if isinstance(node, SubroutineDeclarationIR):
        return node.index == other.index and \
               node.local_variables_count == other.local_variables_count and \
               node.subroutine_kind == other.subroutine_kind and \
               _nodes_lists_equals(node.statements, other.statements, visited) and \
               _nodes_lists_equals(node.parameters, other.parameters, visited)
    if isinstance(node, SubroutineReferenceIR):
        return _equality_traverse(node.declaration, other.declaration, visited)
    if isinstance(node, CallIR):
        return _equality_traverse(node.subroutine, other.subroutine, visited) and \
               _nodes_lists_equals(node.args, other.args, visited)
    if isinstance(node, CallStatementIR):
        return _equality_traverse(node.call, other.call, visited)
    if isinstance(node, ScriptIR):
        return node.global_variables_count == other.global_variables_count and \
               _nodes_lists_equals(node.subroutines, other.subroutines, visited) and \
               _nodes_lists_equals(node.statements, other.statements, visited)
    raise ValueError(node)


def _equals(node, other):
    visited = dict()
    return _equality_traverse(node, other, visited)
