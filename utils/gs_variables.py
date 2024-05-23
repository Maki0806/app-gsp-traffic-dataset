import numpy as np
from pygsp import graphs
from dataclasses import dataclass, field
import utils


@dataclass
class GraphVariables:
    N: np.ndarray
    T: np.ndarray
    L: np.ndarray
    W: np.ndarray
    data: np.ndarray
    pos: np.ndarray
    G: graphs.Graph = field(init=False)
    max_time: int = field(init=False)
    normalized_data: np.ndarray = field(init=False)

    def __post_init__(self):
        self.G = graphs.Graph(self.W)
        self.max_time = self.data.shape[1] - 1
        self.normalized_data = utils.normalize_graph_signal(self.data)
