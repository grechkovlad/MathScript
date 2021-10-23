import parsing.Tokenizer
from parsing.Tokenizer import *
from parsing.Ast import *


class ParserException(Exception):
    def __init__(self, bad_token: Token, expected_types):
        super(ParserException, self).__init__("Unexpected token '%s' at %s. I was expecting %s" % (
            bad_token.value,
            bad_token.location,
            ", or ".join(map(lambda x: x if x in ["IDENT", "INT"] else "'%s'" % x, expected_types))))
        self.bad_token = bad_token
        self.expected_types = expected_types


def _eat_token(tokenizer, token_type):
    token = tokenizer.current()
    if token.type == token_type:
        tokenizer.advance()
        return token
    raise ParserException(token, [token_type])


def _get_start_position(location):
    match location:
        case parsing.Tokenizer.Location():
            return location.line, location.column_start
        case parsing.Parser.Location():
            return location.line_start, location.column_start


def _get_end_position(location):
    match location:
        case parsing.Tokenizer.Location():
            return location.line, location.column_end
        case parsing.Parser.Location():
            return location.line_end, location.column_end


def _interval_location(from_location, to_location):
    line_start, column_start = _get_start_position(from_location)
    line_end, column_end = _get_end_position(to_location)
    return parsing.Parser.Location(line_start, column_start, line_end, column_end)


def _from_token_location(token: Token):
    return Location(token.location.line, token.location.column_start, token.location.line, token.location.column_end)


def parse_identifier(tokenizer: Tokenizer):
    token = _eat_token(tokenizer, "IDENT")
    return Identifier(token.value, _from_token_location(token))


def parse_int(tokenizer: Tokenizer):
    token = _eat_token(tokenizer, "INT")
    return Integer(token.value, _from_token_location(token))


def parse_arguments(tokenizer: Tokenizer):
    arguments = []
    first_token = _eat_token(tokenizer, "(")
    if tokenizer.current().type == ")":
        last_token = _eat_token(tokenizer, ")")
        return ArgumentsList(arguments, _interval_location(first_token.location, last_token.location))
    arguments.append(parse_expr(tokenizer))
    while tokenizer.current().type != ")":
        _eat_token(tokenizer, ",")
        arguments.append(parse_expr(tokenizer))
    last_token = _eat_token(tokenizer, ")")
    return ArgumentsList(arguments, _interval_location(first_token.location, last_token.location))


def parse_parameters(tokenizer):
    params = []
    first_token = _eat_token(tokenizer, "(")
    if tokenizer.current().type == ")":
        last_token = _eat_token(tokenizer, ")")
        return ParametersList(params, _interval_location(first_token.location, last_token.location))
    params.append(parse_identifier(tokenizer))
    while tokenizer.current().type != ")":
        _eat_token(tokenizer, ",")
        params.append(parse_identifier(tokenizer))
    last_token = _eat_token(tokenizer, ")")
    return ParametersList(params, _interval_location(first_token.location, last_token.location))


def parse_call_statement(tokenizer):
    call = parse_call(tokenizer)
    last_token = _eat_token(tokenizer, ";")
    return CallStatement(call, _interval_location(call.location, last_token.location))


def parse_statement(tokenizer):
    match tokenizer.current().type:
        case "return":
            return parse_return(tokenizer)
        case "if":
            return parse_if(tokenizer)
        case "IDENT":
            tokenizer.advance()
            match tokenizer.current().type:
                case "(":
                    tokenizer.rollback()
                    return parse_call_statement(tokenizer)
                case "=":
                    tokenizer.rollback()
                    return parse_assign(tokenizer)
                case _:
                    raise ParserException(tokenizer.current(), ["(", "="])
        case _:
            raise ParserException(tokenizer.current(), ["return", "if", "IDENT"])


def parse_block(tokenizer):
    statements = []
    first_token = _eat_token(tokenizer, "{")
    while tokenizer.current().type != "}":
        statements.append(parse_statement(tokenizer))
    last_token = _eat_token(tokenizer, "}")
    return Block(statements, _interval_location(first_token.location, last_token.location))


def parse_subroutine(tokenizer: Tokenizer):
    match tokenizer.current().type:
        case "function":
            subroutine_kind = SubroutineKind.FUNCTION
        case "procedure":
            subroutine_kind = SubroutineKind.PROCEDURE
        case _:
            raise ParserException(tokenizer.current(), ["function", "procedure"])
    first_token = tokenizer.current()
    tokenizer.advance()
    name = parse_identifier(tokenizer)
    params = parse_parameters(tokenizer)
    body = parse_block(tokenizer)
    return SubroutineDecl(subroutine_kind, name, params, body,
                          _interval_location(first_token.location, body.location))


def parse_return(tokenizer: Tokenizer):
    first_token = _eat_token(tokenizer, "return")
    if tokenizer.current().type == ";":
        last_token = _eat_token(tokenizer, ";")
        return ReturnStatement(None, _interval_location(first_token.location, last_token.location))
    expr = parse_expr(tokenizer)
    last_token = _eat_token(tokenizer, ";")
    return ReturnStatement(expr, _interval_location(first_token.location, last_token.location))


def parse_g(tokenizer):
    match tokenizer.current().type:
        case "(":
            first_token = _eat_token(tokenizer, "(")
            g = parse_expr(tokenizer)
            last_token = _eat_token(tokenizer, ")")
            g.location = _interval_location(first_token.location, last_token.location)
            return g
        case "INT":
            return parse_int(tokenizer)
        case "IDENT":
            name = parse_identifier(tokenizer)
            if tokenizer.current().type == "(":
                tokenizer.rollback()
                return parse_call(tokenizer)
            else:
                return name
        case _:
            raise ParserException(tokenizer.current(), ["(", "IDENT", "INT"])


def parse_f(tokenizer):
    if tokenizer.current().type in ["!", "-"]:
        unary_operator = UnaryOperatorKind.MINUS if tokenizer.current().type == "-" else UnaryOperatorKind.NOT
        first_token = tokenizer.current()
        tokenizer.advance()
        g = parse_g(tokenizer)
        f = UnaryOperation(unary_operator, g, _interval_location(first_token.location, g.location))
        return f
    return parse_g(tokenizer)


def parse_e(tokenizer):
    f = parse_f(tokenizer)
    while tokenizer.current().type == "*":
        tokenizer.advance()
        right_hand_operand = parse_f(tokenizer)
        f = BinaryOperation(BinaryOperatorKind.MUL, f, right_hand_operand,
                            _interval_location(f.location, right_hand_operand.location))
    return f


def parse_d(tokenizer):
    d = parse_e(tokenizer)
    while tokenizer.current().type in ["+", "-"]:
        if tokenizer.current().type == "+":
            binary_operator = BinaryOperatorKind.PLUS
        else:
            binary_operator = BinaryOperatorKind.MINUS
        tokenizer.advance()
        right_hand_operand = parse_e(tokenizer)
        d = BinaryOperation(binary_operator, d, right_hand_operand,
                            _interval_location(d.location, right_hand_operand.location))
    return d


def parse_c(tokenizer):
    c = parse_d(tokenizer)
    while tokenizer.current().type in ["<", "<=", "==", ">=", ">"]:
        match tokenizer.current().type:
            case "<":
                binary_operator = BinaryOperatorKind.LESS
            case "<=":
                binary_operator = BinaryOperatorKind.LEQ
            case "==":
                binary_operator = BinaryOperatorKind.EQ
            case ">=":
                binary_operator = BinaryOperatorKind.GEQ
            case ">":
                binary_operator = BinaryOperatorKind.GREATER
        tokenizer.advance()
        right_hand_operand = parse_d(tokenizer)
        c = BinaryOperation(binary_operator, c, right_hand_operand,
                            _interval_location(c.location, right_hand_operand.location))
    return c


def parse_b(tokenizer):
    b = parse_c(tokenizer)
    while tokenizer.current().type == "&":
        tokenizer.advance()
        right_hand_operand = parse_c(tokenizer)
        b = BinaryOperation(BinaryOperatorKind.AND, b, right_hand_operand,
                            _interval_location(b.location, right_hand_operand.location))
    return b


def parse_expr(tokenizer):
    a = parse_b(tokenizer)
    while tokenizer.current().type == "|":
        tokenizer.advance()
        right_hand_operand = parse_b(tokenizer)
        a = BinaryOperation(BinaryOperatorKind.OR, a, right_hand_operand,
                            _interval_location(a.location, right_hand_operand.location))
    return a


def parse_if(tokenizer: Tokenizer):
    first_token = _eat_token(tokenizer, "if")
    condition = parse_expr(tokenizer)
    then_block = parse_block(tokenizer)
    end_location = then_block.location
    else_block = None
    if tokenizer.current().type == "else":
        tokenizer.advance()
        else_block = parse_block(tokenizer)
        end_location = else_block.location
    return IfStatement(condition, then_block, else_block, _interval_location(first_token.location, end_location))


def parse_call(tokenizer):
    subroutine = parse_identifier(tokenizer)
    arguments = parse_arguments(tokenizer)
    return Call(subroutine, arguments, _interval_location(subroutine.location, arguments.location))


def parse_assign(tokenizer):
    var = parse_identifier(tokenizer)
    _eat_token(tokenizer, "=")
    expr = parse_expr(tokenizer)
    last_token = _eat_token(tokenizer, ";")
    return AssignStatement(var, expr, _interval_location(var.location, last_token.location))


def parse_script(tokenizer: Tokenizer):
    body = []
    while tokenizer.current().type != "EOF":
        if tokenizer.current().type in ["function", "procedure"]:
            body.append(parse_subroutine(tokenizer))
            continue
        if tokenizer.current().type in ["return", "IDENT", "if"]:
            body.append(parse_statement(tokenizer))
            continue
        raise ParserException(tokenizer.current(), ["function", "procedure", "return", "IDENT", "if"])
    return Script(body)
