"""Contains functions and a base class relevant to every graph generator.

A graph is always represented as a square (sparse) matrix.

The module provides a basic GraphFactory class that can be inherited.
"""

__all__ = [
    "GraphFactory",
    "assert_density_valid",
    "assert_n_max_clique_valid"
]

from abc import ABC, abstractmethod
from typing import Self

from scipy.sparse import lil_matrix, csr_array
import numpy as np

from nphard_generators.types.graph_problem import GraphProblem


def assert_density_valid(density: float):
    """Raises ValueError if the given density is invalid."""
    if not isinstance(density, float):
        raise ValueError(f"Expecting density to be a float. Found {type(density)}")

    if density < 0.0:
        raise ValueError(f"Expecting density to be >=0.0. Is {density}")

    if density > 1.0:
        raise ValueError(f"Expecting density to be <=1.0. Is {density}")

def assert_n_nodes_valid(n_nodes: int):
    """Raises ValueError if the given n_nodes is invalid."""
    if not isinstance(n_nodes, int):
        raise ValueError(f"Expecting n_nodes to be an int. Found {type(n_nodes)}")

    if n_nodes < 1:
        raise ValueError(f"Expecting n_nodes to be >=1. Is {n_nodes}")

def assert_n_max_clique_valid(n_max_clique: int, n_nodes: int):
    """Raises ValueError if the given n_max_clique is invalid."""
    if not isinstance(n_max_clique, int):
        raise ValueError(f"Expecting n_max_clique to be a int. Found {type(n_max_clique)}")

    if n_max_clique < 0:
        raise ValueError(f"Expecting n_max_clique to be >=0. Is {n_max_clique}")

    if n_max_clique > n_nodes:
        raise ValueError(f"Expecting n_max_clique to be <=n_nodes. Is {n_max_clique}")


class GraphFactory(ABC):
    """Abstract base class for undirected, unweighted graph generation.

    Usage:
        Inherit and implement the logic for generating a specific graph in a subclass.

        GraphFactoryX.generateInstance(20, 0.1) internally calls
        GraphFactoryX(20, 0.1).connect_graph().toProblem()

    Attributes:
        graph_editable: Graph in lil_matrix format for constructing.
        n_nodes: Number of nodes of the graph.
    """

    @staticmethod
    @abstractmethod
    def generate_instance(n_nodes: int, *args, **kwargs) -> GraphProblem:
        """Creates a specific GraphProblem using the given factory's logic.

        Creates the specific factory, connects the graph accordingly and
        returns the graph as specific problem instance.

        Must be overwritten by subclasses.

        Returns:
            A GraphProblem the specific GraphFactory adresses.
        """

    def __init__(self, n_nodes: int):

        assert_n_nodes_valid(n_nodes)

        self._n_nodes = n_nodes
        self._graph_editable = lil_matrix((n_nodes, n_nodes), dtype=bool)

    @property
    def n_nodes(self):
        """The graph's node count."""
        return self._n_nodes

    @property
    def graph_editable(self):
        """The editable graph."""
        return self._graph_editable

    @abstractmethod
    def to_problem(self) -> GraphProblem:
        """Creates a GraphProblem out of this factory.

        Converts the editable graph to a more efficient representation for calculations
        and wraps it into a type of GraphProblem.
        Subclasses need to specify which subclass of GraphProblem they return.
        """

    def connect_graph(self) -> Self:
        """Calls the factory's graph connecting logic.

        Implementing a factory's connection logic should be done
        by overriding the _connect_graph_logic method.

        Returns:
            A reference to the factory itself to enable chaining.
            E.g: GraphFactoryX().connect_graph().to_problem()
        """
        self._connect_graph_logic()
        return self

    @abstractmethod
    def _connect_graph_logic(self):
        """Connects the graph according to the factory's logic.

        This method should be overriden by subclasses implementing their own logic.
        """

    def _get_final_graph(self) -> csr_array:
        """Creates a more calculation efficient csr_array from the editable graph"""
        return csr_array(self.graph_editable)

    def _get_final_graph_complement(self) -> csr_array:
        """Creates a more calculation efficient csr_array from the editable graph's complement"""
        final_graph = self._get_final_graph()

        all_edges = csr_array(np.ones((self.n_nodes, self.n_nodes), dtype=bool))
        all_edges.setdiag(0)

        # XOR: 1 where only one of A or all_edges has an edge -> complement
        complement = all_edges - final_graph
        complement.eliminate_zeros()
        return complement

    def _connect_edge(self, node_a: int, node_b: int):
        self.graph_editable[node_a,node_b] = True
        self.graph_editable[node_b,node_a] = True

    def _remove_edge(self, node_a: int, node_b: int):
        self.graph_editable[node_a,node_b] = False
        self.graph_editable[node_b,node_a] = False

    def _has_edge(self, node_a: int, node_b: int):
        return self.graph_editable[node_a,node_b]

    def _connect_all_nodes(self, nodes: np.ndarray):
        """Connects all given nodes to each other."""

        if not isinstance(nodes, np.ndarray) or not np.issubdtype(nodes.dtype, np.integer):
            raise TypeError("Input must be a NumPy array of integers.")

        for node_a in nodes:    # Connect all edges in the nodes list
            for node_b in nodes:
                if node_a != node_b:
                    self._connect_edge(node_a, node_b)
