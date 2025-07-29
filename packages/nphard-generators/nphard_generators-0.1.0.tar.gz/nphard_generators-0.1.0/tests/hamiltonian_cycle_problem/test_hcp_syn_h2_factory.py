"""Tests a HCPSynH1Factory instance"""
import pytest

import numpy as np
import numpy.testing as npt

from nphard_generators import HCPSynH1Factory
from nphard_generators.types.graph_problem import calculate_max_edge_count_for_n_nodes
from nphard_generators.types.hamiltonian_cycle_problem.hc_problem_solution import HCProblemSolution


class TestHCPSynH1Factory:
    """Tests for the HCPSynH1Factory."""

    # rerun up to 3 times, since random sometimes creates higher / lower densities
    @pytest.mark.flaky(reruns=6)
    def test_basic_requirements(self):
        """Tests if a graph fullfills basic requirements.

        E.g. n_nodes, density, available_verticies correct.
        density may differ up to 5%.
        """
        n_nodes = 50
        density = 0.2

        synh1_problem = HCPSynH1Factory.generate_instance(n_nodes, density)

        verticies_should = np.array(list(range(0, n_nodes)))
        n_edges_should = calculate_max_edge_count_for_n_nodes(n_nodes) * density

        assert isinstance(synh1_problem, HCProblemSolution)
        assert synh1_problem.is_hamiltonian

        assert synh1_problem.n_nodes == n_nodes, "n_nodes incorrect"
        npt.assert_array_equal(
            synh1_problem.available_verticies, verticies_should, "available_verticies incorrect")

        assert synh1_problem.graph_density == pytest.approx(density, abs=0.16),"density incorrect"

        assert synh1_problem.n_edges == pytest.approx(
            n_edges_should, abs=n_edges_should*0.16),"n_edges incorrect"

        for (i, _) in enumerate(synh1_problem.cycle_nodes):  # Check if cycle is complete
            node_a = synh1_problem.cycle_nodes[i-1]
            node_b = synh1_problem.cycle_nodes[i]
            assert synh1_problem.has_edge(node_a, node_b)

    def test_invalid_density_raises_error(self):
        """Tests if a error is raised when a invalid density is given."""
        n = 20
        d = -0.1

        with pytest.raises(ValueError):
            HCPSynH1Factory.generate_instance(n, d)
