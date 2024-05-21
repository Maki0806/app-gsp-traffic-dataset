import numpy as np
from pygsp import graphs
from dataclasses import dataclass, field


@dataclass
class GraphVariables:
    N: np.ndarray
    T: np.ndarray
    L: np.ndarray
    W: np.ndarray
    data: np.ndarray
    pos: np.ndarray
    G: np.array = field(init=False)
    max_time: int = field(init=False)

    def __post_init__(self):
        self.G = graphs.Graph(self.W)
        self.max_time = self.data.shape[1] - 1
