"""Generates a Maximum-Clique-Problem using SynA1 graph construction.

A graph is always represented as a square (sparse) matrix.

Usage:
    problem = MCPSynA1Factory.generate_instance(...)
"""

__all__ = [
    "MCPSynA1Factory"
]

import random

import numpy as np
import scipy.special as scp

from nphard_generators.graph_factory import (
    GraphFactory, assert_density_valid, assert_n_max_clique_valid
)
from nphard_generators.types.graph_problem import calculate_max_edge_count_for_n_nodes
from nphard_generators.types.maximum_clique_problem.mc_problem_solution import MCProblemSolution



class MCPSynA1Factory(GraphFactory):
    """Generates graphs for the maximum-clique-problem using the SynA1 algorithm.

    Algorithm:

        - A random max clique is generated with clique_size nodes.
        - Every node not in max_clique is allowed to have clique_size - 1 edges.
        This ensures that no bigger clique is build.
        Connection is done randomly until the given density is reached or
        no more connections are possible.
    """

    @staticmethod
    # pylint: disable=arguments-differ
    def generate_instance(n_nodes: int, density: float, n_max_clique: int) -> MCProblemSolution:
        """Creates a MaxCliqueProblem using the SynA1 generator."""
        return MCPSynA1Factory(n_nodes, density, n_max_clique).connect_graph().to_problem()

    def __init__(self, n_nodes: int, density: float, n_max_clique: int):
        super().__init__(n_nodes)

        assert_density_valid(density)
        self._density = density

        assert_n_max_clique_valid(n_max_clique, n_nodes)
        self._n_max_clique = n_max_clique

        # Generates a random max_clique
        self._max_clique = np.random.choice(n_nodes, n_max_clique, replace=False)

    def to_problem(self) -> MCProblemSolution:
        """Creates a MCProblemSolution out of this factory."""
        return MCProblemSolution(self._get_final_graph(), self._max_clique)

    def _connect_graph_logic(self):
        """Connects the graph according to synA1 algorithm.
        Two nodes are connected, if they are in the same or adjacent partitions.
        """
        self._connect_all_nodes(self._max_clique)

        n_edges_max = calculate_max_edge_count_for_n_nodes(self._n_nodes)
        n_edges_clique = scp.binom(self._n_max_clique, 2)
        n_additional_edges = self._density * n_edges_max - n_edges_clique

        self._connect_not_clique(n_additional_edges)

    def _connect_not_clique(self, max_additional_edges):
        """Connects all nodes not in the clique."""

        not_clique = [person for person in range(self.n_nodes) if person not in self._max_clique]
        n_added_edges = 0

        for current_node in not_clique:
            possible_others = list(range(self.n_nodes))
            possible_others.remove(current_node)

            # Count already existing edges for current_node
            n_connections = 0
            for i in range(self.n_nodes):

                if i != current_node and self.graph_editable[current_node,i] is True:
                    n_connections += 1
                    possible_others.remove(i)

            # Connect current_node to other nodes ensuring at most n_max_clique-1 connections
            for _ in range(self._n_max_clique - 1 - n_connections):

                if n_added_edges >= max_additional_edges:
                    return

                if len(possible_others) <= 0:
                    continue

                random_other_node = random.choice(possible_others)
                self._connect_edge(current_node, random_other_node)
                possible_others.remove(random_other_node)
                n_added_edges += 1
