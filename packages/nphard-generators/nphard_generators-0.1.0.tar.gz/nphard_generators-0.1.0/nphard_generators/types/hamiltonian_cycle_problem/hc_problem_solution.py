"""Contains a class representing a hamiltonian-cycle-problem with a solution.

Typical usage example:

    problem = HCProblemSolution(graph, True, [1,2,3,4])
    problem.to_file(path, [])
"""
__all__ = [
    "HCProblemSolution"
]

import numpy as np
from scipy.sparse import csr_array

from nphard_generators.types.graph_problem import (
    assert_is_np_int_array, assert_is_subset, get_np_array_as_string
)
from nphard_generators.types.hamiltonian_cycle_problem.hc_problem_simple_solution import (
    HCProblemSimpleSolution
)



class HCProblemSolution(HCProblemSimpleSolution):
    """Represents a hamiltonian-cycle-problem with known cycle nodes.
    
    to_file(...) stores the problem and cycle nodes in mtx format.
    """

    def __init__(self, graph: csr_array, cycle_nodes: np.ndarray):
        super().__init__(graph, cycle_nodes.size > 0)

        assert_is_np_int_array(cycle_nodes)
        assert_is_subset(cycle_nodes, self.available_verticies)

        self._cycle_nodes = cycle_nodes

    @property
    def cycle_nodes(self):
        """Cycle-nodes that form the hamiltonian cycle.
        Represented as numpy array of nodes.
        E.g.: cycle_nodes = [0,1,2]"""
        return self._cycle_nodes

    def to_file(self, path_to_file: str, comments: list[str] = None):

        cycle_nodes_comment = f"cycle_nodes: {get_np_array_as_string(self.cycle_nodes)}"

        super().to_file(path_to_file, [cycle_nodes_comment] + (comments or []))
