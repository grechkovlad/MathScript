from compilation.IRNodes import *

from backend.jvm.bytecodewriter.bytecompiler import ClassFile, CodeAttribute
from backend.jvm.bytecodewriter.byteassembler import assemble

import itertools


def _to_jvm__jump_binary_operator(kind: BinaryOperatorKind):
    match kind:
        case BinaryOperatorKind.GEQ:
            return "if_icmpge"
        case BinaryOperatorKind.EQ:
            return "if_icmpeq"
        case BinaryOperatorKind.GREATER:
            return "if_icmpgt"
        case BinaryOperatorKind.LEQ:
            return "if_icmple"
        case BinaryOperatorKind.LESS:
            return "if_icmplt"


def _create_method_descriptor(subroutine: SubroutineDeclarationIR):
    return "(%s)%s" % ("".join(["I" for _ in range(len(subroutine.parameters))]),
                       "I" if subroutine.subroutine_kind == SubroutineKind.FUNCTION else "V")


def get_field_name(index):
    return "f%s" % index


def _get_method_name(index):
    return "m%s" % index


class Compiler:
    def __init__(self, class_name):
        self._label_counter = 0
        self._class_name = class_name
        self._clazz = ClassFile(class_name)
        self._subroutine_parameters_count = 0

    def gen_label(self):
        self._label_counter += 1
        return "l%d" % self._label_counter

    def compile(self, script: ScriptIR):
        self._compile_global_variables(script.global_variables_count)
        self._compile_subroutines(script.subroutines)
        self._compile_script_statements(script.statements)

        return self._clazz

    def _compile_global_variables(self, global_variables_count):
        for var_index in range(global_variables_count):
            self._clazz.field(get_field_name(var_index), "I", ["private", "static"])

    def _compile_integer(self, expr: IntegerIR):
        match expr.val:
            case -1:
                return ["iconst_m1"]
            case 0:
                return ["iconst_0"]
            case 1:
                return ["iconst_1"]
            case 2:
                return ["iconst_2"]
            case 3:
                return ["iconst_3"]
            case 4:
                return ["iconst_4"]
            case 5:
                return ["iconst_5"]
            case _:
                const_index = self._clazz.addpool("int", expr.val)
                return ["ldc %d" % const_index]

    def _compile_unary_operator(self, kind):
        if kind == UnaryOperatorKind.MINUS:
            return ["ineg"]
        l1 = self.gen_label()
        l2 = self.gen_label()
        return ["ifeq %s" % l1,
                "iconst_0",
                "goto %s" % l2,
                "%s:" % l1,
                "iconst_1",
                "%s:" % l2]

    def _compile_binary_operator(self, kind: BinaryOperatorKind):
        match kind:
            case BinaryOperatorKind.MUL:
                return ["imul"]
            case BinaryOperatorKind.PLUS:
                return ["iadd"]
            case BinaryOperatorKind.MINUS:
                return ["isub"]
            case BinaryOperatorKind.OR:
                return ["ior"]
            case BinaryOperatorKind.AND:
                return ["iand"]
            case _:
                l1 = self.gen_label()
                l2 = self.gen_label()
                return ["%s %s" % (_to_jvm__jump_binary_operator(kind), l1),
                        "iconst_0",
                        "goto %s" % l2,
                        "%s:" % l1,
                        "iconst_1",
                        "%s:" % l2]

    def _compile_expr(self, expr):
        match expr:
            case IntegerIR():
                return self._compile_integer(expr)
            case BinaryOperationIR():
                return self._compile_binary_operation(expr)
            case UnaryOperationIR():
                return self._compile_unary_operation(expr)
            case CallIR():
                return self._compile_call(expr)
            case VariableReferenceIR():
                return self._compile_variable_read(expr.declaration)
            case _:
                raise ValueError(expr)

    def _compile_binary_operation(self, expr: BinaryOperationIR):
        return self._compile_expr(expr.left_op) + self._compile_expr(expr.right_op) + self._compile_binary_operator(
            expr.kind)

    def _compile_unary_operation(self, expr: UnaryOperationIR):
        return self._compile_expr(expr.operand) + self._compile_unary_operator(expr.kind)

    def _compile_call(self, call: CallIR):
        arguments = list(itertools.chain.from_iterable([self._compile_expr(arg) for arg in call.args]))
        class_ref = self._clazz.qpool("class", self._class_name)
        method_ref = self._clazz.qpool("method", class_ref, _get_method_name(call.subroutine.declaration.index),
                                       _create_method_descriptor(call.subroutine.declaration))
        return arguments + ["invokestatic %d" % method_ref]

    def _compile_global_read(self, index):
        class_ref = self._clazz.qpool("class", self._class_name)
        field_ref = self._clazz.qpool("field", class_ref, get_field_name(index), "I")
        return ["getstatic %s" % field_ref]

    def _compile_global_write(self, index):
        class_ref = self._clazz.qpool("class", self._class_name)
        field_ref = self._clazz.qpool("field", class_ref, get_field_name(index), "I")
        return ["putstatic %s" % field_ref]

    def _compile_local_read(self, index):
        return ["iload %d" % index]

    def _compile_local_write(self, index):
        return ["istore %d" % index]

    def _compile_variable_read(self, variable_decl):
        match variable_decl:
            case GlobalVariableDeclarationIR():
                return self._compile_global_read(variable_decl.index)
            case LocalVariableDeclarationIR():
                index = self._subroutine_parameters_count + variable_decl.index
                return self._compile_local_read(index)
            case ParameterDeclarationIR():
                return self._compile_local_read(variable_decl.index)
            case _:
                raise ValueError(variable_decl)

    def _compile_if_statement(self, statement: IfStatementIR):
        expr = self._compile_expr(statement.condition)
        then_stmts = self._compile_statements(statement.then_block)
        if statement.else_block is None:
            l = self.gen_label()
            return expr + ["ifeq %s" % l] + then_stmts + ["%s:" % l]
        else_stmts = self._compile_statements(statement.else_block)
        l1 = self.gen_label()
        l2 = self.gen_label()
        return expr + ["ifeq %s" % l1] + then_stmts + ["goto %s" % l2] + ["%s:" % l1] + else_stmts + ["%s:" % l2]

    def _compile_var_assign(self, var, value):
        rvalue = self._compile_expr(value)
        match var:
            case GlobalVariableDeclarationIR():
                return rvalue + self._compile_global_write(var.index)
            case LocalVariableDeclarationIR():
                index = self._subroutine_parameters_count + var.index
                return rvalue + self._compile_local_write(index)
            case ParameterDeclarationIR():
                return rvalue + self._compile_local_write(var.index)
            case _:
                raise ValueError(var)

    def _compile_assign_statement(self, statement: AssignStatementIR):
        return self._compile_var_assign(statement.var.declaration, statement.value)

    def _compile_call_statement(self, statement: CallStatementIR):
        return self._compile_call(statement.call)

    def _compile_global_var_init(self, statement: GlobalVariableDeclarationIR):
        return self._compile_var_assign(statement, statement.init_value)

    def _compile_local_var_init(self, statement: LocalVariableDeclarationIR):
        return self._compile_var_assign(statement, statement.init_value)

    def _compile_return_statement(self, statement: ReturnStatementIR):
        if statement.return_value is None:
            return ["return"]
        return self._compile_expr(statement.return_value) + ["ireturn"]

    def _compile_statement(self, statement):
        match statement:
            case IfStatementIR():
                return self._compile_if_statement(statement)
            case AssignStatementIR():
                return self._compile_assign_statement(statement)
            case ReturnStatementIR():
                return self._compile_return_statement(statement)
            case CallStatementIR():
                return self._compile_call_statement(statement)
            case GlobalVariableDeclarationIR():
                return self._compile_global_var_init(statement)
            case LocalVariableDeclarationIR():
                return self._compile_local_var_init(statement)
            case _:
                raise ValueError(statement)

    def _compile_statements(self, statements: list):
        return list(
            itertools.chain.from_iterable([self._compile_statement(statement) for statement in statements]))

    def _compile_subroutine(self, subroutine: SubroutineDeclarationIR):
        self._subroutine_parameters_count = len(subroutine.parameters)
        code = self._compile_statements(subroutine.statements)
        if subroutine.subroutine_kind == SubroutineKind.PROCEDURE:
            code.append("return")
        while ":" in code[len(code) - 1]:
            code.pop()
        self._clazz.method("m%d" % subroutine.index, _create_method_descriptor(subroutine), ["private", "static"],
                           [CodeAttribute(assemble("\n".join(code)))])

    def _compile_subroutines(self, subroutines: list):
        for subroutine in subroutines:
            self._compile_subroutine(subroutine)

    def _compile_script_statements(self, statements):
        self._subroutine_parameters_count = 0
        code = self._compile_statements(statements)
        self._clazz.method("main", "()I", ["public", "static"], [CodeAttribute(assemble("\n".join(code)))])
