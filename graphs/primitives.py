

class GraphException(Exception):
    pass


class Node:
    def __init__(self):
        self.edges = []

    def add_edge(self, edge):
        self.edges.append(edge)


class Edge:
    def __init__(self, tail, head):
        self.tail = tail
        self.head = head


class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}

    def add_node(self, label):
        if label in self.nodes:
            raise GraphException('Node %s already exists in graph.', label)
        else:
            node = self.nodes[label] = Node()
            return node

    def add_edge(self, tail, head):
        for node in [tail, head]:
            if node not in self.nodes:
                raise GraphException('Node %s does not exist in graph.', node)

        # If we've not seen this pair of nodes before, initialize.
        if (tail, head) not in self.edges:
            self.edges[(tail, head)] = []

        edge = Edge(tail, head)
        self.edges[(tail, head)].append(edge)
        return edge
