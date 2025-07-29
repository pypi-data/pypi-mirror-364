"""Generates a Maximum-Clique-Problem using the hamming distance.

A graph is always represented as a square (sparse) matrix.

Usage:
    problem = MCPHamming3Factory.generate_instance(...)
"""

__all__ = [
    "MCPHamming3Factory"
]


from math import floor
from nphard_generators.maximum_clique_problem.mcp_hamming_factory import MCPHammingFactory
from nphard_generators.types.maximum_clique_problem.mc_problem_simple_solution import (
    MCProblemSimpleSolution
)


class MCPHamming3Factory(MCPHammingFactory):
    """Generates graphs for the maximum-clique-problem using the hamming distance.

    Implements the algorithm described by Hasselberg et al. (1993) for generating
    test cases using the hamming distance.

    Edges are always connect when they have a hamming distance of 3 (or more).
    It is unclear, if the exact max clique can be determined, but the size is calculated.

    Usage:

        For a Hamming3 graph with 20 nodes:
        MCPHamming3Factory.generateInstance(20)

    References:
        Hasselberg, J., Pardalos, P. M., & Vairaktarakis, G. (1993).
        Test case generators and computational results for the maximum clique problem.
        *Journal of Global Optimization, 3*, 463-482.
    """

    @staticmethod
    # pylint: disable=arguments-differ
    def generate_instance(n_nodes: int):
        """Creates a MaxCliqueProblem using the hamming distance."""
        return MCPHamming3Factory(n_nodes).connect_graph().to_problem()

    def __init__(self, n_nodes: int):
        super().__init__(n_nodes, 3)

        self._n_max_clique = self._calculate_n_max_clique()

    def to_problem(self) -> MCProblemSimpleSolution:
        """Creates a MCProblemSolution out of this factory."""
        return MCProblemSimpleSolution(self._get_final_graph(), self._n_max_clique)

    def _calculate_n_max_clique(self):
        """Calculates the size of the max clique.
        
        Formula is extracted from empirical evaluations."""
        if self.n_nodes < 5:
            return self.n_nodes

        return 2*(floor((self.n_nodes-5)/16)+1)+floor(((self.n_nodes-5)%16)/12)
