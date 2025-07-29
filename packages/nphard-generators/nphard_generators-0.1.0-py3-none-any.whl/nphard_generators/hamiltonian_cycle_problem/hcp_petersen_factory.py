"""Generates a petersen graph as Hamiltonian-Cycle-Problem.

A graph is always represented as a square (sparse) matrix.

Usage:
    problem = HCPPetersenFactory.generate_instance(...)
"""

__all__ = [
    "HCPPetersenFactory"
]

from nphard_generators.graph_factory import GraphFactory
from nphard_generators.types.hamiltonian_cycle_problem.hc_problem_simple_solution import (
    HCProblemSimpleSolution
)
from nphard_generators.types.hamiltonian_cycle_problem.hc_problem_solution import HCProblemSolution

class HCPPetersenFactory(GraphFactory):
    """Generates petersen graphs for the hamiltonian-cycle-problem.

    The algorithm splits the n_nodes into two groups, the u's and the v's.
    Connections:
        1. Each u is connected in order
        2. Each u_i is connected to its corresponding v_i
        3. Each v_i is connected with v_i+k

    Careful: The algorithm uses a n which is n_nodes / 2.

    Usage:

        For a petersen graph with 20 nodes and k=2:
        HCPPetersenFactory.generateInstance(20, 2)

    References:
        Alspach, B. (1983).
        The classification or hamiltonian generalized Petersen graphs.
        *Journal of Combinatorial Theory, Series B, 34.3*, 293-312.
    """

    @staticmethod
    # pylint: disable=arguments-differ
    def generate_instance(n_nodes: int, k: int) -> HCProblemSolution:
        """Creates a petersen graph."""
        return HCPPetersenFactory(n_nodes, k).connect_graph().to_problem()

    def __init__(self, n_nodes, k):
        super().__init__(n_nodes)

        if n_nodes < 4:
            raise ValueError(f"Expecting n_nodes to be >=4. Is {n_nodes}")

        if n_nodes%2 != 0:
            raise ValueError(f"Expecting n_nodes a even number. Is {n_nodes}")

        self._n = n_nodes / 2

        if k < 1 or k > self._n-1:
            raise ValueError(f"Expecting k to be 1<=k<=n_nodes-1. Is {k}")

        self._n = int(n_nodes / 2)
        self._k = k

    def to_problem(self):
        """Creates a HCProblemSimpleSolution out of this factory."""
        is_hamiltonian = self._is_hamiltonian(self._n, self._k)
        return HCProblemSimpleSolution(self._get_final_graph(), is_hamiltonian)

    def _connect_graph_logic(self):
        """Connects the graph using the petersen algorithm."""

        for i in range(self._n):     # Connect each u (u_i -> u_i+1)
            u_0 = i
            u_1 = (i + 1) % self._n
            self._connect_edge(u_0, u_1)

            # Connect each v (v_i -> v_i+k)
            v_0 = i+self._n
            v_1 = ((i + self._k) % self._n) + self._n
            self._connect_edge(v_0, v_1)

            # Connect u -> v (u_i -> v_i)
            self._connect_edge(i, self._n+i)

    def _is_hamiltonian(self, n, k):
        """Returns, whether or not the given petersen configuration is hamiltonian"""
        if (n%6)==5 and k in (2, n-2, (n-1)/2, (n+1)/2):
            return False

        if (n%4)==0 and k==n/2 and n>=8:
            return False

        return True
