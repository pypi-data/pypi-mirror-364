"""Tests the mc_problem module"""
import tempfile
from pathlib import Path

import numpy as np
from scipy.sparse import csr_array

from nphard_generators.types import MCProblem


def test_to_file_creates_valid_mtx_file():
    """Tests if a graph is correctly stored in mtx format.
    Creates a fully connected 3-node graph.
    Includes two comments.
    """
    row = np.array([0, 1, 0, 2, 1, 2])
    col = np.array([1, 0, 2, 0, 2, 1])
    data = np.ones(len(row), dtype=bool)
    graph = csr_array((data, (row, col)), shape=(3, 3))

    mc_problem = MCProblem(graph)

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "graph.mtx"
        mc_problem.to_file(str(path), comments=["src: test", "a: b"])

        assert path.exists()

        with open(path, "r", encoding="ascii") as f:
            lines = f.readlines()

        assert lines[0].startswith("%%MatrixMarket matrix coordinate pattern symmetric")
        assert "%%src: test" in lines[1]
        assert "%%a: b" in lines[2]
        assert "%%density:" in lines[3]
        assert "3 3 3" in lines[4]

        edge_lines = [line for line in lines if not line.startswith("%%")][1:]
        assert len(edge_lines) == 3

        for line in edge_lines:
            i, j = map(int, line.strip().split())
            assert i <= j, "Only upper triangle edges should be written"
