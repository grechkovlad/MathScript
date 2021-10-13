from parsing.Tokenizer import *
from parsing.Ast import *


class ParserException(Exception):
    def __init__(self, bad_token: Token, expected_types):
        super(ParserException, self).__init__("Unexpected token '%s' at %d:%d-%d. I was expecting %s" % (
            bad_token.value, bad_token.line, bad_token.column_start, bad_token.column_end, " or".join(expected_types)))
        pass


def _eat_token(tokenizer, token_type):
    token = tokenizer.current()
    if token.type == token_type:
        tokenizer.advance()
        return token
    raise ParserException(token, [token_type])


def parse_parameters(tokenizer):
    params = []
    _eat_token(tokenizer, "(")
    if tokenizer.current().type == ")":
        return params
    params.append(_eat_token(tokenizer, "IDENT").value)
    while tokenizer.current().type != ")":
        _eat_token(tokenizer, ",")
        params.append(_eat_token(tokenizer, "IDENT").value)
    _eat_token(tokenizer, ")")
    return params


def parse_call_statement(tokenizer):
    call = parse_call(tokenizer)
    _eat_token(tokenizer, ";")
    return CallStatement(call)


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
    body = []
    _eat_token(tokenizer, "{")
    while tokenizer.current().type != "}":
        body.append(parse_statement(tokenizer))
    _eat_token(tokenizer, "}")
    return body


def parse_function(tokenizer: Tokenizer):
    _eat_token(tokenizer, "function")
    name = _eat_token(tokenizer, "IDENT").value
    params = parse_parameters(tokenizer)
    body = parse_block(tokenizer)
    return FunctionDecl(name, params, body)


def parse_procedure(tokenizer: Tokenizer):
    _eat_token(tokenizer, "procedure")
    name = _eat_token(tokenizer, "IDENT").value
    params = parse_parameters(tokenizer)
    body = parse_block(tokenizer)
    return FunctionDecl(name, params, body)


def parse_return(tokenizer: Tokenizer):
    _eat_token(tokenizer, "return")
    if tokenizer.current().type == ";":
        return ReturnStatement()
    return ReturnStatement(parse_expr(tokenizer))


def parse_f(tokenizer):
    match tokenizer.current().type:
        case "!":
            unary_operator = UnaryOperatorKind.NOT
            tokenizer.advance()
        case "-":
            unary_operator = UnaryOperatorKind.MINUS
            tokenizer.advance()
        case _:
            unary_operator = None

    match tokenizer.current().type:
        case "(":
            tokenizer.advance()
            f = parse_expr(tokenizer)
            _eat_token(tokenizer, ")")
        case "INT":
            f = tokenizer.current().value
            tokenizer.advance()
        case "IDENT":
            name = _eat_token(tokenizer, "IDENT").value
            if tokenizer.current().type == "(":
                tokenizer.rollback()
                f = parse_call(tokenizer)
            else:
                f = name
        case _:
            raise ParserException(tokenizer.current(), ["(", "IDENT", "INT"])
    if unary_operator is None:
        return f
    return UnaryOperation(unary_operator, f)


def parse_e(tokenizer):
    f = parse_f(tokenizer)
    while tokenizer.current().type == "*":
        tokenizer.advance()
        f = BinaryOperation(BinaryOperatorKind.MUL, f, parse_f(tokenizer))
    return f


def parse_d(tokenizer):
    d = parse_e(tokenizer)
    while tokenizer.current().type in ["+", "-"]:
        if tokenizer.current().type == "+":
            binary_operator = BinaryOperatorKind.PLUS
        else:
            binary_operator = BinaryOperatorKind.MINUS
        tokenizer.advance()
        d = BinaryOperation(binary_operator, d, parse_e(tokenizer))
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
        c = BinaryOperation(binary_operator, c, parse_d(tokenizer))
    return c


def parse_b(tokenizer):
    b = parse_c(tokenizer)
    while tokenizer.current().type == "&":
        tokenizer.advance()
        b = BinaryOperation(BinaryOperatorKind.AND, b, parse_c(tokenizer))
    return b


def parse_expr(tokenizer):
    a = parse_b(tokenizer)
    while tokenizer.current().type == "|":
        tokenizer.advance()
        a = BinaryOperation(BinaryOperatorKind.OR, a, parse_b(tokenizer))
    return a


def parse_if(tokenizer: Tokenizer):
    _eat_token(tokenizer, "if")
    condition = parse_expr(tokenizer)
    then_block = parse_block(tokenizer)
    else_block = None
    if tokenizer.current().type == "else":
        tokenizer.advance()
        else_block = parse_block(tokenizer)
    return IfStatement(condition, then_block, else_block)


def parse_call(tokenizer):
    subroutine = _eat_token(tokenizer, "IDENT").value
    _eat_token(tokenizer, "(")
    if tokenizer.current().type == ")":
        tokenizer.advance()
        return Call(subroutine, [])
    arguments = [parse_expr(tokenizer)]
    while tokenizer.current().type != ")":
        _eat_token(tokenizer, ",")
        arguments.append(parse_expr(tokenizer))
    tokenizer.advance()
    return Call(subroutine, arguments)


def parse_assign(tokenizer):
    var = _eat_token(tokenizer, "IDENT").value
    _eat_token(tokenizer, "=")
    expr = parse_expr(tokenizer)
    _eat_token(tokenizer, ";")
    return AssignStatements(var, expr)


def parse_script(tokenizer: Tokenizer):
    tokenizer.advance()
    body = []
    while tokenizer.current().type != "EOF":
        if tokenizer.current().type == "function":
            body.append(parse_function(tokenizer))
            continue
        if tokenizer.current().type == "procedure":
            body.append(parse_procedure(tokenizer))
            continue
        if tokenizer.current().type in ["return", "IDENT", "if"]:
            body.append(parse_statement(tokenizer))
            continue
        raise ParserException(tokenizer.current(), ["function", "procedure", "return", "IDENT", "if"])
    return Script(body)
