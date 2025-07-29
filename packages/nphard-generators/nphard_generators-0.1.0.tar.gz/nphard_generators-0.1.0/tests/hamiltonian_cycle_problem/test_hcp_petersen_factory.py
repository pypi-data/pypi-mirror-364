"""Tests a HCPPetersenFactory instance"""
import pytest

import numpy as np
import numpy.testing as npt

from nphard_generators.hamiltonian_cycle_problem.hcp_petersen_factory import HCPPetersenFactory
from nphard_generators.types.hamiltonian_cycle_problem.hc_problem_simple_solution import (
    HCProblemSimpleSolution
)


class TestHCPPetersenFactory:
    """Tests for the HCPPetersenFactory."""

    @pytest.mark.parametrize("n_nodes, k, is_hamiltonian_expected, edges", [
        (3*2, 2, True, [(0,1), (1,2), (0,2), (3,4), (4,5), (3,5), (0,3), (1,4), (2,5)]),
        (4*2, 3, True, [(0,1), (1,2), (2,3), (3,0), (0,4)]),
        (11*2, 9, False, [(0,1), (0,11), (11, 20)]),
        (5*2, 2, False, []),
    ])
    def test_basic_requirements(self, n_nodes, k, is_hamiltonian_expected, edges):
        """Tests if a graph fullfills basic requirements.
        """
        petersen_problem = HCPPetersenFactory.generate_instance(n_nodes, k)


        assert isinstance(petersen_problem, HCProblemSimpleSolution)
        assert petersen_problem.is_hamiltonian == is_hamiltonian_expected

        verticies_should = np.array(list(range(0, n_nodes)))
        assert petersen_problem.n_nodes == n_nodes, "n_nodes incorrect"
        npt.assert_array_equal(
            petersen_problem.available_verticies, verticies_should, "available_verticies incorrect")

        for (u,v) in edges:
            assert petersen_problem.has_edge(u, v)

    def test_invalid_k_raises_error(self):
        """Tests if a error is raised when a invalid k is given."""
        n = 4*2
        k = 5

        with pytest.raises(ValueError):
            HCPPetersenFactory.generate_instance(n, k)
