"""Generates a hamiltonian Hamiltonian-Cycle-Problem with a trivial approach.

A graph is always represented as a square (sparse) matrix.

Usage:
    problem = HCPSynH1Factory.generate_instance(...)
"""

__all__ = [
    "HCPSynH1Factory"
]


import random

import numpy as np

from nphard_generators.random_factory import RandomFactory
from nphard_generators.types.hamiltonian_cycle_problem.hc_problem_solution import HCProblemSolution

class HCPSynH1Factory(RandomFactory):
    """Generates hamilontian graphs for the hamiltonian-cycle-problem using a trivial approach.

    The generator first creates a closed circle to ensure hamiltonity.
    In a second step, random edges are added.

    Usage:

        For a hamiltonian graph with 20 nodes and density 0.5:
        HCPSynH1Factory.generateInstance(20, 0.5)
    """

    @staticmethod
    # pylint: disable=arguments-differ
    def generate_instance(n_nodes: int, density: float) -> HCProblemSolution:
        """Creates a hamiltonian graph using a trivial approach."""
        return HCPSynH1Factory(n_nodes, density).connect_graph().to_problem()

    def __init__(self, n_nodes, density):
        super().__init__(n_nodes, density)
        self._cycle_nodes = np.array(random.sample(range(0, self.n_nodes), self.n_nodes))

        # TODO: Density is now a bit higher due to the additional edges of the circle
        """Solution: Calculate n_edges missing -> select random nodes, check if ok and connect"""

    def to_problem(self) -> HCProblemSolution:
        """Creates a HCProblemSolution out of this factory."""
        return HCProblemSolution(self._get_final_graph(), self._cycle_nodes)

    def _connect_graph_logic(self):
        """Connects the graph using a trivial approach."""

        super()._connect_graph_logic()  # Connects the graph randomly

        for (i, _) in enumerate(self._cycle_nodes): # Connect cycle
            self._connect_edge(self._cycle_nodes[i-1], self._cycle_nodes[i])
