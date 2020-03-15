from cfg_structures import *
from graphviz import Digraph
from grammar import module


class Counter:
    def __init__(self, _from):
        self.val = _from

    def inc(self):
        self.val = self.val + 1
        return str(self.val - 1)


def _to_graphviz(v, graph, storage, counter):
    if isinstance(v, Terminal):
        v_id = counter.inc()
        graph.node(v_id, label=v.name, _attributes={"shape": "square", "fillcolor": "pink", "style": "filled"})
        return v_id
    if isinstance(v, NonTerminal):
        if v in storage:
            return storage[v]
        storage[v] = counter.inc()
        graph.node(storage[v], label=v.name,
                   _attributes={"shape": "square", "fillcolor": "green", "style": "filled"})
        rule_node_id = _to_graphviz(v.rule, graph, storage, counter)
        graph.edge(storage[v], rule_node_id)
        return storage[v]
    else:
        v_id = counter.inc()
        graph.node(v_id, label="", _attributes={"shape": _get_regex_shape(v)})
        if isinstance(v, Or) or isinstance(v, Concat):
            children = [_to_graphviz(child, graph, storage, counter) for child in v.list]
            for index, child in enumerate(children):
                if isinstance(v, Or):
                    graph.edge(v_id, child)
                else:
                    graph.edge(v_id, child, label=str(index))
            return v_id
        if isinstance(v, Question) or isinstance(v, Star):
            child = _to_graphviz(v.expr, graph, storage, counter)
            graph.edge(v_id, child)
            return v_id
        raise NotImplementedError("Unknown node type")


def _get_regex_shape(v):
    if isinstance(v, Or):
        return "diamond"
    if isinstance(v, Concat):
        return "egg"
    if isinstance(v, Star):
        return "star"
    if isinstance(v, Question):
        return "invtriangle"


def visualize(root, file):
    graph = Digraph()
    graph.node("0", label="kleenee star", _attributes={"shape": "star"})
    graph.node("1", label="concatenation", _attributes={"shape": "egg"})
    graph.node("2", label="alternative", _attributes={"shape": "diamond"})
    graph.node("3", label="optional", _attributes={"shape": "invtriangle"})
    graph.node("4", label="terminal", _attributes={"shape": "square", "fillcolor": "pink", "style": "filled"})
    graph.node("5", label="nonterminal",
               _attributes={"shape": "square", "fillcolor": "green", "style": "filled"})
    _to_graphviz(root, graph, dict(), Counter(6))
    graph.render(file, format="png")


visualize(module, "grammar_visualization")
