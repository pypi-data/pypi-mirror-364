#!/usr/bin/env python3

import sys
from graphviz import Digraph, Source
from graph_builder import build_graph
from smume.course_model import courses
from smume.styles import styles

def apply_styles(graph, styles):
    graph.graph_attr.update(styles.get('graph', {}))
    graph.node_attr.update(styles.get('nodes', {}))
    graph.edge_attr.update(styles.get('edges', {}))
    return graph

def add_embedded_legend(graph):
    with graph.subgraph(name="cluster_legend") as legend:
        legend.attr(label="Legend", style="dashed")
        legend.attr(rank="sink")  # Push to bottom
        legend.node("prereq_label", "prerequisite", shape="plaintext")
        legend.node("coreq_label", "corequisite", shape="plaintext")
        legend.node("coprereq_label", "con-prerequisite", shape="plaintext")
        legend.node("prereq_box", "", shape="box", style="filled", width="0.3", height="0.2")
        legend.node("coreq_box", "", shape="box", style="filled,dashed", width="0.3", height="0.2")
        legend.node("coprereq_box", "", shape="box", style="filled,dotted", width="0.3", height="0.2")
        legend.edge("prereq_label", "prereq_box", penwidth="3")
        legend.edge("coreq_label", "coreq_box", dir="both", penwidth="3")
        legend.edge("coprereq_label", "coprereq_box", style="dashed", penwidth="3")

def main():
    graph = build_graph()
    graph = apply_styles(graph, styles)
    add_embedded_legend(graph)
    graph.render('img/flowchart', view=True)

if __name__ == '__main__':
    main()