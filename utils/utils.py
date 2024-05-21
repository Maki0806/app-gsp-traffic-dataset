from pathlib import Path
import streamlit as st
import numpy as np
from .gs_variables import GraphVariables
from typing import List, Type
from scipy.sparse import find
import networkx as nx
import matplotlib.pyplot as plt


def top_dir() -> Path:
    return Path(__file__).parent.parent


def get_paths_of_target_suffix(parent_path: Path, suffix: str) -> List[Path]:
    file_paths = parent_path.glob(f"**/*.{suffix}")
    return [*file_paths]


def get_file_names_from_paths(file_paths: List[Path]) -> List[str]:
    return [file_path.stem for file_path in file_paths]


def init_page_st(page_title):
    st.set_page_config(
        page_title=page_title,
        layout="wide",
        initial_sidebar_state="auto",
    )


def get_graph_variables(use_gs_fpath: Path) -> Type[GraphVariables]:
    gs_variables_npz = np.load(use_gs_fpath)
    gs_variables = GraphVariables(
        N=gs_variables_npz["N"],
        T=gs_variables_npz["T"],
        W=gs_variables_npz["W"],
        L=gs_variables_npz["L"],
        data=gs_variables_npz["data"],
        pos=gs_variables_npz["pos"],
    )
    return gs_variables


def draw_graph_signals(
    G: np.ndarray, pos: np.ndarray, data: np.ndarray = None, save_image_name: str = None
):
    position_dict = {
        node_num: (pos_x, pos_y) for node_num, (pos_x, pos_y) in enumerate(pos)
    }
    edges = _make_edge(G)
    graphD = _make_graphD(G=G, edges=edges)
    _st_graph_pyplot(graphD, data, position_dict)


def _make_edge(G: np.ndarray) -> List:
    W = find(G.W)
    edge_len = len(W[0])
    edges = [[int(W[0][i]), int(W[1][i])] for i in range(edge_len)]
    return edges


def _make_graphD(G: np.ndarray, edges: List) -> nx.DiGraph | nx.Graph:
    if G.is_directed:
        graphD = nx.DiGraph()
    else:
        graphD = nx.Graph()
    graphD.add_edges_from(edges)
    return graphD


def _st_graph_pyplot(
    graphD: nx.DiGraph | nx.Graph, data: np.ndarray, position_dict: dict
) -> None:
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1)
    if data is not None:
        mean_data = sum(data) / len(data)
        node_sizes = [20 * float(signal / mean_data) for signal in data]
        nx.draw_networkx_nodes(
            G=graphD,
            pos=position_dict,
            node_color=data,
            cmap="turbo",
            node_size=node_sizes,
        )
        sm = plt.cm.ScalarMappable(
            cmap="turbo", norm=plt.Normalize(vmin=min(data), vmax=max(data))
        )
        sm.set_array([0, max(data)])
        plt.colorbar(sm, ax=ax)
    else:
        nx.draw_networkx_nodes(G=graphD, pos=position_dict, node_size=10)
    nx.draw_networkx_edges(G=graphD, pos=position_dict, width=0.2)
    st.pyplot(fig=fig, use_container_width=True)


def show_empty_fig():
    zero_array = np.zeros((100, 2))
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(x=zero_array[:, 0], y=zero_array[:, 1])
    st.pyplot(fig=fig, use_container_width=True)
