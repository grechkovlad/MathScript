from random import randint, choice

from grammar import *

START_MAX = 5
IDENT_LEN_MAX = 5
MAX_DEPTH = 20


def random_int_terminal():
    return randint(-100, 100)


def random_ident():
    len = randint(1, IDENT_LEN_MAX)
    return "".join([chr(randint(ord('a'), ord('z'))) for _ in range(len)])


def random_star_count():
    return randint(0, START_MAX)


def randbool():
    return choice([True, False])


def generate_random_word(v, depth):
    if isinstance(v, Literal):
        return [v.name]
    if isinstance(v, NamedTerminal) and v.name == "IDENT":
        return [str(random_ident())]
    if isinstance(v, NamedTerminal) and v.name == "INTEGER":
        return [random_int_terminal()]
    if isinstance(v, NonTerminal):
        return generate_random_word(v.rule, depth + 1)
    if isinstance(v, Or):
        or_choice = choice(v.list)
        return generate_random_word(or_choice, depth + 1)
    if isinstance(v, Concat):
        res = []
        for child in v.list:
            res.extend(generate_random_word(child, depth + 1))
        return res
    if isinstance(v, Question):
        return_eps = True if depth > MAX_DEPTH else randbool()
        if return_eps:
            return []
        else:
            return generate_random_word(v.expr, depth + 1)
    if isinstance(v, Star):
        star_count = 0 if depth > MAX_DEPTH else random_star_count()
        res = []
        for _ in range(star_count):
            res.extend((generate_random_word(v.expr, depth + 1)))
        return res
