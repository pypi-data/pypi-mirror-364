"""Contains a class representing a hamiltonian-cycle-problem.

Typical usage example:

    problem = HCProblem(graph)
    problem.to_file(path, [])
"""
__all__ = [
    "HCProblem"
]

from nphard_generators.types.graph_problem import GraphProblem


class HCProblem(GraphProblem):
    """Represents a hamiltonian-cycle-problem with no solution.
    
    to_file(...) stores the problem in tsp format.
    """

    def to_file(self, path_to_file: str, comments: list[str] = None):
        super()._to_tsp_file(path_to_file, comments)
