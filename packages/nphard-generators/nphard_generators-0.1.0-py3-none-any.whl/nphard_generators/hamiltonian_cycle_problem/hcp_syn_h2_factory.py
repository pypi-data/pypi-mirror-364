"""Generates a non-hamiltonian Hamiltonian-Cycle-Problem with a trivial approach.

A graph is always represented as a square (sparse) matrix.

Usage:
    problem = HCPSynH2Factory.generate_instance(...)
"""

__all__ = [
    "HCPSynH2Factory"
]


import random

from nphard_generators.graph_factory import GraphFactory, assert_density_valid
from nphard_generators.types.hamiltonian_cycle_problem.hc_problem_simple_solution import (
    HCProblemSimpleSolution
)
from nphard_generators.types.hamiltonian_cycle_problem.hc_problem_solution import HCProblemSolution

class HCPSynH2Factory(GraphFactory):
    """Generates non-hamilontian graphs for the hamiltonian-cycle-problem using a trivial approach.

    The generator first inserts a bottleneck-like structure to ensure non-hamiltonity.
    In a second step, random edges are added.

    Usage:

        For a non-hamiltonian graph with 20 nodes and density 0.5:
        HCPSynH2Factory.generateInstance(20, 0.5)
    """

    @staticmethod
    # pylint: disable=arguments-differ
    def generate_instance(n_nodes: int, density: float) -> HCProblemSimpleSolution:
        """Creates a hamiltonian graph using a trivial approach."""
        return HCPSynH2Factory(n_nodes, density).connect_graph().to_problem()

    def __init__(self, n_nodes, density):
        super().__init__(n_nodes)

        assert_density_valid(density)
        self._density = density

        assert n_nodes >=7, f"Structure requires at least 7 nodes. Is {n_nodes}."

        # TODO: Density is now a bit higher due to the additional edges of the circle
        # Solution: Calculate n_edges missing -> select random nodes, check if ok and connect

    def to_problem(self) -> HCProblemSolution:
        """Creates a HCProblemSolution out of this factory."""
        return HCProblemSimpleSolution(self._get_final_graph(), False)

    def _connect_graph_logic(self):
        """Connects the graph using a trivial approach."""

        blocked_nodes = self._create_and_connect_bottle_neck()

        # Connect graph randomly
        for x in range(0, self.n_nodes):

            if x in blocked_nodes:
                continue

            for y in range(x+1, self.n_nodes):

                if y in blocked_nodes:
                    continue

                if random.random() < self._density:
                    self._connect_edge(x,y)

    def _create_and_connect_bottle_neck(self):
        """Creates and connects the bottle-neck structure-. Returns the blocked nodes."""
        nodes = random.sample(list(range(0, self.n_nodes)), 7)
        bottle_neck = nodes[0]
        pairs = [tuple(nodes[i:i+2]) for i in range(1, len(nodes), 2)]

        blocked_nodes = []  # Shoulders, are hiddin to the outside

        for shoulder, bottom in pairs:
            self._connect_edge(bottle_neck, shoulder)
            self._connect_edge(shoulder, bottom)
            blocked_nodes.append(shoulder)

        return blocked_nodes
