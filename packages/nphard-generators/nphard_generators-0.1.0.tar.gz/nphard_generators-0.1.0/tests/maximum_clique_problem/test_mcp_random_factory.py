"""Tests a MCPRandomFactory instance"""
import pytest

import numpy as np
import numpy.testing as npt

from nphard_generators import MCPRandomFactory
from nphard_generators.types import MCProblem
from nphard_generators.types.graph_problem import calculate_max_edge_count_for_n_nodes


class TestMCPRandomFactory:
    """Tests for the MCPRandomFactory."""

    # rerun up to 3 times, since random sometimes creates higher / lower densities
    @pytest.mark.flaky(reruns=3)
    def test_basic_requirements(self):
        """Tests if a graph fullfills basic requirements.

        E.g. n_nodes, density, available_verticies, n_edges correct.
        n_edges and density may differ up to 5%.
        """
        n_nodes = 50
        density = 0.2

        mcp_random = MCPRandomFactory.generate_instance(n_nodes, density)

        verticies_should = np.array(list(range(0, n_nodes)))
        n_edges_should = calculate_max_edge_count_for_n_nodes(n_nodes) * density

        assert isinstance(mcp_random, MCProblem)

        assert mcp_random.n_nodes == n_nodes, "n_nodes incorrect"
        npt.assert_array_equal(
            mcp_random.available_verticies, verticies_should, "available_verticies incorrect")

        assert mcp_random.graph_density == pytest.approx(density, abs=0.05),"density incorrect"

        assert mcp_random.n_edges == pytest.approx(
            n_edges_should, abs=n_edges_should*0.1),"n_edges incorrect"

    def test_invalid_density_raises_error(self):
        """Tests if a error is raised when a invalid density is given."""
        n = 20
        d = -0.1

        with pytest.raises(ValueError):
            MCPRandomFactory.generate_instance(n, d)
