"""Generates a Maximum-Clique-Problem using the hamming distance.

A graph is always represented as a square (sparse) matrix.

Usage:
    problem = MCPHamming2Factory.generate_instance(...)
"""

__all__ = [
    "MCPHamming2Factory"
]


import numpy as np
from nphard_generators.maximum_clique_problem.mcp_hamming_factory import MCPHammingFactory
from nphard_generators.types.maximum_clique_problem.mc_problem_solution import MCProblemSolution


class MCPHamming2Factory(MCPHammingFactory):
    """Generates graphs for the maximum-clique-problem using the hamming distance.

    Implements the algorithm described by Hasselberg et al. (1993) for generating
    test cases using the hamming distance.

    Edges are always connect when they have a hamming distance of 2 (or more).
    The maximum clique is either all nodes with even count of 1s in binary representation
    or all nodes with an odd count.

    Usage:

        For a Hamming2 graph with 20 nodes:
        MCPHamming2Factory.generateInstance(20)

    References:
        Hasselberg, J., Pardalos, P. M., & Vairaktarakis, G. (1993).
        Test case generators and computational results for the maximum clique problem.
        *Journal of Global Optimization, 3*, 463-482.
    """

    @staticmethod
    # pylint: disable=arguments-differ
    def generate_instance(n_nodes: int) -> MCProblemSolution:
        """Creates a MaxCliqueProblem using the hamming distance."""
        return MCPHamming2Factory(n_nodes).connect_graph().to_problem()

    def __init__(self, n_nodes: int):
        super().__init__(n_nodes, 2)

        self._max_clique = self._calculate_max_clique()

    def to_problem(self) -> MCProblemSolution:
        """Creates a MCProblemSolution out of this factory."""
        return MCProblemSolution(self._get_final_graph(), self._max_clique)

    def _calculate_max_clique(self):
        """Calculates the max clique that is either the group
        that has an odd amount of 1s in its binary representation or
        the one that has an even amout."""
        odd_clique = []
        even_clique = []

        for node in range(self.n_nodes):
            if bin(node).count('1')%2==0:
                even_clique.append(node)
            else:
                odd_clique.append(node)

        if len(even_clique) <= 0:
            even_clique.append(0)

        if len(even_clique) >= len(odd_clique):
            return np.array(even_clique)

        return np.array(odd_clique)
