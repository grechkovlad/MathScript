from grammar import module
from graphviz import Digraph

dot = Digraph(comment='The Round Table')

dot.node('A', 'King Arthur')

dot.render("graph", format="png")
