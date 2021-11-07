from compilation.IRNodes import *


class SubroutineContext:
    def __init__(self, subroutine_kind: SubroutineKind):
        self.subroutine_kind = subroutine_kind
        self.variables = dict()

    def __eq__(self, other):
        if isinstance(other, SubroutineContext):
            return self.subroutine_kind == other.subroutine_kind and self.variables == other.variables


class ScriptContext:
    def __init__(self):
        self.subroutines = dict()
        self.variables = dict()

    def __eq__(self, other):
        if isinstance(other, ScriptContext):
            return self.subroutines == other.subroutines and self.variables == other.variables
        raise NotImplementedError()


class Type(Enum):
    INT = "int"
    BOOL = "bool"
    VOID = "void"


def _end_location(location: Location):
    return Location(location.line_end, location.column_end, location.line_end, location.column_end)


class CompilationException(Exception):
    def __init__(self, message: str, location: Location):
        super(CompilationException, self).__init__(message)
        self.location = location


class DuplicateDeclaration(CompilationException):
    def __init__(self, name: str, location: Location):
        super(DuplicateDeclaration, self).__init__("'%s' is already defined in this scope" % name, location)
        self.name = name

    def __eq__(self, other):
        if isinstance(other, DuplicateDeclaration):
            return self.name == other.name and self.location == other.location


class DeclarationNotFound(CompilationException):
    def __init__(self, name: str, location: Location):
        super(DeclarationNotFound, self).__init__("declaration of '%s' not found" % name, location)
        self.name = name

    def __eq__(self, other):
        if isinstance(other, DeclarationNotFound):
            return self.name == other.name and self.location == other.location


class TypeMismatch(CompilationException):
    def __init__(self, expected: Type, actual: Type, location: Location):
        super(TypeMismatch, self).__init__("Type mismatch: expected '%s', but got '%s'" % (expected, actual), location)
        self.expected = expected
        self.actual = actual

    def __eq__(self, other):
        if isinstance(other, TypeMismatch):
            return self.expected == other.expected and self.actual == other.actual and self.location == other.location


class ArgumentsNumberMismatch(CompilationException):
    def __init__(self, expected: int, actual: int, location: Location):
        super(ArgumentsNumberMismatch, self).__init__(
            "Arguments number mismatch: expected %d, but got %d" % (expected, actual), location)
        self.expected = expected
        self.actual = actual

    def __eq__(self, other):
        if isinstance(other, ArgumentsNumberMismatch):
            return self.expected == other.expected and self.actual == other.actual and self.location == other.location


class IllegalEmptyReturn(CompilationException):
    def __init__(self, location: Location):
        super(IllegalEmptyReturn, self).__init__("Empty return outside procedure context", location)

    def __eq__(self, other):
        if isinstance(other, IllegalEmptyReturn):
            return self.location == other.location


class IllegalValueReturn(CompilationException):
    def __init__(self, location: Location):
        super(IllegalValueReturn, self).__init__("Value return in procedure context", location)

    def __eq__(self, other):
        if isinstance(other, IllegalValueReturn):
            return self.location == other.location


class MissingReturnStatement(CompilationException):
    def __init__(self, location: Location):
        super(MissingReturnStatement, self).__init__("Missing return statement", location)

    def __eq__(self, other):
        if isinstance(other, MissingReturnStatement):
            return self.location == other.location


class ResultOfFunctionCallIgnored(CompilationException):
    def __init__(self, location: Location):
        super(ResultOfFunctionCallIgnored, self).__init__("Result of function call ignored", location)

    def __eq__(self, other):
        if isinstance(other, ResultOfFunctionCallIgnored):
            return self.location == other.location


def compile_parameters(param_list: ParametersList, script_context: ScriptContext,
                       subroutine_context: SubroutineContext):
    res = []
    for index, parameter in enumerate(param_list.parameters):
        if parameter.name in dict(script_context.variables, **subroutine_context.variables):
            raise DuplicateDeclaration(parameter.name, parameter.location)
        param_ir = ParameterDeclarationIR(index)
        res.append(param_ir)
        subroutine_context.variables[parameter.name] = param_ir
    return res


def _always_returns(statements):
    for statement in statements:
        if isinstance(statement, ReturnStatementIR):
            return True
        if isinstance(statement, IfStatementIR):
            if statement.else_block is not None and _always_returns(statement.then_block) and _always_returns(
                    statement.else_block):
                return True
    return False


def compile_subroutine_declaration(subroutine: SubroutineDecl, script_context: ScriptContext):
    if subroutine.name.name in script_context.subroutines:
        raise DuplicateDeclaration(subroutine.name.name, subroutine.name.location)
    subroutine_decl = SubroutineDeclarationIR(subroutine.kind, [], [])
    script_context.subroutines[subroutine.name.name] = subroutine_decl
    subroutine_context = SubroutineContext(subroutine.kind)
    parameters = compile_parameters(subroutine.parameters, script_context, subroutine_context)
    subroutine_decl.parameters = parameters
    body = []
    for statement in subroutine.body.statements:
        body.append(compile_statement(statement, script_context, subroutine_context))
    if subroutine.kind == SubroutineKind.FUNCTION and not _always_returns(body):
        raise MissingReturnStatement(_end_location(subroutine.body.location))
    subroutine_decl.body = body
    return subroutine_decl


def compile_call_statement(call_statement: CallStatement, script_context: ScriptContext,
                           subroutine_context: SubroutineContext):
    if call_statement.call.subroutine.name not in script_context.subroutines:
        raise DeclarationNotFound(call_statement.call.subroutine.name, call_statement.call.subroutine.location)
    if script_context.subroutines[call_statement.call.subroutine.name].subroutine_kind == SubroutineKind.FUNCTION:
        raise ResultOfFunctionCallIgnored(call_statement.location)
    call, _ = compile_call(call_statement.call, script_context, subroutine_context)
    return CallStatementIR(call)


def compile_subroutine_reference(subroutine: Identifier, script_context: ScriptContext,
                                 subroutine_context: SubroutineContext):
    if subroutine.name in script_context.subroutines:
        subroutine_declaration = script_context.subroutines[subroutine.name]
        return SubroutineReferenceIR(subroutine_declaration)
    raise DeclarationNotFound(subroutine.name, subroutine.location)


def compile_call(call: Call, script_context: ScriptContext, subroutine_context: SubroutineContext):
    subroutine_reference = compile_subroutine_reference(call.subroutine, script_context, subroutine_context)
    subroutine_declaration = subroutine_reference.declaration
    if len(call.arguments.arguments) != len(subroutine_declaration.parameters):
        raise ArgumentsNumberMismatch(len(subroutine_declaration.parameters),
                                      len(call.arguments.arguments),
                                      call.arguments.location)
    args_ir = []
    for arg in call.arguments.arguments:
        arg_ir, arg_type = compile_expr(arg, script_context, subroutine_context)
        if arg_type != Type.INT:
            raise TypeMismatch(Type.INT, arg_type, arg.location)
        args_ir.append(arg_ir)
    return CallIR(subroutine_reference,
                  args_ir), Type.INT if subroutine_declaration.subroutine_kind == SubroutineKind.FUNCTION else Type.VOID


def compile_variable_reference(identifier: Identifier, script_context: ScriptContext,
                               subroutine_context: SubroutineContext):
    all_variables = script_context.variables if subroutine_context is None else dict(script_context.variables,
                                                                                     **subroutine_context.variables)
    if identifier.name in all_variables:
        return VariableReferenceIR(all_variables[identifier.name])
    raise DeclarationNotFound(identifier.name, identifier.location)


def _has_numeric_operands(kind: BinaryOperatorKind):
    return kind in [BinaryOperatorKind.MUL, BinaryOperatorKind.PLUS, BinaryOperatorKind.MINUS,
                    BinaryOperatorKind.EQ, BinaryOperatorKind.GEQ, BinaryOperatorKind.GREATER,
                    BinaryOperatorKind.LESS, BinaryOperatorKind.LEQ]


def _has_numeric_result(kind: BinaryOperatorKind):
    return kind in [BinaryOperatorKind.MUL, BinaryOperatorKind.PLUS, BinaryOperatorKind.MINUS]


def _safe_compile_operand(binary_operation: BinaryOperation, target_type: Type, script_context: ScriptContext,
                          subroutine_context: SubroutineContext):
    left_op, left_op_type = compile_expr(binary_operation.left_operand, script_context, subroutine_context)
    if left_op_type != target_type:
        raise TypeMismatch(target_type, left_op_type, binary_operation.left_operand.location)
    right_op, right_op_type = compile_expr(binary_operation.right_operand, script_context, subroutine_context)
    if right_op_type != target_type:
        raise TypeMismatch(target_type, right_op_type, binary_operation.right_operand.location)
    return left_op, right_op


def compile_binary_operation(binary_operation: BinaryOperation, script_context: ScriptContext,
                             subroutine_context: SubroutineContext):
    if _has_numeric_operands(binary_operation.kind):
        left_op, right_op = _safe_compile_operand(binary_operation, Type.INT, script_context, subroutine_context)
        return BinaryOperationIR(left_op, right_op, binary_operation.kind), Type.INT if _has_numeric_result(
            binary_operation.kind) else Type.BOOL
    left_op, right_op = _safe_compile_operand(binary_operation, Type.BOOL, script_context, subroutine_context)
    return BinaryOperationIR(left_op, right_op, binary_operation.kind), Type.BOOL


def compile_unary_operation(unary_operation: UnaryOperation, script_context: ScriptContext,
                            subroutine_context: SubroutineContext):
    operand, operand_type = compile_expr(unary_operation.operand, script_context, subroutine_context)
    if unary_operation.kind == UnaryOperatorKind.MINUS:
        if operand_type != Type.INT:
            raise TypeMismatch(Type.INT, operand_type, unary_operation.operand.location)
        return UnaryOperationIR(operand, unary_operation.kind), Type.INT
    else:
        if operand_type != Type.BOOL:
            raise TypeMismatch(Type.BOOL, operand_type, unary_operation.operand.location)
        return UnaryOperationIR(operand, unary_operation.kind), Type.BOOL


def compile_expr(expr, script_context: ScriptContext, subroutine_context: SubroutineContext = None):
    match expr:
        case BinaryOperation():
            return compile_binary_operation(expr, script_context, subroutine_context)
        case UnaryOperation():
            return compile_unary_operation(expr, script_context, subroutine_context)
        case Call():
            return compile_call(expr, script_context, subroutine_context)
        case Identifier():
            return compile_variable_reference(expr, script_context, subroutine_context), Type.INT
        case Integer():
            return IntegerIR(expr.val), Type.INT


def compile_if(if_statement: IfStatement, script_context: ScriptContext, subroutine_context: SubroutineContext):
    cond, cond_type = compile_expr(if_statement.condition, script_context, subroutine_context)
    if cond_type != Type.BOOL:
        raise TypeMismatch(Type.BOOL, cond_type, if_statement.condition.location)
    then_block = [compile_statement(statement, script_context, subroutine_context) for statement in
                  if_statement.then_block.statements]
    else_block = None
    if if_statement.else_block is not None:
        else_block = [compile_statement(statement, script_context, subroutine_context) for statement in
                      if_statement.else_block.statements]
    return IfStatementIR(cond, then_block, else_block)


def compile_return(return_statement: ReturnStatement, script_context: ScriptContext,
                   subroutine_context: SubroutineContext):
    if return_statement.return_value is None:
        if subroutine_context is None or subroutine_context.subroutine_kind != SubroutineKind.PROCEDURE:
            raise IllegalEmptyReturn(return_statement.location)
        return ReturnStatementIR(return_value=None)
    if subroutine_context is not None and subroutine_context.subroutine_kind == SubroutineKind.PROCEDURE:
        raise IllegalValueReturn(return_statement.return_value.location)
    return_value, return_value_type = compile_expr(return_statement.return_value, script_context, subroutine_context)
    if return_value_type != Type.INT:
        raise TypeMismatch(Type.INT, return_value_type, return_statement.return_value.location)
    return ReturnStatementIR(return_value)


def compile_assign(assign_statement: AssignStatement, script_context: ScriptContext,
                   subroutine_context: SubroutineContext):
    assignee = compile_variable_reference(assign_statement.var, script_context, subroutine_context)
    r_value, r_value_type = compile_expr(assign_statement.expr, script_context, subroutine_context)
    if r_value_type != Type.INT:
        raise TypeMismatch(Type.INT, r_value_type, assign_statement.expr.location)
    return AssignStatementIR(assignee, r_value)


def compile_variable_decl(var_declaration: VariableDeclaration, script_context: ScriptContext,
                          subroutine_context: SubroutineContext):
    var_name = var_declaration.var.name
    if subroutine_context is None:
        if var_name in script_context.variables:
            raise DuplicateDeclaration(var_name, var_declaration.var.location)
        init_value, init_value_type = compile_expr(var_declaration.init_expr, script_context)
        if init_value_type != Type.INT:
            raise TypeMismatch(Type.INT, init_value_type, var_declaration.init_expr.location)
        global_var_decl = GlobalVariableDeclarationIR(len(script_context.variables), init_value)
        script_context.variables[var_name] = global_var_decl
        return global_var_decl
    else:
        if var_name in dict(script_context.variables, **subroutine_context.variables):
            raise DuplicateDeclaration(var_name, var_declaration.var.location)
        init_value, init_value_type = compile_expr(var_declaration.init_expr, script_context)
        if init_value_type != Type.INT:
            raise TypeMismatch(Type.INT, init_value_type, var_declaration.init_expr.location)
        local_var_decl = LocalVariableDeclarationIR(len(subroutine_context.variables), init_value)
        subroutine_context.variables[var_name] = local_var_decl
        return local_var_decl


def compile_statement(statement, script_context: ScriptContext, subroutine_context: SubroutineContext = None):
    match statement:
        case IfStatement():
            return compile_if(statement, script_context, subroutine_context)
        case ReturnStatement():
            return compile_return(statement, script_context, subroutine_context)
        case AssignStatement():
            return compile_assign(statement, script_context, subroutine_context)
        case VariableDeclaration():
            return compile_variable_decl(statement, script_context, subroutine_context)
        case CallStatement():
            return compile_call_statement(statement, script_context, subroutine_context)


def compile_script(script: Script):
    subroutines = []
    statements = []
    script_context = ScriptContext()
    for script_elem in script.body:
        if isinstance(script_elem, SubroutineDecl):
            subroutines.append(compile_subroutine_declaration(script_elem, script_context))
        else:
            statements.append(compile_statement(script_elem, script_context))
    if not _always_returns(statements):
        raise MissingReturnStatement(_end_location(script.end_location))
    return ScriptIR(subroutines, statements)
