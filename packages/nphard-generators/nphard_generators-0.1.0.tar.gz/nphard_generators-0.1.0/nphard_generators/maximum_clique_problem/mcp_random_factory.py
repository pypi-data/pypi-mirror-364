"""Contains a class to generate a random Maximum-Clique-Problem.

A graph is always represented as a square (sparse) matrix.

Usage:
    `problem = MCPRandomFactory.generate_instance(...)`
"""

__all__ = [
    "MCPRandomFactory"
]


from nphard_generators.random_factory import RandomFactory
from nphard_generators.types.maximum_clique_problem.mc_problem import MCProblem


class MCPRandomFactory(RandomFactory):
    """Factory for generating undirected, unweighted random Maximum-Clique-Problems.

    Usage:

        for a random graph with 20 nodes and a density of 0.1:
        `MCPRandomFactory.generateInstance(20, 0.1)`
    """

    @staticmethod
    # pylint: disable=arguments-differ
    def generate_instance(n_nodes: int, density: float) -> MCProblem:
        """Creates a MaxCliqueProblem using a randomly connected graph."""
        return MCPRandomFactory(n_nodes, density).connect_graph().to_problem()

    def to_problem(self) -> MCProblem:
        """Creates a MCProblem out of this factory."""
        return MCProblem(self._get_final_graph())
