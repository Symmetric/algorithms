import logging
import unittest
from graphs.primitives import Graph, GraphException

_log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class GraphTestCase(unittest.TestCase):
    def _setup_basic_graph(self):
        self.graph = Graph()
        self.node_a = self.graph.add_node_by_label('a')
        self.node_b = self.graph.add_node_by_label('b')
        self.edge_a_b = self.graph.add_edge_by_label('a', 'b')

    def _setup_triangle_graph(self):
        self.graph = Graph()
        self.node_a = self.graph.add_node_by_label('a')
        self.node_b = self.graph.add_node_by_label('b')
        self.node_c = self.graph.add_node_by_label('c')
        self.edge_a_b = self.graph.add_edge_by_label('a', 'b')
        self.edge_b_c = self.graph.add_edge_by_label('b', 'c')
        self.edge_c_a = self.graph.add_edge_by_label('c', 'a')


class TestGraph(GraphTestCase):
    def test_simple(self):
        """Test a simple 2-node graph with one edge."""
        graph = Graph()
        a = graph.add_node_by_label('a')
        b = graph.add_node_by_label('b')
        a_b = graph.add_edge_by_label('a', 'b')

        self.assertTrue(a in graph.nodes)
        self.assertTrue(b in graph.nodes)
        self.assertTrue(a_b in graph.edges)

    def test_parallel(self):
        """Test a 2-node graph with parallel edges."""
        graph = Graph()
        a = graph.add_node_by_label('a')
        b = graph.add_node_by_label('b')
        a_b_1 = graph.add_edge_by_label('a', 'b')
        a_b_2 = graph.add_edge_by_label('a', 'b')

        self.assertTrue(a in graph.nodes)
        self.assertTrue(b in graph.nodes)
        self.assertTrue(a_b_1 in graph.edges)
        self.assertTrue(a_b_2 in graph.edges)

    def test_add_edge_by_label(self):
        """Test that an exception is raised when adding an edge with a non-existant label."""
        self._setup_basic_graph()
        self.assertRaises(GraphException, self.graph.add_edge_by_label, 'z', 'x')

    def test_add_node_by_label(self):
        """Test that an exception is raised when adding a node with a duplicate label."""
        self._setup_basic_graph()
        self.assertRaises(GraphException, self.graph.add_node_by_label, 'a')

    def test_bfs(self):
        """Test Breadth First Search in a graph."""
        self._setup_triangle_graph()
        self.node_d = self.graph.add_node_by_label('d')  # Unconnected node

        found, explored = self.graph.breadth_first_search(self.node_a, self.node_c)

        _log.info('Found? %s. Explored: %s', found, explored)
        self.assertTrue(found)
        self.assertEquals(explored, [self.node_a, self.node_b, self.node_c])

    def test_bfs_fail(self):
        """Test that BFS explores all nodes if it doesn't find the target."""
        self._setup_triangle_graph()
        self.node_d = self.graph.add_node_by_label('d')  # Unconnected node

        found, explored = self.graph.breadth_first_search(self.node_a, self.node_d)

        _log.info('Found? %s. Explored: %s', found, explored)
        self.assertFalse(found)
        self.assertEquals(explored, [self.node_a, self.node_b, self.node_c])