"""Tests a MCPBrockFactory instance"""
import pytest


from nphard_generators import MCPBrockFactory
from nphard_generators.types import MCProblemSolution


class TestMCPBrockFactory:
    """Tests for the MCPBrockFactory."""

    @pytest.mark.flaky(reruns=3)
    @pytest.mark.parametrize("n, d, s, h", [
        (20, 0.4, 4, 1),
    ])
    def test_various_shapes(self, n, d, s, h):
        """Test some configurations for expected max_clique"""
        brock_problem = MCPBrockFactory.generate_instance(n, d, s, h)

        assert isinstance(brock_problem, MCProblemSolution)
        assert brock_problem.n_nodes == n, "n_nodes differs."
        assert brock_problem.n_max_clique == s, "n_max_clique differs."
        assert brock_problem.max_clique.size == s, "max_clique not size s"
        assert brock_problem.graph_density == pytest.approx(d, abs=0.05),"density incorrect"

        assert brock_problem.has_edge(brock_problem.max_clique[0], brock_problem.max_clique[1])
        assert brock_problem.has_edge(brock_problem.max_clique[1], brock_problem.max_clique[2])
