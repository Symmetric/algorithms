import unittest
from graphs.primitives import Graph

__author__ = 'paul'


class TestGraph(unittest.TestCase):
    def test_simple(self):
        """Test a simple 2-node graph with one edge."""
        graph = Graph()
        a = graph.add_node('a')
        b = graph.add_node('b')
        a_b = graph.add_edge('a', 'b')

        self.assertEqual(graph.nodes, {'a': a, 'b': b})
        self.assertEqual(graph.edges, {('a', 'b'): [a_b]})

    def test_parallel(self):
        """Test a 2-node graph with parallel edges."""
        graph = Graph()
        a = graph.add_node('a')
        b = graph.add_node('b')
        a_b_1 = graph.add_edge('a', 'b')
        a_b_2 = graph.add_edge('a', 'b')

        self.assertEqual(graph.nodes, {'a': a, 'b': b})
        self.assertEqual(graph.edges, {('a', 'b'): [a_b_1, a_b_2]})