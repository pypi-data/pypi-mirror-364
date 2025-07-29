"""Generates a Maximum-Clique-Problem using CFat graph construction.

A graph is always represented as a square (sparse) matrix.

Usage:
    problem = MCPCFatFactory.generate_instance(...)
"""

__all__ = [
    "MCPCFatFactory"
]


from math import floor, log

import numpy as np
from nphard_generators.graph_factory import GraphFactory
from nphard_generators.types.maximum_clique_problem.mc_problem_solution import MCProblemSolution


class MCPCFatFactory(GraphFactory):
    """Generates graphs for the maximum-clique-problem using the CFat algorithm.

    Implements the algorithm described by Hasselberg et al. (1993) for generating
    test cases for the maximum clique problem.

    The algorithm is based on an idea orginally proposed by Berman und Pelc (1990) in
    the context of multiprocessor fault detection.

    Usage:

        For a CFat graph with 20 nodes and c-value of 3:
        MCPCFatFactory.generateInstance(20, 3)

    References:
        Hasselberg, J., Pardalos, P. M., & Vairaktarakis, G. (1993).
        Test case generators and computational results for the maximum clique problem.
        *Journal of Global Optimization, 3*, 463-482.

        Berman, P., & Pelc, A. (1990).
        Distributed Fault Diagnosis for Multiprocessor Systems.
        In *Proceedings of the 20th Annual International Symposium on Fault-Tolerant Computing*
        (pp. 340-346).
    """

    @staticmethod
    # pylint: disable=arguments-differ
    def generate_instance(n_nodes: int, c: float) -> MCProblemSolution:
        """Creates a MaxCliqueProblem using the CFat generator."""
        return MCPCFatFactory(n_nodes, c).connect_graph().to_problem()

    def __init__(self, n_nodes: int, c: float):
        super().__init__(n_nodes)

        self._c = c
        self._max_clique = self._calculate_max_clique()

    def to_problem(self) -> MCProblemSolution:
        """Creates a MCProblemSolution out of this factory."""
        return MCProblemSolution(self._get_final_graph(), self._max_clique)

    def _connect_graph_logic(self):
        """Connects the graph according to the cfat algorithm.
        The graph is split into k partitions.
        Two nodes are connected, if they are in the same or adjacent partitions.
        """

        k = self._calculate_k(self._c)

        for vert1 in range(0, self.n_nodes-1):
            partition_of_1 = vert1 % k
            for vert2 in range(vert1+1, self.n_nodes):
                partition_of_2 = vert2 % k

                partition_distance = abs(partition_of_1 - partition_of_2)

                if partition_distance <= 1 or partition_distance==k-1:
                    self._connect_edge(vert1, vert2)

    def _calculate_max_clique(self):
        """Calculates the max clique based on the n_nodes and k value"""

        k = self._calculate_k(self._c)

        # At most 3 partitions -> fully connected
        if k<=3:
            return np.array(list(range(self.n_nodes)))

        # Max clique is in partition0 and partition1
        max_clique = []
        for i in range(self.n_nodes):
            if i%k==0 or i%k==1:
                max_clique.append(i)

        return np.array(max_clique)


    def _calculate_k(self, c: float):
        k = floor(self.n_nodes / (c*log(self.n_nodes)))
        return max(k, 1)
