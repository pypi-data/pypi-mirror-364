"""Tests a MCPSynA1Factory instance"""
import pytest

from nphard_generators import MCPSynA1Factory
from nphard_generators.types import MCProblemSolution


class TestMCPSynA1Factory:
    """Tests for the MCPSynA1Factory."""

    @pytest.mark.parametrize("n, d, n_max_clique", [
        (70, 0.15, 15),
        (100, 0.2, 20),
    ])
    def test_various_shapes(self, n, d, n_max_clique):
        """Test some configurations for expected max_clique"""

        syna1_problem = MCPSynA1Factory.generate_instance(n, d, n_max_clique)

        assert isinstance(syna1_problem, MCProblemSolution)
        assert syna1_problem.n_nodes == n, "n_nodes differs."
        assert syna1_problem.graph_density == pytest.approx(d, abs=0.05), "density incorrect"
        assert syna1_problem.n_max_clique == n_max_clique, "n_max_clique incorrect"

        # TODO: Add test to check if edges of max_clique are set
        # for syna1_problem.max_clique


    def test_invalid_density_raises_error(self):
        """Tests if a error is raised when a invalid density is given."""
        n = 20
        d = -0.1
        n_max_clique = 4

        with pytest.raises(ValueError):
            MCPSynA1Factory.generate_instance(n, d, n_max_clique)
