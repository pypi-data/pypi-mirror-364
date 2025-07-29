"""Tests a MCPSanchisFactory instance"""
import pytest

import numpy as np
import numpy.testing as npt


from nphard_generators import MCPSanchisFactory
from nphard_generators.types import MCProblemSolution


class TestMCPSanchisFactory:
    """Tests for the MCPSanchisFactory."""

    @pytest.mark.parametrize("n, d, x, max_clique_expected, edges", [
        (4, 0.5, 2, np.array([0,1]), [(0,1)]),
        (10, 0.5, 3, np.array([0,1,2]), [(0,1), (1,2)]),
    ])
    def test_various_shapes(self, n, d, x, max_clique_expected, edges):
        """Test some configurations for expected max_clique"""
        sanchis_problem = MCPSanchisFactory.generate_instance(n, d, x)

        assert isinstance(sanchis_problem, MCProblemSolution)
        assert sanchis_problem.n_nodes == n, "n_nodes differs."
        assert sanchis_problem.graph_density == pytest.approx(d, abs=0.05), "density incorrect"

        npt.assert_array_equal(
            sanchis_problem.max_clique, max_clique_expected, "max_clique differs from expected."
        )

        for (u,v) in edges:
            assert sanchis_problem.has_edge(u, v)
