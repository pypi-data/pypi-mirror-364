"""Tests the graph_problem module"""
import numpy as np
import numpy.testing as npt
import pytest
from scipy.sparse import csr_array

from nphard_generators.types.graph_problem import (
    calculate_available_verticies,
    calculate_edge_count,
    calculate_graph_density,
    calculate_max_edge_count_for_graph,
)


class TestCalculateEdgeCount:
    """Tests for calculate_edge_count method"""

    def test_symmetric_graph(self):
        """Tests the edge counting with a simple symmetric graph
        Graph:
            0 - 1
            | /
             2

        Edges:
            (0,1), (0,2), (1,2)
        """
        row = np.array([0, 1, 2, 0, 1, 2])
        col = np.array([1, 0, 0, 2, 2, 1])
        data = np.ones(len(row))
        graph = csr_array((data, (row, col)), shape=(3,3))

        assert calculate_edge_count(graph) == 3

    def test_empty_graph(self):
        """Tests the edge counting with an empty symmetric graph"""
        graph = csr_array((3, 3))
        assert calculate_edge_count(graph) == 0

    def test_raises_error_on_non_square(self):
        """Test with a non square shapes and expect error"""
        graph = csr_array((2, 4))
        with pytest.raises(ValueError):
            calculate_edge_count(graph)


class TestCalculateMaxEdgeCount:
    """Tests for calculate_max_edge_count method"""

    @pytest.mark.parametrize("shape, expected", [
        ((3, 3), 3),    # 3 nodes -> 3 edges max
        ((6, 6), 15),   # 6 nodes -> 15 edges max
        ((0, 0), 0),    # 0 nodes -> 0 edges max
        ((1, 1), 0),    # 1 node -> 0 edges max
    ])
    def test_various_shapes(self, shape, expected):
        """Test some shapes with expected max edge count"""
        graph = csr_array(shape)
        assert calculate_max_edge_count_for_graph(graph) == expected

    def test_raises_error_on_non_square(self):
        """Test with a non square shapes and expect error"""
        graph = csr_array((2, 4))
        with pytest.raises(ValueError):
            calculate_max_edge_count_for_graph(graph)


class TestCalculateGraphDensity:
    """Tests for calculate_graph_density method"""

    @pytest.mark.parametrize(
        "row, col, shape, expected_density",
        [
            # 0 nodes => density 0
            ([], [], (0, 0), 0.0),

            # 1 node, no edges => density 0
            ([], [], (1, 1), 0.0),

            # 2 nodes, 1 edge
            ([0, 1], [1, 0], (2, 2), 1.0),

            # 3 nodes, full graph (3 edges out of 3 possible)
            ([0, 1, 0, 2, 1, 2], [1, 0, 2, 0, 2, 1], (3, 3), 1.0),

            # 3 nodes, partial (1 edge)
            ([0, 1], [1, 0], (3, 3), 1 / 3),
        ],
    )
    def test_various_shapes(self, row, col, shape, expected_density):
        """Test some shapes with expected density"""
        data = np.ones(len(row))
        graph = csr_array((data, (row, col)), shape=shape)
        result = calculate_graph_density(graph)
        assert result == pytest.approx(expected_density)

    def test_raises_error_on_non_square(self):
        """Should raise if graph is not square"""
        graph = csr_array((2, 3))
        with pytest.raises(ValueError):
            calculate_graph_density(graph)


class TestCalculateAvailableVerticies:
    """Tests for calculate_available_verticies method"""

    @pytest.mark.parametrize("shape, expected", [
        ((0, 0), np.array([])),    # 0 nodes -> 0 edges max
        ((1, 1), np.array([0])),    # 1 node -> 0 edges max
        ((4, 4), np.array([0,1,2,3])),    # 4 nodes -> [0,1,2,3]
    ])
    def test_various_shapes(self, shape, expected):
        """Test some shapes with expected available verticies"""
        graph = csr_array(shape)
        result = calculate_available_verticies(graph)
        npt.assert_array_equal(result, expected)

    def test_raises_error_on_non_square(self):
        """Test with a non square shapes and expect error"""
        graph = csr_array((2, 4))
        with pytest.raises(ValueError):
            calculate_available_verticies(graph)
