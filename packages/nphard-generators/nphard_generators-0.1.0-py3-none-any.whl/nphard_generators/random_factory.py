"""Contains functions and a base class relevant to every random graph generator.

A graph is always represented as a square (sparse) matrix.

The module provides a basic RandomFactory class that can be inherited.
"""

__all__ = [
    "RandomFactory"
]


from abc import abstractmethod
import random

from nphard_generators.graph_factory import GraphFactory, assert_density_valid
from nphard_generators.types.graph_problem import GraphProblem


class RandomFactory(GraphFactory):
    """Abstract base class for undirected, unweighted random graph generation.

    Usage:
        Inherit and implement the logic for generating a
        specific random graph problem in a subclass.

        RandomFactoryX.generateInstance(20, 0.1) internally calls
        RandomFactoryX(20, 0.1).connect_graph().toProblem()
    """

    @staticmethod
    @abstractmethod
    # pylint: disable=arguments-differ
    def generate_instance(n_nodes: int, density: float) -> GraphProblem:
        """Creates a specific GraphProblem using a randomly connected graph.

        Creates the specific factory, connects the graph accordingly and
        returns the graph as specific problem instance.

        Must be overwritten by subclasses.

        Returns:
            A GraphProblem the specific RandomFactory adresses.
        """

    def __init__(self, n_nodes: int, density: float):
        super().__init__(n_nodes)

        assert_density_valid(density)
        self._density = density

    def _connect_graph_logic(self):
        """Connects a graph with a probability of density for each edge.
        
        Another approach would be to calculate the amount of edges to add and
        randomly connect edges until the amount is reached.
        Problem: Could potentially run very long for high densities or need much memory
        if speed up.
        Downside of this approach: Density may vary more on smaller graphs.

        If you need exact densities, create a generator using one of the other approaches.
        """
        for y in range(0, self.n_nodes):
            for x in range(y+1, self.n_nodes):
                if random.random() < self._density:
                    self._connect_edge(x,y)
