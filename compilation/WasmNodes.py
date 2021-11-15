from enum import Enum


class Module:
    def __init__(self, global_variables: list, functions: list, exports: list):
        self.globals = global_variables
        self.functions = functions
        self.exports = exports


class WasmType(Enum):
    I32 = "i32"


class I32Const:
    def __init__(self, val: int):
        self.val = val


class GlobalI32:
    def __init__(self, name: str, is_mutable: bool, init_val: I32Const):
        self.name = name
        self.is_mutable = is_mutable
        self.init_val = init_val


class Local:
    def __init__(self, name: str, var_type: WasmType):
        self.name = name
        self.type = var_type


class WasmBinaryOperationKind(Enum):
    I32_MUL = "i32.mul"
    I32_ADD = "i32.add"
    I32_SUB = "i32.sub"
    I32_GE_S = "i32.ge_s"
    I32_EQ = "i32.eq"
    I32_GT_S = "i32.gt_s"
    I32_LE_S = "i32.le_s"
    I32_LT_S = "i32.lt_s"
    I32_OR = "i32.or"
    I32_AND = "i32.and"


class Function:
    def __init__(self, name: str, parameters: list, is_void: bool, result_type: WasmType, local_vars: list,
                 instructions: list):
        if is_void and result_type is not None:
            raise ValueError(is_void, result_type)
        if not is_void and result_type is None:
            raise ValueError(is_void, result_type)
        self.name = name
        self.parameters = parameters
        self.is_void = is_void
        self.result_type = result_type
        self.locals = local_vars
        self.instructions = instructions


class Parameter:
    def __init__(self, name, var_type: WasmType):
        self.name = name
        self.type = var_type


class Export:
    def __init__(self, func_name: str, export_name: str):
        self.func_name = func_name
        self.export_name = export_name


class If:
    def __init__(self, condition, then_statements: list, else_statements: list):
        self.condition = condition
        self.then_instructions = then_statements
        self.else_instructions = else_statements


class WasmBinaryOperation:
    def __init__(self, left_operand, right_operand, kind: WasmBinaryOperationKind):
        self.left_operand = left_operand
        self.right_operand = right_operand
        self.kind = kind


class Call:
    def __init__(self, name: str, arguments: list):
        self.name = name
        self.arguments = arguments


class Return:
    def __init__(self, value):
        self.value = value


class SetLocal:
    def __init__(self, name, val):
        self.name = name
        self.val = val


class GetLocal:
    def __init__(self, name):
        self.name = name


class SetGlobal:
    def __init__(self, name, val):
        self.name = name
        self.val = val


class GetGlobal:
    def __init__(self, name):
        self.name = name
