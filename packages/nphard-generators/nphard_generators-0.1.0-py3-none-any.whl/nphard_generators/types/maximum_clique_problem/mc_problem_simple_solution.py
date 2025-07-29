"""Contains a class representing a maximum-clique-problem with known maximum-clique size.

Typical usage example:

    problem = MCProblemSimpleSolution(graph, 4)
    problem.to_file(path, [])
"""
__all__ = [
    "MCProblemSimpleSolution"
]

from scipy.sparse import csr_array

from nphard_generators.types.maximum_clique_problem.mc_problem import MCProblem


class MCProblemSimpleSolution(MCProblem):
    """Represents a maximum-clique-problem with known maximum-clique size.
    
    to_file(...) stores the problem and clique size in mtx format.
    """

    def __init__(self, graph: csr_array, n_max_clique: int):
        super().__init__(graph)
        self._n_max_clique = n_max_clique

    @property
    def n_max_clique(self):
        """Size of maximum-clique of the instance."""
        return self._n_max_clique

    def to_file(self, path_to_file: str, comments: list[str] = None):

        n_max_clique_comment = f"n_max_clique: {self.n_max_clique}"

        super().to_file(path_to_file, [n_max_clique_comment] + (comments or []))
