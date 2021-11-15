import compilation.WasmNodes
from compilation.IRNodes import *
from compilation.WasmNodes import *


def compile_global_variables_declaration(global_variables_count: int):
    return [GlobalI32(_get_global_var_name(index), is_mutable=True, init_val=I32Const(0)) for index in
            range(global_variables_count)]


def _get_global_var_name(index: int):
    return "global_%d" % index


def _get_param_var_name(index: int):
    return "param_%d" % index


def _get_local_var_name(index: int):
    return "local_%d" % index


def _get_func_name(index: int):
    return "func_%d" % index


def compile_script_statements(statements: list):
    return Function("main", [], False, WasmType.I32, [],
                    compile_statements(statements) + [_create_explicit_stub_return()])


def compile_parameters(parameters: list):
    return [Parameter(_get_param_var_name(index), WasmType.I32) for index in range(len(parameters))]


def _create_explicit_stub_return():
    return Return(I32Const(0))


def compile_if_statement(statement: IfStatementIR):
    return If(compile_expr(statement.condition), compile_statements(statement.then_block),
              [] if statement.else_block is None else compile_statements(statement.else_block))


def _get_wasm_variable_name(variable_decl):
    match variable_decl:
        case GlobalVariableDeclarationIR():
            return _get_global_var_name(variable_decl.index)
        case LocalVariableDeclarationIR():
            return _get_local_var_name(variable_decl.index)
        case ParameterDeclarationIR():
            return _get_param_var_name(variable_decl.index)
        case _:
            raise ValueError(variable_decl)


def compile_variable_assign(var, value):
    compiled_value = compile_expr(value)
    match var:
        case GlobalVariableDeclarationIR():
            return SetGlobal(_get_global_var_name(var.index), compiled_value)
        case ParameterDeclarationIR():
            return SetLocal(_get_param_var_name(var.index), compiled_value)
        case LocalVariableDeclarationIR():
            return SetLocal(_get_local_var_name(var.index), compiled_value)


def compile_assign_statement(statement: AssignStatementIR):
    return compile_variable_assign(statement.var.declaration, statement.value)


def compile_integer(expr: IntegerIR):
    return I32Const(expr.val)


def _to_wasm_binary_operator(kind: BinaryOperatorKind):
    match kind:
        case BinaryOperatorKind.MUL:
            return WasmBinaryOperationKind.I32_MUL
        case BinaryOperatorKind.PLUS:
            return WasmBinaryOperationKind.I32_ADD
        case BinaryOperatorKind.MINUS:
            return WasmBinaryOperationKind.I32_SUB
        case BinaryOperatorKind.GEQ:
            return WasmBinaryOperationKind.I32_GE_S
        case BinaryOperatorKind.EQ:
            return WasmBinaryOperationKind.I32_EQ
        case BinaryOperatorKind.GREATER:
            return WasmBinaryOperationKind.I32_GT_S
        case BinaryOperatorKind.LEQ:
            return WasmBinaryOperationKind.I32_LE_S
        case BinaryOperatorKind.LESS:
            return WasmBinaryOperationKind.I32_LT_S
        case BinaryOperatorKind.OR:
            return WasmBinaryOperationKind.I32_OR
        case BinaryOperatorKind.AND:
            return WasmBinaryOperationKind.I32_AND


def compile_binary_operation(expr: BinaryOperationIR):
    return WasmBinaryOperation(compile_expr(expr.left_op), compile_expr(expr.right_op),
                               _to_wasm_binary_operator(expr.kind))


def compile_unary_operation(expr: UnaryOperationIR):
    operand = compile_expr(expr.operand)
    match expr.kind:
        case UnaryOperatorKind.MINUS:
            return WasmBinaryOperation(I32Const(0), operand, WasmBinaryOperationKind.I32_SUB)
        case UnaryOperatorKind.NOT:
            return WasmBinaryOperation(I32Const(0), operand, WasmBinaryOperationKind.I32_EQ)
        case _:
            raise ValueError(expr)


def compile_call(expr: CallIR):
    return compilation.WasmNodes.Call(_get_func_name(expr.subroutine.declaration.index),
                                      [compile_expr(arg) for arg in expr.args])


def compile_variable_read(variable_decl):
    match variable_decl:
        case GlobalVariableDeclarationIR():
            return GetGlobal(_get_global_var_name(variable_decl.index))
        case LocalVariableDeclarationIR():
            return GetLocal(_get_local_var_name(variable_decl.index))
        case ParameterDeclarationIR():
            return GetLocal(_get_param_var_name(variable_decl.index))
        case _:
            raise ValueError(variable_decl)


def compile_expr(expr):
    match expr:
        case IntegerIR():
            return compile_integer(expr)
        case BinaryOperationIR():
            return compile_binary_operation(expr)
        case UnaryOperationIR():
            return compile_unary_operation(expr)
        case CallIR():
            return compile_call(expr)
        case VariableReferenceIR():
            return compile_variable_read(expr.declaration)
        case _:
            raise ValueError(expr)


def compile_return_statement(statement: ReturnStatementIR):
    if statement.return_value is None:
        return Return(None)
    return Return(compile_expr(statement.return_value))


def compile_call_statement(statement: CallStatementIR):
    return compile_call(statement.call)


def compile_global_var_init(statement: GlobalVariableDeclarationIR):
    return compile_variable_assign(statement, statement.init_value)


def compile_local_var_init(statement: LocalVariableDeclarationIR):
    return compile_variable_assign(statement, statement.init_value)


def compile_statement(statement):
    match statement:
        case IfStatementIR():
            return compile_if_statement(statement)
        case AssignStatementIR():
            return compile_assign_statement(statement)
        case ReturnStatementIR():
            return compile_return_statement(statement)
        case CallStatementIR():
            return compile_call_statement(statement)
        case GlobalVariableDeclarationIR():
            return compile_global_var_init(statement)
        case LocalVariableDeclarationIR():
            return compile_local_var_init(statement)
        case _:
            raise ValueError(statement)


def compile_statements(statements: list):
    return [compile_statement(statement) for statement in statements]


def compile_local_variables_declaration(local_variables_count):
    return [Local(_get_local_var_name(index), WasmType.I32) for index in range(local_variables_count)]


def compile_subroutine(subroutine: SubroutineDeclarationIR):
    if subroutine.subroutine_kind == SubroutineKind.FUNCTION:
        is_void = False
        return_type = WasmType.I32
    else:
        is_void = True
        return_type = None
    return Function(_get_func_name(subroutine.index), compile_parameters(subroutine.parameters),
                    is_void, return_type,
                    compile_local_variables_declaration(subroutine.local_variables_count),
                    compile_statements(subroutine.statements) + [_create_explicit_stub_return()])


def compile_subroutines(subroutines: list):
    return [compile_subroutine(subroutine) for subroutine in subroutines]


def _create_main_export():
    return Export("main", "main")


def compile_script(script: ScriptIR):
    return Module(compile_global_variables_declaration(script.global_variables_count),
                  compile_subroutines(script.subroutines) + [compile_script_statements(script.statements)],
                  [_create_main_export()])


def stringify_type(wasm_type: WasmType):
    return wasm_type.value


def stringify_i32_const(i32_const: I32Const):
    return "%s.const %d" % (WasmType.I32.value, i32_const.val)


def stringify_global(global_var: GlobalI32):
    type_str = "(mut %s)" % WasmType.I32.value if global_var.is_mutable else WasmType.I32.value
    return "(global $%s %s (%s))" % (global_var.name, type_str, stringify_i32_const(global_var.init_val))


def stringify_local(local_var: Local):
    return "(local $%s %s)" % (local_var.name, local_var.type.value)


def stringify_export(export: Export):
    return "(export \"%s\" (func $%s))" % (export.export_name, export.func_name)


def stringify_parameter(parameter: Parameter):
    return "(param $%s %s)" % (parameter.name, parameter.type.value)


def stringify_parameters(parameters: list[Parameter]):
    return " ".join([stringify_parameter(parameter) for parameter in parameters])


def stringify_function_header(function: Function):
    result_str = "" if function.is_void else "(result %s)" % function.result_type.value
    return "func $%s %s %s" % (function.name, stringify_parameters(function.parameters), result_str)


def stringify_if(instruction: If):
    cond_instructions = stringify_instruction(instruction.condition)
    then_instructions = stringify_instructions(instruction.then_instructions)
    if instruction.else_instructions is None:
        return cond_instructions + ["if"] + then_instructions + ["end"]
    else_instructions = stringify_instructions(instruction.else_instructions)
    return cond_instructions + ["if"] + then_instructions + ["else"] + else_instructions + ["end"]


def stringify_binary_operation(instruction: WasmBinaryOperation):
    left_op_instructions = stringify_instruction(instruction.left_operand)
    right_op_instructions = stringify_instruction(instruction.right_operand)
    return left_op_instructions + right_op_instructions + [instruction.kind.value]


def stringify_call(instruction: Call):
    arg_instructions = []
    for arg in instruction.arguments:
        arg_instructions += stringify_instruction(arg)
    return arg_instructions + ["call $%s" % instruction.name]


def stringify_return(instruction: Return):
    return stringify_instruction(instruction.value) + ["return"]


def stringify_set_local(instruction: SetLocal):
    return stringify_instruction(instruction.val) + ["set_local $%s" % instruction.name]


def stringify_get_local(instruction: GetLocal):
    return ["get_local $%s" % instruction.name]


def stringify_set_global(instruction: SetGlobal):
    return stringify_instruction(instruction.val) + ["set_global $%s" % instruction.name]


def stringify_get_global(instruction: GetLocal):
    return ["get_global $%s" % instruction.name]


def stringify_instructions(instructions: list):
    res = []
    for instruction in instructions:
        res += stringify_instruction(instruction)
    return res


def stringify_instruction(instruction):
    match instruction:
        case I32Const():
            return [stringify_i32_const(instruction)]
        case If():
            return stringify_if(instruction)
        case WasmBinaryOperation():
            return stringify_binary_operation(instruction)
        case Call():
            return stringify_call(instruction)
        case Return():
            return stringify_return(instruction)
        case SetLocal():
            return stringify_set_local(instruction)
        case GetLocal():
            return stringify_get_local(instruction)
        case SetGlobal():
            return stringify_set_global(instruction)
        case GetGlobal():
            return stringify_get_global(instruction)


def stringify_function(function: Function):
    lines = ["(" + stringify_function_header(function)]
    for local in function.locals:
        lines.append("\t" + stringify_local(local))
    for instruction in function.instructions:
        for inst_line in stringify_instruction(instruction):
            lines.append("\t" + inst_line)
    lines.append(")")
    return lines


def emit_module_code(module: Module):
    lines = ["(module"]
    for global_var in module.globals:
        lines.append("\t" + stringify_global(global_var))
    for function in module.functions:
        for func_line in stringify_function(function):
            lines.append("\t" + func_line)
    for export in module.exports:
        lines.append("\t" + stringify_export(export))
    lines.append(")")
    return "\n".join(lines)
