from cfg_structures import *
from graphviz import Digraph
from grammar import module


def _to_graphviz(v, graph, storage):
    if isinstance(v, Terminal):
        storage[v] = str(len(storage))
        graph.node(storage[v], label=v.name, _attributes={"shape": "square", "fillcolor": "red", "style": "filled"})
        return storage[v]
    if isinstance(v, NonTerminal):
        if v in storage:
            return storage[v]
        storage[v] = str(len(storage))
        graph.node(storage[v], label=v.name, _attributes={"shape": "square", "fillcolor": "green", "style": "filled"})
        rule_node_id = _to_graphviz(v.rule, graph, storage)
        graph.edge(storage[v], rule_node_id)
        return storage[v]
    else:
        storage[v] = str(len(storage))
        graph.node(storage[v], label=_get_regex_label(v))
        if isinstance(v, Or) or isinstance(v, Concat):
            children = [_to_graphviz(child, graph, storage) for child in v.list]
            for index, child in enumerate(children):
                if isinstance(v, Or):
                    graph.edge(storage[v], child)
                else:
                    graph.edge(storage[v], child, label=str(index))
            return storage[v]
        if isinstance(v, Question) or isinstance(v, Star):
            child = _to_graphviz(v.expr, graph, storage)
            graph.edge(child, storage[v])
            return storage[v]
        raise NotImplementedError("Unknown node type")


def _get_regex_label(v):
    if isinstance(v, Or):
        return "Or"
    if isinstance(v, Concat):
        return "Concat"
    if isinstance(v, Star):
        return "*"
    if isinstance(v, Question):
        return "?"


def visualize(root, file):
    graph = Digraph()
    _to_graphviz(root, graph, dict())
    graph.render("file", format="png")


visualize(module, "graph")
