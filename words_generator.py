from grammar import *
from fractions import Fraction as frac

from random import randint, seed, choice


def random_int_terminal():
    return randint(1, 1)


def random_ident():
    return "id"


def random_star_count():
    return randint(0, 1)


def randbool():
    return choice([True, False])


def generate_random_word(v, depth):
    if isinstance(v, Literal):
        return v.name
    if isinstance(v, Integer):
        return str(random_int_terminal())
    if isinstance(v, Ident):
        return random_ident()
    if isinstance(v, NonTerminal):
        return generate_random_word(v.rule, depth + 1)
    if isinstance(v, Or):
        choice1 = choice(v.list)
        return generate_random_word(choice1, depth + 1)
    if isinstance(v, Concat):
        return "".join([generate_random_word(child, depth + 1) for child in v.list])
    if isinstance(v, Question):
        is_eps = choice([True, False])
        if is_eps:
            return ""
        else:
            return generate_random_word(v.expr, depth + 1)
    if isinstance(v, Star):
        star_count = random_star_count()
        return "".join([generate_random_word(v.expr, depth + 1) for _ in range(star_count)])


e = NonTerminal("e")
f = NonTerminal("f")
t = NonTerminal("t")
PLUS = Literal("+")
MULT = Literal("*")

e.rule = Concat([f, Star(Concat([PLUS, f]))])
f.rule = Concat([t, Star(Concat([MULT, t]))])
t.rule = Or([INTEGER, Concat([OPEN_BRACKET, e, CLOSE_BRACKET])])


def generate_E():
    if randbool():
        return generate_F() + "+" + generate_F()
    else:
        return generate_F()


def generate_F():
    if randbool():
        return generate_T() + "*" + generate_T()
    else:
        return generate_T()


def generate_T():
    if randbool():
        return "(" + generate_E() + ")"
    else:
        return "1"


def depth_e():
    if randbool():
        return max(depth_f(), depth_f()) + 1
    else:
        return depth_f() + 1


def depth_f():
    if randbool():
        return max(depth_t(), depth_t()) + 1
    else:
        return depth_t() + 1


def depth_t():
    if randbool():
        return depth_e() + 1
    else:
        return 1



RUNS = 3000
rec = dict()
for _ in range(RUNS):
    try:
        run_depth = depth_e()
        if not run_depth in rec:
            rec[run_depth] = 0
        rec[run_depth] = rec[run_depth] + 1
    except RecursionError as _:
        if not "error" in rec:
            rec["error"] = 0
        rec["error"] = rec["error"] + 1

for key in rec.keys():
    rec[key] = rec[key] / RUNS

print(rec)


p_store = {("t", 1): frac(1, 2)}


def gen_tuples(k):
    return [(i, k - 1) for i in range(1, k)] + ([(k - 1, i) for i in range(1, k - 1)])


def p(non_terminal, depth):
    if depth == 0:
        return 0
    if (non_terminal, depth) in p_store:
        return p_store[(non_terminal, depth)]
    if non_terminal == "e":
        res = frac(1, 2) * (p("f", depth - 1) + sum([p("f", k1) * p("f", k2) for k1, k2 in gen_tuples(depth)]))
    if non_terminal == "f":
        res = frac(1, 2) * (p("t", depth - 1) + sum([p("t", k1) * p("t", k2) for k1, k2 in gen_tuples(depth)]))
    if non_terminal == "t":
        res = frac(1, 2) * p("e", depth - 1)
    p_store[(non_terminal, depth)] = res
    return res

cdf = 0
for depth in range(1, 15):
    prob = p("e", depth)
    print("%d %s %f" % (depth, prob, prob))
