from collections import deque
import logging

_log = logging.getLogger(__name__)


class GraphException(Exception):
    pass


class Node:
    def __init__(self, label=None):
        self.edges = []
        self.label = label

    def add_edge(self, edge):
        self.edges.append(edge)

    def remove_edge(self, edge):
        for i, this_edge in enumerate(self.edges):
            if this_edge == edge:
                del self.edges[i]
                break
        else:
            raise GraphException('Edge %s not found on node %s.' % (edge, self))

    def get_edges_by_label(self, label):
        """Get first edge with the specified label."""
        edges = []
        for edge in self.edges:
            if edge.label == label:
                edges.append(edge)

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
        self.tail.add_edge(self)
        self.head.add_edge(self)

    def get_other_node(self, node):
        if self.tail == node:
            return self.head
        elif self.head == node:
            return self.tail
        else:
            raise GraphException('Edge %s does not reference node %s' % (self, node))

    def __repr__(self):
        return 'Edge(%s, %s)' % (self.tail, self.head)


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
        for i, this_node in enumerate(self.nodes):
            if this_node == node:
                del self.nodes[i]
                # delete edges too?
                break
        else:
            raise GraphException('Node %s not found.' % node)

    def add_edge(self, edge):
        self.edges.append(edge)

    def add_edge_by_label(self, tail_label, head_label, edge_label=None):
        for label in [tail_label, head_label]:
            if label not in [node.label for node in self.nodes]:
                raise GraphException('Node %s does not exist in graph.' % label)

        tail = self.get_node_by_label(tail_label)
        head = self.get_node_by_label(head_label)

        edge = Edge(tail, head, label=edge_label)
        self.add_edge(edge)
        return edge

    def remove_edge(self, edge):
        """Remove an edge from the Graph.

        Also updates the edge-list of the nodes.
        """
        for i, this_edge in enumerate(self.edges):
            if this_edge == edge:
                del self.edges[i]
                edge.head.remove_edge(edge)
                edge.tail.remove_edge(edge)
                break
        else:
            raise GraphException('Edge %s not found.' % edge)

    def get_node_by_label(self, label):
        """Get first node with the specified label."""
        for node in self.nodes:
            if node.label == label:
                return node
        else:
            # No hits
            raise GraphException('No node with label "%s"' % label)

    def breadth_first_search(self, start, end):
        """Perform a breadth-first search for a path from 'start' to 'end'."""
        for node in self.nodes:
            node.explored = None

        # Put the starting node in the frontier list.
        frontier = deque([start])
        explored_list = []
        # Nodes are marked explored once they are in the frontier
        start.explored = True

        found = False

        # Loop until the frontier is empty (no more nodes to explore), or we find the target.
        while frontier and not found:
            _log.debug('Frontier: %s', frontier)
            node = frontier.popleft()
            _log.debug('Exploring node %s', node)
            explored_list.append(node)
            if node == end:
                found = True
            for edge in node.edges:
                other_node = edge.get_other_node(node)
                _log.debug('Examining other node %s (explored=%s)', other_node, other_node.explored)
                if not other_node.explored:
                    frontier.append(other_node)
                    other_node.explored = True
                    # Else other node was explored already, so ignore it.

        return found, explored_list

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