"""Contains a class representing a hamiltonian-cycle-problem with a simple solution.

Typical usage example:

    problem = HCProblemSimpleSolution(graph, True)
    problem.to_file(path, [])
"""
__all__ = [
    "HCProblemSimpleSolution"
]

from scipy.sparse import csr_array

from nphard_generators.types.hamiltonian_cycle_problem.hc_problem import HCProblem


class HCProblemSimpleSolution(HCProblem):
    """Represents a hamiltonian-cycle-problem with a simple solution.
    
    to_file(...) stores the problem and solution in tsp format.
    """

    def __init__(self, graph: csr_array, is_hamiltonian: bool):
        super().__init__(graph)
        self._is_hamiltonian = is_hamiltonian

    @property
    def is_hamiltonian(self):
        """Is this instance hamiltonian."""
        return self._is_hamiltonian

    def to_file(self, path_to_file: str, comments: list[str] = None):

        is_hamiltonian_comment = f"is_hamiltonian_should={self.is_hamiltonian}"

        super().to_file(path_to_file, [is_hamiltonian_comment] + (comments or []))
