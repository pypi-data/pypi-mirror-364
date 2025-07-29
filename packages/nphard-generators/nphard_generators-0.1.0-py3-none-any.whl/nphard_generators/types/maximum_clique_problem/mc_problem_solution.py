"""Contains a class representing a maximum-clique-problem with known maximum-clique.

Typical usage example:

    problem = MCProblemSolution(graph, [0,1,2]) # Maximum-clique are nodes 0,1 and 2
    problem.to_file(path, [])
"""

__all__ = [
    "MCProblemSolution"
]

import numpy as np
from scipy.sparse import csr_array

from nphard_generators.types.graph_problem import (
    assert_is_np_int_array, assert_is_subset, get_np_array_as_string
)
from nphard_generators.types.maximum_clique_problem.mc_problem_simple_solution import (
    MCProblemSimpleSolution
)


class MCProblemSolution(MCProblemSimpleSolution):
    """Represents a maximum-clique-problem with known maximum-clique.
    
    to_file(...) stores the problem and maximum-clique in mtx format.
    """

    def __init__(self, graph: csr_array, max_clique: np.ndarray):
        super().__init__(graph, max_clique.size)

        assert_is_np_int_array(max_clique)
        assert_is_subset(max_clique, self.available_verticies)

        self._max_clique = max_clique

    @property
    def max_clique(self):
        """Maximum-clique of the instance.
        Represented as numpy array of nodes.
        E.g.: max_clique = [0,1,2]"""
        return self._max_clique

    def to_file(self, path_to_file: str, comments: list[str] = None):

        max_clique_comment = f"max_clique: {get_np_array_as_string(self.max_clique)}"

        super().to_file(path_to_file, [max_clique_comment] + (comments or []))
