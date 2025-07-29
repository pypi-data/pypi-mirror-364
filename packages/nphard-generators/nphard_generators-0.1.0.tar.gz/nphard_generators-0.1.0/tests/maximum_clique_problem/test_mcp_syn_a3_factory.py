"""Tests a MCPSynA3Factory instance"""
import pytest


from nphard_generators import MCPSynA3Factory
from nphard_generators.types import MCProblemSolution


class TestMCPSynA3Factory:
    """Tests for the MCPSynA3Factory."""

    @pytest.mark.flaky(reruns=3)
    @pytest.mark.parametrize("n_nodes, density", [
        (20, 0.4),
    ])
    def test_various_shapes(self, n_nodes, density):
        """Test some configurations for expected max_clique"""
        syn_a3_problem = MCPSynA3Factory.generate_instance(n_nodes, density, 2)

        assert isinstance(syn_a3_problem, MCProblemSolution)
        assert syn_a3_problem.n_nodes == n_nodes, "n_nodes differs."
        assert syn_a3_problem.graph_density == pytest.approx(density, abs=0.15),"density incorrect"

        assert syn_a3_problem.has_edge(syn_a3_problem.max_clique[0], syn_a3_problem.max_clique[1])
        assert syn_a3_problem.has_edge(syn_a3_problem.max_clique[1], syn_a3_problem.max_clique[2])
