import networkx as nx
from block import Block
from settings import WEIGHTS, NUM_VALIDATORS, ESTIMATE_SPACE
from math import pi
import matplotlib.pyplot as plt
import pylab
import plot_tool
import copy


def plot_view(view, coloured_bets=[], colour='green', use_edges=[], thick_edges=[], colored_edges=[]):

    G = nx.Graph()

    nodes = view.messages

    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = 20
    fig_size[1] = 20
    plt.rcParams["figure.figsize"] = fig_size

    for b in nodes:
        G.add_edges_from([(b, b)])

    edges = []
    if use_edges == []:
        for b in nodes:
            for b2 in b.justification.latest_messages.values():
                if b2 is not None:
                    edges.append((b2, b))
    else:
        for e in use_edges:
            if e[0] in nodes and e[1] in nodes:
                edges.append((e[0], e[1]))

    # G.add_edges_from([('A', 'B'),('C','D'),('G','D')])
    # G.add_edges_from([('C','F')])

    positions = dict()

    for b in nodes:
        positions[b] = (float)(b.sender + 1)/(float)(NUM_VALIDATORS + 1), 0.2 + 0.1*b.height

    node_color_map = {}
    for b in nodes:
        if b in coloured_bets:
            node_color_map[b] = colour
        else:
            node_color_map[b] = 'white'

    color_values = [node_color_map.get(node) for node in nodes]

    labels = {}

    node_sizes = []
    for b in nodes:
        node_sizes.append(700*pow(WEIGHTS[b.sender]/pi, 0.5))
        labels[b] = b.sequence_number

    # nx.draw(G, positions, , node_size=node_sizes, edge_color='black', edge_cmap=plt.cm.Reds)

    nx.draw_networkx_nodes(G, positions, alpha=0.3, node_color=color_values, nodelist=nodes, node_size=node_sizes,edge_color='black')
    if colored_edges != []:
        nx.draw_networkx_edges(G, positions, edgelist=colored_edges, width=10, edge_color='r')
    if thick_edges != []:
        nx.draw_networkx_edges(G, positions, edgelist=thick_edges, width=1, style='solid')

    nx.draw_networkx_edges(G, positions, edgelist=edges, style='dashed', edge_color='grey')
    nx.draw_networkx_labels(G, positions, labels=labels)

    #fig = plt.figure(figsize=(10, 10))
    #ax = fig.add_subplot()
    ax = plt.gca()  # to get the current axis
    ax.collections[0].set_edgecolor("black")
    ax.text(-0.05, 0.1, "Weights: ", fontsize=20)

    for v in xrange(NUM_VALIDATORS):
        xpos = (float)(v + 1)/(float)(NUM_VALIDATORS + 1) - 0.01
        ax.text(xpos, 0.1, (str)((int)(WEIGHTS[v])), fontsize=20)


    pylab.show()
    plt.close('all')
