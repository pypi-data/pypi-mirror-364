"""Generates a Maximum-Clique-Problem using the brock algorithm.

A graph is always represented as a square (sparse) matrix.

Usage:
    problem = MCPBrockFactory.generate_instance(...)
"""

__all__ = [
    "MCPBrockFactory"
]


import random

import numpy as np
from scipy.optimize import bisect

from nphard_generators.graph_factory import (
    GraphFactory, assert_density_valid, assert_n_max_clique_valid
)
from nphard_generators.types.maximum_clique_problem.mc_problem_solution import MCProblemSolution

def assert_hiding_depth_valid(hiding_depth: int):
    """Raises ValueError if the given hiding_depth is invalid."""
    if not isinstance(hiding_depth, int):
        raise ValueError(f"Expecting hiding_depth to be an int. Found {type(hiding_depth)}")

    if hiding_depth < 0:
        raise ValueError(f"Expecting hiding_depth to be >=0. Is {hiding_depth}")

    if hiding_depth > 4:
        raise ValueError(f"Expecting hiding_depth to be <=4. Is {hiding_depth}")


class MCPBrockFactory(GraphFactory):
    """Generates graphs for the maximum-clique-problem using the brock algorithm.

    Implements the algorithm proposed by Brockington and Culberson (1994) for generating
    instances for the maximum-clique-problem by hiding a clique in a random graph.

    The algorithm constructs the graph using the maximum-independent-set problem
    and hides the implemented clique based on a given hiding depth.

    Usage:

        For a Brock graph with 20 nodes, density 0.5, clique size of 4 and hiding depth of 1:
        MCPBrockFactory.generateInstance(20, 0.5, 4, 1)

    References:
        Brockington, M., Culberson, J. C. (1994).
        Camouflaging independent sets in quasi-random graphs.
        *Cliques, coloring, and satisfiability, 26*, 75-88.
    """

    @staticmethod
    # pylint: disable=arguments-differ
    def generate_instance(
        n_nodes: int, density: float, n_max_clique: int, hiding_depth: int)-> MCProblemSolution:
        """Creates a MaxCliqueProblem using the brock algorithm."""
        return MCPBrockFactory(
            n_nodes, density, n_max_clique, hiding_depth).connect_graph().to_problem()

    def __init__(self, n_nodes: int, density: float, n_max_clique: int, hiding_depth: int):
        super().__init__(n_nodes)

        assert_density_valid(density)
        self._density_ind_set = 1-density

        assert_n_max_clique_valid(n_max_clique, n_nodes)
        self._n_max_clique = n_max_clique

        assert_hiding_depth_valid(hiding_depth)
        self._u = hiding_depth-1

        self._max_clique = np.random.choice(n_nodes, n_max_clique, replace=False)

    def to_problem(self) -> MCProblemSolution:
        """Creates a MCProblemSolution out of this factory."""
        return MCProblemSolution(self._get_final_graph_complement(), self._max_clique)

    def _connect_graph_logic(self):
        """Connects the graph using the brock algorithm."""

        outside_nodes = [v for v in range(0, self.n_nodes) if v not in self._max_clique]
        (p0, p1) = self._calculate_p0_p1(
            self.n_nodes, self._density_ind_set, self._n_max_clique, self._u)

        for outside_node in outside_nodes:

            for outside_node2 in outside_nodes:   # Add connections between outside nodes

                if outside_node2 <= outside_node:  # Check each connection only once
                    continue

                if random.random() < p0:
                    self._connect_edge(outside_node, outside_node2)

            d = int(round(self._n_max_clique * p1)) # Connect outside nodes to clique nodes
            while d > 0:
                while True:
                    clique_node = random.choice(self._max_clique)
                    if not self._has_edge(outside_node, clique_node):
                        self._connect_edge(outside_node, clique_node)
                        d -= 1
                        break

    def _calculate_p0_p1(self, n_nodes, density, n_max_clique, u):
        """Calculates the probability p0 for outside connections and p0 for out-to-in."""
        if u == -1:
            return (density, density)

        p1 = self._calculate_p1(n_nodes, density, n_max_clique, u)
        p0 = self._calculate_p0(n_nodes, n_max_clique, u, p1)
        return (p0, p1)

    def _calculate_p1(self, n_nodes, density, n_max_clique, u):
        """Calculates the probability p1 for connections from out to in nodes.
        
            u is the amount of correctly identified nodes.
            The original paper uses an i=u-1. For more clarity, this subtraction is done
            in the constructor so the classes uses directly u everywhere.
        """
        assert 0 <= u <= 3, f"u out of range 0 <= u <= 3. Is {u}."

        epsilon = 1e-12

        min_x = density
        max_x = (1.0 + u * density) / (1.0 + u)
        if u == 0:
            max_x = 0.99

        f_max = self._p1_function(max_x, density, n_nodes, n_max_clique, u)

        if abs(f_max) < epsilon:
            return max_x

        if f_max < 0:
            raise ValueError("Level of hiding and edge density yield a non-real solution.")

        # Use bisection to solve f(p1)=0
        p1 = bisect(
            self._p1_function, min_x, max_x,
            args=(density, n_nodes, n_max_clique, u), xtol=epsilon
        )

        return float(p1)

    def _calculate_p0(self, n, s, u, p1):
        """Calculates the probability p0 for outside connections.
        Requires p1 for calculation.
        """
        return p1 * ((n-s)*(1-p1)**u-(s-u)) / ((n-s)*(1-p1)**u-1)

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    def _p1_function(self, p1, p, n, s, u):
        """Represents f(p1)=...
        
        Goal is: find p1 such that f(p1)=0.
        Can be solved using a numerical approach.
        """
        return (p1-p)*(n-s)*(1-p1)**u - p*(s-u-1)
