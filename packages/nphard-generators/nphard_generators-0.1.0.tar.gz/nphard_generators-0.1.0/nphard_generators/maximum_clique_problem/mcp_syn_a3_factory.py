"""Generates a Maximum-Clique-Problem using SynA3 graph construction.

A graph is always represented as a square (sparse) matrix.

Usage:
    problem = MCPSynA3Factory.generate_instance(...)
"""

__all__ = [
    "MCPSynA3Factory"
]

from math import log
import math

import numpy as np

from nphard_generators.random_factory import RandomFactory
from nphard_generators.types.maximum_clique_problem.mc_problem_solution import MCProblemSolution



class MCPSynA3Factory(RandomFactory):
    """Generates graphs for the maximum-clique-problem using the SynA3 algorithm.

    Usage:

        For a SynA3 graph with 20 nodes, density 0.4 and clique size overhead of 2:
        MCPSynA3Factory.generateInstance(20, 0.4, 2)

    Algorithm:

        - Background clique size for random graphs is calculated.
        - The graph is randomly connected using the given density.
        - A random max clique with an overhead size is implemented to the graph.

    References:
        Bollobás, B. (2001).
        Random graphs (2nd ed.).
        *Cambridge University Press*, 282-290
        https://www.cambridge.org/9780521809207
    """

    @staticmethod
    # pylint: disable=arguments-differ
    def generate_instance(n_nodes: int, density: float, max_clique_overhead: int):
        """Creates a MaxCliqueProblem using the SynA1 generator."""
        return MCPSynA3Factory(n_nodes, density, max_clique_overhead).connect_graph().to_problem()

    def __init__(self, n_nodes: int, density: float, max_clique_overhead: int):
        super().__init__(n_nodes, density)

        self._max_clique_overhead = max_clique_overhead

        _n_max_clique = self._calculate_background_clique_size(
            n_nodes, density
        ) + max_clique_overhead

        self._max_clique = np.random.choice(n_nodes, _n_max_clique, replace=False)

        # TODO: Density is now a bit higher due to the additional edges of the circle
        """Solution: Calculate n_edges missing -> select random nodes, check if ok and connect"""

    def to_problem(self):
        """Creates a MCProblemSolution out of this factory."""
        return MCProblemSolution(self._get_final_graph(), self._max_clique)

    def _connect_graph_logic(self):
        """Connects the graph according to synA3 algorithm.
        Connects the graph randomly and implements a clique.
        """
        super()._connect_graph_logic()
        self._connect_all_nodes(self._max_clique)   # Connect the implemented clique

    def _calculate_background_clique_size(self, n_nodes, density):
        """Every random graph has a high probability of a maximum clique of a given size."""
        b = 1/density
        return round(2*log(n_nodes, b) - 2*log(log(n_nodes, b),b) + 2*log((math.e / 2), b) + 1)
