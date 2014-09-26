import itertools
from collections import deque, defaultdict
import logging

_log = logging.getLogger(__name__)


class GraphException(Exception):
    pass


class Node:
    def __init__(self, label=None):
        self.edges = []
        self.incident_edges = []
        self.outgoing_edges = []
        self.label = label

    def add_edge(self, edge):
        """Add an edge to the node's local lists.

        Will add to the appropriate incident/outgoing list based
        on whether the edge is directed.
        """
        self.edges.append(edge)
        if not self in [edge.head, edge.tail]:
            raise GraphException('%s does not reference %s' % (edge, self))

        if edge.directed:
            if edge.head == self:
                self.incident_edges.append(edge)
            else:
                self.outgoing_edges.append(edge)
        else:
            # Undirected edge. Count as both incident and outgoing.
            self.incident_edges.append(edge)
            self.outgoing_edges.append(edge)

    def remove_edge(self, edge):
        """Remove an edge from the node's local lists.

        Will remove from the appropriate incident/outgoing list based
        on whether the edge is directed.
        """
        self.edges.remove(edge)

        if edge.directed:
            if edge.head == self:
                self.incident_edges.remove(edge)
            elif edge.tail == self:
                self.outgoing_edges.remove(edge)
        else:
            # Undirected edge. Count as both incident and outgoing.
            self.incident_edges.remove(edge)
            self.outgoing_edges.remove(edge)

    def get_edges_by_label(self, label):
        """Get a list of edges with the specified label."""
        edges = [edge for edge in self.edges if edge.label == label]

        if not edges:
            # No hits
            raise GraphException('No edge with label "%s"' % label)
        else:
            return edges

    def __repr__(self):
        return 'Node(%s)' % self.label


class Edge:
    def __init__(self, tail, head, label=None):
        self.tail = tail
        self.head = head
        self.label = label
        self.directed = False
        self.tail.add_edge(self)
        self.head.add_edge(self)

    def get_other_node(self, node):
        if self.tail == node:
            return self.head
        elif self.head == node:
            return self.tail
        else:
            raise GraphException('Edge %s does not reference node %s' % (self, node))

    def delete(self):
        self.tail.remove_edge(self)
        self.head.remove_edge(self)

    def __repr__(self):
        return 'Edge(%s, %s)' % (self.tail, self.head)


class DirectedEdge:
    def __init__(self, tail, head, label=None):
        self.tail = tail
        self.head = head
        self.label = label
        self.directed = True
        self.tail.add_edge(self)
        self.head.add_edge(self)


class Graph:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_node(self, node):
        self.nodes.append(node)

    def add_node_by_label(self, label):
        if label in [node.label for node in self.nodes]:
            raise GraphException('Node %s already exists in graph.', label)
        else:
            node = Node(label=label)
            self.add_node(node)
            return node

    def remove_node(self, node):
        try:
            self.nodes.remove(node)
        except ValueError:
            raise GraphException('Node %s not found.' % node)

    def add_edge_by_label(self, tail_label, head_label, edge_label=None, directed=False):
        for label in [tail_label, head_label]:
            if label not in [node.label for node in self.nodes]:
                raise GraphException('Node %s does not exist in graph.' % label)

        tail = self.get_node_by_label(tail_label)
        head = self.get_node_by_label(head_label)

        edge_cls = DirectedEdge if directed else Edge
        edge = edge_cls(tail, head, label=edge_label)
        self.edges.append(edge)
        return edge

    def remove_edge(self, edge):
        """Remove an edge from the Graph.

        Also updates the edge-list of the nodes.
        """
        try:
            self.edges.remove(edge)
            edge.delete()
        except ValueError:
            raise GraphException('Edge %s not found.' % edge)

    def get_node_by_label(self, label):
        """Get first node with the specified label."""
        for node in self.nodes:
            if node.label == label:
                return node
        else:
            # No hits
            raise GraphException('No node with label "%s"' % label)

    def breadth_first_search(self, start, end=None):
        """Perform a breadth-first search for a path from 'start' to 'end'."""
        for node in self.nodes:
            node.explored = None

        # Put the starting node in the frontier list.
        frontier = deque([start])
        explored_list = []

        # Nodes are marked explored once they are in the frontier
        explored = {start: True}
        node_layer = {start: 0}

        found = False

        # Loop until the frontier is empty (no more nodes to explore), or we find the target.
        while frontier and not found:
            _log.debug('Frontier: %s', frontier)
            node = frontier.popleft()
            _log.debug('Exploring node %s', node)
            explored_list.append((node, node_layer[node]))
            if node == end:
                found = True
            for edge in node.edges:
                other_node = edge.get_other_node(node)
                _log.debug('Examining other node %s (explored=%s)', other_node, other_node.explored)
                if other_node not in explored:
                    frontier.append(other_node)
                    explored[other_node] = True
                    # By definition, all other_nodes are one layer deeper than the current node.
                    node_layer[other_node] = node_layer[node] + 1
                    # Keep a reference to the node that discovered the other_node
                    edge_to_parent[other_node] = edge
                    _log.debug('Marked other node explored, layer=%s', node_layer[other_node])
                    # Else other node was explored already, so ignore it.

        return found, explored_list, edge_to_parent

    def bfs_path(self, start_node, end_node):
        """
        Get the path from start_node to end_node, as calculated by the BFS algorithm.

        Note that this will evaluate the path with the lowest number of hops, not the shortest distance.

        :param start_node: The node to start the search on.
        :param end_node: The node to find a path to.
        :return path: A list containing the path from the start_node to the end_node.
        """
        _, _, edge_to_parent = self.breadth_first_search(start_node, end_node)

        node = end_node
        edge = edge_to_parent[node]
        path = []

        while edge:
            path.append(edge)
            node = edge.get_other_node(node) if edge else None
            edge = edge_to_parent[node]

        return path[::-1]

    def bfs_connected_regions(self):
        """Use the BFS algorithm to determine the connected regions of an undirected graph."""
        regions = []
        for node in self.nodes:
            # Make a list from the nodes in all regions.
            discovered_nodes = itertools.chain.from_iterable(regions)
            if node not in discovered_nodes:
                _, new_explored = self.breadth_first_search(node)
                regions.append([result[0] for result in new_explored])  # Unpack the explored tuples to get the nodes.
                _log.info('Found new region %s', regions[-1])

        return regions

    def __eq__(self, other):
        if other is None:
            return False
        elif len(self.nodes) != len(other.nodes):
            return False
        elif len(self.edges) != len(other.edges):
            return False
        else:
            for node in self.nodes:
                if node not in other.nodes:
                    return False
            for edge in self.edges:
                if edge not in other.edges:
                    return False
        return True

    def __repr__(self):
        return 'Graph(nodes=%s, edges=%s)' % (self.nodes, self.edges)