from copy import deepcopy, copy
import logging
from unittest.mock import patch
from graphs.primitives import Graph
from graphs.random_contraction import run_random_contraction_algorithm, _get_random_edge, _merge_nodes
from graphs.test.test_primitives import GraphTestCase

logging.basicConfig(level=logging.DEBUG)
_log = logging.getLogger(__name__)


class TestRandomContraction(GraphTestCase):
    """Test the random contraction algorithm for finding minimum cuts."""
    @patch('graphs.random_contraction.random', autospec=True)
    def test_get_random_edge(self, m_random):
        """Test that the _get_random_edge helper function correctly selects from the full range of edges.
        
        TODO: double-edges.
        """
        self._setup_triangle_graph()

        random_edges = []
        for r in [0, 0.5, 0.9]:
            m_random.return_value = r
            random_edge = _get_random_edge(self.graph)
            _log.info('Got edge %s', random_edge)
            random_edges.append(random_edge)

        for edge in self.graph.edges:
            # In this case there are no parallel edges => only one edge in the edge list.
            self.assertTrue(edge in random_edges, "%s not found in %s" % (edge, random_edges))
            
    def test_merge_nodes(self):
        """Test that the _merge_nodes helper function correctly merges two nodes, and trims self-edges."""
        self._setup_triangle_graph()
        
        _merge_nodes(self.graph, self.node_a, self.node_b)
        
        self.assertEqual(len(self.graph.nodes), 2)
        self.assertEqual(len(self.graph.edges), 2)

    def test_noop(self):
        """Test the random contraction algorithm in the no-op case of two nodes."""
        self._setup_basic_graph()
        graph_before = copy(self.graph)

        run_random_contraction_algorithm(self.graph)

        self.assertEqual(self.graph, graph_before)

    def test_triangle_contraction(self):
        """Test the random contraction algorithm in the simple case of a triangle network."""
        self._setup_triangle_graph()

        min_edges = run_random_contraction_algorithm(self.graph)

        self.assertEqual(min_edges, 2)

    def test_grid_contraction(self):
        """Test the random contraction algorithm in the non-trivial case of a square grid."""
        self.graph = Graph()

        self.a = self.graph.add_node_by_label('a')
        self.b = self.graph.add_node_by_label('b')
        self.c = self.graph.add_node_by_label('c')
        self.d = self.graph.add_node_by_label('d')

        self.a_b = self.graph.add_edge_by_label('a', 'b')
        self.b_c = self.graph.add_edge_by_label('b', 'c')
        self.c_d = self.graph.add_edge_by_label('c', 'd')
        self.d_a = self.graph.add_edge_by_label('d', 'a')
        self.a_c = self.graph.add_edge_by_label('a', 'c')

        min_edges = run_random_contraction_algorithm(self.graph)

        self.assertEqual(min_edges, 2)
