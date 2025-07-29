"""Generates a Maximum-Clique-Problem using the hamming distance.

A graph is always represented as a square (sparse) matrix.

Abstract class for specific hamming factories.
"""

__all__ = [
    "MCPHammingFactory"
]


from math import ceil, floor, log2

from nphard_generators.graph_factory import GraphFactory


class MCPHammingFactory(GraphFactory):
    """Generates graphs for the maximum-clique-problem using the hamming distance.

    Implements the algorithm described by Hasselberg et al. (1993) for generating
    test cases using the hamming distance.

    Serves as a base class for factories with a specific d

    Usage:

        For a Hamming2 graph with 20 nodes:
        MCPHamming2Factory.generateInstance(20)

    References:
        Hasselberg, J., Pardalos, P. M., & Vairaktarakis, G. (1993).
        Test case generators and computational results for the maximum clique problem.
        *Journal of Global Optimization, 3*, 463-482.
    """

    def __init__(self, n_nodes: int, hamming_distance: int):
        super().__init__(n_nodes)

        self._hamming_distance = hamming_distance

    def _connect_graph_logic(self):
        """Connects the graph using the hamming distance."""

        for vert1 in range(0, self.n_nodes-1):
            for vert2 in range(vert1+1, self.n_nodes):
                dist = self._calculate_hamming_distance(vert1, vert2)

                if dist >= self._hamming_distance:
                    self._connect_edge(vert1, vert2)

    def _calculate_hamming_distance(self, a: int, b: int):
        """Calculates the hamming distance of a and b for word_size bits"""
        word_size = ceil(log2(max(a, b)+1))   # +1 because counting starts with 0
        dist = 0

        for pos in range(0, word_size):
            if floor(a / 2**pos)%2 != floor(b/2**pos)%2:
                dist += 1

        return dist
