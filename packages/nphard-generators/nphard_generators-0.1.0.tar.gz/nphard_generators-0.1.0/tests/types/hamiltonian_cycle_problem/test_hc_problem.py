"""Tests a HCProblem instance"""
import tempfile
from pathlib import Path

import numpy as np
from scipy.sparse import csr_array

from nphard_generators.types import HCProblem


def test_to_file_creates_valid_tsp_file():
    """Tests if a graph is correctly stored in tsp format.
    Creates a 3-node graph with edges (0,1) and (0,2).
    Includes two comments.
    """
    row = np.array([0, 1, 0, 2])
    col = np.array([1, 0, 2, 0])
    data = np.ones(len(row), dtype=bool)
    graph = csr_array((data, (row, col)), shape=(3, 3))

    hc_problem = HCProblem(graph)

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.tsp"
        hc_problem.to_file(str(path), comments=["src=test", "a=b"])

        assert path.exists()

        with open(path, "r", encoding="ascii") as f:
            lines = f.readlines()

        print(lines)

        assert lines[0] == "NAME: test.tsp\n"
        assert f"COMMENT: density={hc_problem.graph_density};src=test;a=b\n" in lines[1]
        assert lines[2] == "TYPE: TSP\n"
        assert lines[3] == "DIMENSION: 3\n"
        assert lines[4] == "EDGE_WEIGHT_TYPE: EXPLICIT\n"
        assert lines[5] == "EDGE_WEIGHT_FORMAT: UPPER_ROW\n"
        assert lines[6] == "EDGE_WEIGHT_SECTION\n"

        assert lines[7] == "1 1\n"
        assert lines[8] == "9999\n"
        assert lines[9] == "EOF\n"
