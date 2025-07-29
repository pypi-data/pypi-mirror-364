"""Tests a HCPSynH2Factory instance"""
import pytest

import numpy as np
import numpy.testing as npt

from nphard_generators import HCPSynH2Factory
from nphard_generators.types.graph_problem import calculate_max_edge_count_for_n_nodes
from nphard_generators.types.hamiltonian_cycle_problem.hc_problem_simple_solution import HCProblemSimpleSolution


class TestHCPSynH2Factory:
    """Tests for the HCPSynH2Factory."""

    # rerun up to 3 times, since random sometimes creates higher / lower densities
    @pytest.mark.flaky(reruns=3)
    def test_basic_requirements(self):
        """Tests if a graph fullfills basic requirements.

        E.g. n_nodes, density, available_verticies correct.
        density may differ up to 5%.
        """
        n_nodes = 50
        density = 0.2

        synh2_problem = HCPSynH2Factory.generate_instance(n_nodes, density)

        verticies_should = np.array(list(range(0, n_nodes)))
        n_edges_should = calculate_max_edge_count_for_n_nodes(n_nodes) * density

        assert isinstance(synh2_problem, HCProblemSimpleSolution)
        assert not synh2_problem.is_hamiltonian

        assert synh2_problem.n_nodes == n_nodes, "n_nodes incorrect"
        npt.assert_array_equal(
            synh2_problem.available_verticies, verticies_should, "available_verticies incorrect")

        assert synh2_problem.graph_density == pytest.approx(density, abs=0.10),"density incorrect"

        assert synh2_problem.n_edges == pytest.approx(
            n_edges_should, abs=n_edges_should*0.10),"n_edges incorrect"

    def test_invalid_density_raises_error(self):
        """Tests if a error is raised when a invalid density is given."""
        n = 20
        d = -0.1

        with pytest.raises(ValueError):
            HCPSynH2Factory.generate_instance(n, d)
