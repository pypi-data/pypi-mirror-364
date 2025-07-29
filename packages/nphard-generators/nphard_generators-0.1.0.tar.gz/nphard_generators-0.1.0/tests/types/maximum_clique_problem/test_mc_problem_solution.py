"""Tests the mc_problem_solution module"""
import tempfile
from pathlib import Path

import pytest

import numpy as np
import numpy.testing as npt
from scipy.sparse import csr_array

from nphard_generators.types import MCProblemSolution
from nphard_generators.types.graph_problem import (
    assert_is_np_int_array, assert_is_subset, get_np_array_as_string, get_np_array_incremented
)


class TestAssertIsNPIntArray:
    """Tests for assert_is_np_int_array method"""

    def test_correct_array(self):
        """Tests with a correct numpy int 1D array"""
        arr0 = np.array([], dtype=int)
        arr1 = np.array([0, 1, 2])

        assert_is_np_int_array(arr0)
        assert_is_np_int_array(arr1)

    def test_python_list(self):
        """Tests with a simply python list. Expect error."""
        arr0 = [1,2,3]
        with pytest.raises(ValueError):
            assert_is_np_int_array(arr0)

    def test_numpy_float_array(self):
        """Tests with a float numpy array. Expect error."""
        arr0 = np.array([0.0, 1.0, 2.1])
        with pytest.raises(ValueError):
            assert_is_np_int_array(arr0)

    def test_numpy_two_dimensional_array(self):
        """Tests with a int 2D numpy array. Expect error."""
        arr0 = np.array([[0.0], [1.0], [2.1]])
        with pytest.raises(ValueError):
            assert_is_np_int_array(arr0)


class TestAssertIsSubset:
    """Tests for assert_is_subset method"""

    @pytest.mark.parametrize("superset, subset", [
        (np.array([], dtype=int), np.array([], dtype=int)),
        (np.array([1,2]), np.array([], dtype=int)),
        (np.array([1,2]), np.array([1])),
        (np.array([1,2,3]), np.array([1,2,3])),
    ])
    def test_various_correct_subsets(self, superset, subset):
        """Tests with a correct subset"""
        print(subset.dtype)
        assert_is_subset(subset, superset)

    def test_incorrect_subset(self):
        """Tests with an incorrect subset. Expect error."""
        subset = np.array([1,2,3])
        superset = np.array([1,2])
        with pytest.raises(ValueError):
            assert_is_subset(subset, superset)


class TestGetNPArrayAsString:
    """Tests for get_np_array_as_string method"""

    @pytest.mark.parametrize("arr_src, str_expected", [
        (np.array([]), "[]"),
        (np.array([1]), "[1]"),
        (np.array([1,2,3,-4]), "[1,2,3,-4]"),
    ])
    def test_various_arrays_to_string(self, arr_src, str_expected):
        """Tests various array conversions"""
        str_received = get_np_array_as_string(arr_src)
        assert str_received == str_expected


class TestGetNPArrayIncremented:
    """Tests various array incrementations"""

    @pytest.mark.parametrize("arr_src, arr_expected", [
        (np.array([]), np.array([])),
        (np.array([1]), np.array([2])),
        (np.array([1,2,3,-4]), np.array([2,3,4,-3])),
    ])
    def test_various_arrays_incremented(self, arr_src, arr_expected):
        """Tests various array incrementations"""
        arr_received = get_np_array_incremented(arr_src, 1)
        npt.assert_array_equal(arr_received, arr_expected)


class TestMCProblemSolution:
    """Tests the class implementation of MCProblemSolution"""

    def test_to_file_creates_valid_mtx_file(self):
        """Tests if a graph is correctly stored in mtx format and contains solution.
        Creates a fully connected 3-node graph.
        Maximum-Clique is [0,1,2].
        Includes two comments.
        """
        row = np.array([0, 1, 0, 2, 1, 2])
        col = np.array([1, 0, 2, 0, 2, 1])
        data = np.ones(len(row), dtype=bool)
        graph = csr_array((data, (row, col)), shape=(3, 3))

        mc_problem_solution = MCProblemSolution(graph, np.array([0,1,2]))

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.mtx"
            mc_problem_solution.to_file(str(path), comments=["src: test", "a: b"])

            assert path.exists()

            with open(path, "r", encoding="ascii") as f:
                lines = f.readlines()

            assert lines[0].startswith("%%MatrixMarket matrix coordinate pattern symmetric")
            assert "%%n_max_clique: 3" in lines[1]
            assert "%%max_clique: [0,1,2]" in lines[2]
            assert "%%src: test" in lines[3]
            assert "%%a: b" in lines[4]
            assert f"%%density: {mc_problem_solution.graph_density}" in lines[5]
            assert "3 3 3" in lines[6]

            edge_lines = [line for line in lines if not line.startswith("%%")][1:]
            assert len(edge_lines) == 3

            for line in edge_lines:
                i, j = map(int, line.strip().split())
                assert i <= j, "Only upper triangle edges should be written"
