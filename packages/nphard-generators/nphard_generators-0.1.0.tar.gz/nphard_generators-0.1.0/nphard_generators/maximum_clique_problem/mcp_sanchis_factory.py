"""Generates a Maximum-Clique-Problem using Sanchis graph construction.

A graph is always represented as a square (sparse) matrix.

Usage:
    problem = MCPSanchisFactory.generate_instance(...)
"""

__all__ = [
    "MCPSanchisFactory"
]


import random
import scipy.special as scp

import numpy as np
from nphard_generators.graph_factory import (
    GraphFactory, assert_density_valid, assert_n_max_clique_valid
)
from nphard_generators.types.maximum_clique_problem.mc_problem_solution import MCProblemSolution


class MCPSanchisFactory(GraphFactory):
    """Generates graphs for the maximum-clique-problem using the Sanchis algorithm.

    Implements the algorithm described by Hasselberg et al. (1993) for generating
    test cases for the minimum vertex cover problem and converting them to
    the maximum clique problem.

    The algorithm is based on an idea orginally proposed by Sanchis (1992) in
    the context of generating NP-hard problems.

    Usage:

        For a Sanchis graph with 20 nodes, density 0.4 and hidden maximum clique of size 4:
        MCPCSanchisFactory.generateInstance(20, 0.4, 4)

    References:
        Hasselberg, J., Pardalos, P. M., & Vairaktarakis, G. (1993).
        Test case generators and computational results for the maximum clique problem.
        *Journal of Global Optimization, 3*, 463-482.

        Sanchis, L. (1992).
        Test case construction for the vertex cover problem.
        In *DIMACS Series in Discrete Mathematics and Theoretical Computer Science, 15*
        (pp. 315-326). American Mathematical Society.
    """

    @staticmethod
    # pylint: disable=arguments-differ
    def generate_instance(n_nodes: int, density: float, n_max_clique: int) -> MCProblemSolution:
        """Creates a MaxCliqueProblem using the Sanchis generator."""
        return MCPSanchisFactory(n_nodes, density, n_max_clique).connect_graph().to_problem()

    def __init__(self, n_nodes: int, density: float, n_max_clique: int):
        super().__init__(n_nodes)

        assert_density_valid(density)
        self._density = density

        assert_n_max_clique_valid(n_max_clique, n_nodes)
        self._n_max_clique = n_max_clique

        self._n_edges = 0
        self._max_clique = self._calculate_max_clique()

    def to_problem(self) -> MCProblemSolution:
        """Creates a MCProblemSolution out of this factory."""
        return MCProblemSolution(self._get_final_graph_complement(), self._max_clique)

    def _connect_graph_logic(self):
        """Connects the graph according to the sanchis algorithm."""

        k = self._n_max_clique

        self._connect_cliques(k)
        self._connect_additional_edges(k)

    def _connect_cliques(self, k):
        """Connects the partitions to be a clique itself"""
        for vert1 in range(0, self.n_nodes-1):
            partition_of_1 = vert1 % k
            for vert2 in range(vert1+1, self.n_nodes):
                partition_of_2 = vert2 % k

                if partition_of_1 == partition_of_2:
                    self._connect_edge(vert1, vert2)
                    self._n_edges += 1

    def _connect_additional_edges(self, k):
        """Adds random edges from cover verticies to any other verticies."""
        _n_edges_mvc_should = scp.binom(self.n_nodes, 2) * (1 - self._density)
        _n_edges_mvc_max = scp.binom(self.n_nodes, 2) - scp.binom(self._n_max_clique, 2)

        while self._n_edges < min(_n_edges_mvc_should, _n_edges_mvc_max):
            vert1 = vert2 = None

            while vert1 == vert2 or self._has_edge(vert1, vert2):
                vert1 = random.randint(k, self.n_nodes-1)    # Choose a cover vertex
                vert2 = random.randint(0, self.n_nodes-1)    # Choose a random node

            self._connect_edge(vert1, vert2)
            self._n_edges += 1

    def _calculate_max_clique(self):
        """Calculates the max clique that is every node from 0, ..., k-1"""
        k = self._n_max_clique

        return np.array(list(range(0, k)))
