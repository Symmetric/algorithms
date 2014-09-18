from copy import deepcopy
import logging
from random import random

_log = logging.getLogger(__name__)


def _get_random_edge(graph):
    index = int(random() * len(graph.edges))
    _log.debug('Random index %s', index)
    edge = graph.edges[index]
    return edge


def _merge_nodes(graph, first_node, second_node):
    super_node = first_node
    _log.debug('First node: %s (%s). Second node: %s (%s).',
               first_node, first_node.edges, second_node, second_node.edges)
    for edge in second_node.edges:
        _log.debug('Processing edge %s', edge)
        # First, check whether this edge will be a self-loop (in which case remove it)
        if ((edge.head == second_node and edge.tail == first_node) or
                (edge.head == first_node and edge.tail == second_node)):
            _log.debug('Self-loop, removing edge %s.', edge)
            graph.remove_edge(edge)
        else:
            # Retarget all edges to point to the merged node instead of the second node.
            _log.debug('Retargeting edge %s', edge)
            if edge.head == second_node:
                edge.head = super_node
            else:
                assert edge.tail == second_node, "node.edges contained edge which didn't point to node."
                edge.tail = super_node

            # Update the supernode's edge list too.
            super_node.add_edge(edge)
            _log.debug('New edge is %s', edge)

    # Finally, trim the second node that was merged.
    graph.remove_node(second_node)


def run_random_contraction_algorithm(graph):
    iterations = len(graph.nodes) ** 2
    min_edges = len(graph.edges)
    _log.info('Running for %s iterations', iterations)
    for i in range(iterations):
        working_graph = deepcopy(graph)
        _log.debug('Iteration %s', i)
        while len(working_graph.nodes) > 2:
            edge = _get_random_edge(working_graph)
            _merge_nodes(working_graph, edge.tail, edge.head)
        if len(working_graph.edges) < min_edges:
            min_edges = len(working_graph.edges)

    return min_edges
