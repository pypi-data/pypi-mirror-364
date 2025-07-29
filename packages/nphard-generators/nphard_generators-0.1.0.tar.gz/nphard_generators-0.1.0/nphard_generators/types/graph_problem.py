"""Contains functions and a base class relevant to every basic graph problem.

A graph is always represented as a square (sparse) matrix.

The module provides methods for counting edges, calculating density
and a basic GraphProblem class that can be inherited.

Typical usage example:

    n_edges = calculate_edge_count(graph)
    density = calculate_graph_density(graph)
    n_edges_max = calculate_max_edge_count(graph)
    available_verticies = calculate_available_verticies(graph)
"""

__all__ = [
    "calculate_edge_count",
    "calculate_max_edge_count_for_graph",
    "calculate_max_edge_count_for_n_nodes",
    "calculate_graph_density",
    "calculate_available_verticies",
    "assert_is_square_matrix",
    "assert_is_np_int_array",
    "assert_is_subset",
    "get_np_array_incremented",
    "get_np_array_as_string",
    "GraphProblem"
]

from abc import ABC, abstractmethod
import os

from scipy.sparse import csr_array
import numpy as np


def calculate_edge_count(graph: csr_array):
    """Returns the number of edges of the given graph.
    
    Assuming a symmetric graph where both connections are set, e.g.
    graph[x,y] == True -> graph[y,x] == True
    and no self connections => For all x: graph[x,x] == False.

    Therefore a connection from x,y or y,x counts as one connection.

    Args:
        graph: An graph is csr_array format.
    """
    assert_is_square_matrix(graph)

    return int(graph.nnz/2)


def calculate_max_edge_count_for_graph(graph: csr_array):
    """Returns the maximum number of edges for the given graph.

    Edges from a node to itself are not considered.

    Args:
        graph: An graph is csr_array format.
    """
    assert_is_square_matrix(graph)

    return calculate_max_edge_count_for_n_nodes(graph.shape[0])


def calculate_max_edge_count_for_n_nodes(n_nodes: int):
    """Returns the maximum number of edges for the node count.

    Edges from a node to itself are not considered.
    """
    n_total_edges = n_nodes**2
    return (n_total_edges - n_nodes)/2


def calculate_graph_density(graph: csr_array):
    """Returns the density of the given graph.

    Counts the edges and divides it by the amount of possible edges.
    See calculate_edge_count for more details.

    Args:
        graph: An graph is csr_array format.
    """
    assert_is_square_matrix(graph)

    n_edges = calculate_edge_count(graph)

    if n_edges == 0:
        return 0

    n_edges_max = calculate_max_edge_count_for_graph(graph)
    return n_edges / n_edges_max


def calculate_available_verticies(graph: csr_array):
    """Returns a list of verticies of the graph.

    Args:
        graph: An graph is csr_array format.

    Returns:
        A numpy array with elements [0, 1, ..., n-1].
    """
    assert_is_square_matrix(graph)

    n_nodes = min(graph.shape[0], graph.shape[1])
    return np.array(list(range(0, n_nodes)))


def assert_is_square_matrix(graph):
    """Raises ValueError if the graph is not a square matrix."""
    if graph.shape[0] != graph.shape[1]:
        raise ValueError(
            f"Expecting graph matrix to be square. "
            f"Found {graph.shape[0]}x{graph.shape[1]}"
        )


def assert_is_np_int_array(arr: np.ndarray) -> bool:
    """Raises ValueError if the array is not a 1D numpy int array."""

    if not isinstance(arr, np.ndarray):
        raise ValueError(f"Array must be a numpy array. Found {type(arr)}.")

    if not arr.ndim == 1:
        raise ValueError(f"Array must be one dimensional. Found {arr.ndim} dimensions.")

    if not np.issubdtype(arr.dtype, np.integer):
        raise ValueError(f"Array must contain integers. Found {arr.dtype}.")


def assert_is_subset(subset: np.ndarray, superset: np.ndarray) -> bool:
    """Raises ValueError if the subset array is not a subset of the superset array."""

    if not all(node in superset for node in subset):
        raise ValueError(f"Given subset {subset} not a subset of {superset}.")


def get_np_array_incremented(arr: np.ndarray, increment: int):
    """Increments each value in arr by increment and returns an incremented copy."""
    arr_incremented = arr.copy()
    arr_incremented += increment
    return arr_incremented


def get_np_array_as_string(arr: np.ndarray):
    """Converts [1,2,3] to "[1,2,3]"."""
    return np.array2string(arr,separator=',',max_line_width=np.inf).replace(' ','')


class GraphProblem(ABC):
    """Abstract base class for undirected, unweighted graph problems.

    Attributes:
        graph: Graph representation in sparse row format.
        n_nodes: Number of nodes of the graph.
        n_edges: Number of edges of the graph.
        density: Density of the graph.
        available_verticies: IDs (0,1,...) of the verticies.
    """

    def __init__(self, graph: csr_array):

        if not isinstance(graph, csr_array):
            raise TypeError(f"Input must be a scipy.sparse.csr_array. Found {type(graph)}.")

        assert_is_square_matrix(graph)

        if (graph != graph.T).nnz != 0:
            raise ValueError(
                "Graph must be undirected: adjacency matrix is not equal to its transpose.")

        self._graph = graph
        self._n_nodes = graph.shape[0]
        self._n_edges = calculate_edge_count(graph)
        self._graph_density = calculate_graph_density(graph)
        self._available_verticies = calculate_available_verticies(graph)

    @property
    def graph(self):
        """The graph itself."""
        return self._graph

    @property
    def n_nodes(self):
        """The graph's node count."""
        return self._n_nodes

    @property
    def n_edges(self):
        """The graph's edge count."""
        return self._n_edges

    @property
    def graph_density(self):
        """The graph's density."""
        return self._graph_density

    @property
    def available_verticies(self):
        """The available verticies of the graph."""
        return self._available_verticies

    def has_edge(self, x: int, y: int):
        """Returns true, if the graph has an edge [x,y] or [y,x]."""
        return self.graph[x,y] or self.graph[y,x]

    @abstractmethod
    def to_file(self, path_to_file: str, comments: list[str] = None):
        """Writes the problem instance to a file on the given path.
        
        Subclasses need to specify wheather they call to_tsp_file, to_mtx_file or other.
        Provide comments without file specific format, conversion will be automatically done.
        E.g. Provide: "density: 0.2"
        -> mtx: %%density: 0.2
        -> tsp: COMMENT: density: 0.2

        Args:
            path_to_file: Path to the file to write into
            comments: List of strings that are converted into file specific comments
        """

    def _to_tsp_file(self, path_to_file: str, comments: list[str] = None):
        """Writes the graph problem to a file in tsp format.

        Creates the file, if necessary.

        Format:
            NAME: [filename]
            COMMENT: density=[density];[comments...]
            TYPE: TSP
            DIMENSION: [n_nodes]
            EDGE_WEIGHT_TYPE: EXPLICIT
            EDGE_WEIGHT_FORMAT: UPPER_ROW
            EDGE_WEIGHT_SECTION
            9999 9999 1 9999
            1 9999 9999
            ...
        """

        dir_name = os.path.dirname(path_to_file) or "./"
        os.makedirs(dir_name, exist_ok=True)

        with open(path_to_file, "w", encoding="ascii") as f:

            file_name = os.path.basename(path_to_file)
            comments = comments or []
            comments_str = ";".join(comments)   # Results in comment1;comment2;...

            f.write(f"NAME: {file_name}\n")
            f.write(f"COMMENT: density={self.graph_density};{comments_str}\n")
            f.write("TYPE: TSP\n")
            f.write(f"DIMENSION: {self.n_nodes}\n")
            f.write("EDGE_WEIGHT_TYPE: EXPLICIT\n")
            f.write("EDGE_WEIGHT_FORMAT: UPPER_ROW\n")
            f.write("EDGE_WEIGHT_SECTION\n")

            # Write upper triangle
            for i in range(self.n_nodes-1):

                row_start = self.graph.indptr[i]
                row_end = self.graph.indptr[i+1]
                cols = self.graph.indices[row_start:row_end]
                values = self.graph.data[row_start:row_end]
                row_dict = dict(zip(cols, values))

                # Create rows like: 1 9999 1 1 9999
                row_entries = [
                    str(int(row_dict.get(j, 9999))) for j in range(i + 1, self.n_nodes)
                ]
                f.write(" ".join(row_entries) + "\n")

            f.write("EOF\n")


    def _to_mtx_file(self, path_to_file: str, comments: list[str] = None):
        """Writes the graph problem to a file in matrix market format.

        Creates the file, if necessary.

        Important: MatrixMarket indizes start by 1 (not 0).

        Configuration of the matrix market format:
        - matrix: The graph is stored as a matrix
        - coordinate: Edges are stored as a coordinate list, e.g. 2 4 -> Edge from 2 to 4
        - pattern: The matrix contains only the structure, no values (-> unweighted graph)
        - symmetric: Undirected graph -> only upper trianble of the matrix is stored

        Format:
            %%MatrixMarket matrix coordinate pattern symmetric
            %%[comment1]
            ...
            %%density: [density]
            [n_nodes] [n_nodes] [n_edges]
            0 1
            1 2
            1 2
            ...

        Args:
            path_to_file: Path to a file the graph problem will be written into.
            comments: A list of comments that will be inserted into the file.
        """

        dir_name = os.path.dirname(path_to_file) or "./"
        os.makedirs(dir_name, exist_ok=True)

        with open(path_to_file, "w", encoding="ascii") as f:

            f.write("%%MatrixMarket matrix coordinate pattern symmetric\n")

            comments = comments or []
            for comment in comments:
                f.write(f"%%{comment}\n")

            f.write(f"%%density: {self.graph_density}\n")

            f.write(f"{self.n_nodes} {self.n_nodes} {self.n_edges}\n")

            # Coo format for more efficient upper triangle retrieval
            graph_coo = self.graph.tocoo()

            # Filter for upper triangle (i <= j)
            mask = graph_coo.row <= graph_coo.col
            row = graph_coo.row[mask]
            col = graph_coo.col[mask]

            for i, j in zip(row, col):
                f.write(f"{i+1} {j+1}\n")
