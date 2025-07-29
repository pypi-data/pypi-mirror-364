"""Contains a class representing a maximum-clique-problem.

Typical usage example:

    problem = MCProblem(graph)
    problem.to_file(path, [])
"""
__all__ = [
    "MCProblem"
]

from nphard_generators.types.graph_problem import GraphProblem


class MCProblem(GraphProblem):
    """Represents a maximum-clique-problem with no solution.
    
    to_file(...) stores the problem in mtx format.
    """

    def to_file(self, path_to_file: str, comments: list[str] = None):
        super()._to_mtx_file(path_to_file, comments)
