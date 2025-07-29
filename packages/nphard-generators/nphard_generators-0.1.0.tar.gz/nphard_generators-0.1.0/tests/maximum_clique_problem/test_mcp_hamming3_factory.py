"""Tests a MCPHamming3Factory instance"""
import pytest


from nphard_generators import MCPHamming3Factory
from nphard_generators.types import MCProblemSimpleSolution


class TestMCPHamming3Factory:
    """Tests for the MCPHamming3Factory."""

    @pytest.mark.parametrize("n, n_max_clique_expected, edges", [
        (5, 2, [(3, 4)]),
    ])
    def test_various_shapes(self, n, n_max_clique_expected, edges):
        """Test some configurations for expected max_clique"""
        hamming_problem = MCPHamming3Factory.generate_instance(n)

        assert isinstance(hamming_problem, MCProblemSimpleSolution)
        assert hamming_problem.n_nodes == n, "n_nodes differs."
        assert hamming_problem.n_max_clique == n_max_clique_expected

        for (u,v) in edges:
            assert hamming_problem.has_edge(u, v)
