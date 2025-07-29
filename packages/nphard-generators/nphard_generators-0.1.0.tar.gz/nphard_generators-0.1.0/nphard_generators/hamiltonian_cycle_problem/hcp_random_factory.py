"""Contains a class to generate a random Hamiltonian-Cycle-Problem.

A graph is always represented as a square (sparse) matrix.

Usage:
    problem = HCPRandomFactory.generate_instance(...)
"""

__all__ = [
    "HCPRandomFactory"
]


from nphard_generators.random_factory import RandomFactory
from nphard_generators.types.hamiltonian_cycle_problem.hc_problem import HCProblem

class HCPRandomFactory(RandomFactory):
    """Factory for generating undirected, unweighted random Hamiltonian-Cycle-Problems.

    Usage:

        for a random graph with 20 nodes and a density of 0.1:
        HCPRandomFactory.generateInstance(20, 0.1) 
    """

    @staticmethod
    # pylint: disable=arguments-differ
    def generate_instance(n_nodes: int, density: float) -> HCProblem:
        """Creates a Hamiltonian-Cycle-Problem using a randomly connected graph."""
        return HCPRandomFactory(n_nodes, density).connect_graph().to_problem()

    def to_problem(self) -> HCProblem:
        """Creates a HCProblem out of this factory."""
        return HCProblem(self._get_final_graph())
