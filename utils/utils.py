from pathlib import Path
import streamlit as st
import numpy as np
from .gs_variables import GraphVariables
from typing import List, Type
from scipy.sparse import find
import networkx as nx
import matplotlib.pyplot as plt
from pygsp import filters


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
    G: any,
    pos: np.ndarray,
    data: np.ndarray = None,
    normalized_data: np.ndarray = None,
):
    position_dict = {
        node_num: (pos_x, pos_y) for node_num, (pos_x, pos_y) in enumerate(pos)
    }
    node_value_disabled = _check_node_value_disabled(data, normalized_data)
    if not node_value_disabled and normalized_data is None:
        normalized_data = data
    node_sizes = _make_node_size(data)
    edges = _make_edge(G)
    graphD = _make_graphD(G=G, edges=edges)
    _st_graph_pyplot(
        graphD, normalized_data, node_sizes, position_dict, node_value_disabled
    )


def _check_node_value_disabled(data, normalized_data) -> bool:
    node_value_disabled = data is None and normalized_data is None
    if data is None and normalized_data is not None:
        raise Exception("Please input `data` into draw_graph to show the node values.")
    return node_value_disabled


def _make_edge(G) -> List:
    W = find(G.W)
    edge_len = len(W[0])
    edges = [[int(W[0][i]), int(W[1][i])] for i in range(edge_len)]
    return edges


def _make_graphD(G, edges: List) -> nx.DiGraph | nx.Graph:
    if G.is_directed():
        graphD = nx.DiGraph()
    else:
        graphD = nx.Graph()
    graphD.add_edges_from(edges)
    return graphD


def _make_node_size(data: np.ndarray) -> List[float]:
    mean_data = sum(data) / len(data)
    node_sizes = [20 * float(signal / mean_data) for signal in data]
    return node_sizes


def _st_graph_pyplot(
    graphD: nx.DiGraph | nx.Graph,
    normalized_data: np.ndarray,
    node_sizes: List[float],
    position_dict: dict,
    node_value_disabled: bool,
) -> None:
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1)
    if node_value_disabled:
        nx.draw_networkx_nodes(G=graphD, pos=position_dict, node_size=10)
    else:
        nx.draw_networkx_nodes(
            G=graphD,
            nodelist=np.arange(len(position_dict)),
            pos=position_dict,
            node_color=normalized_data,
            cmap="turbo",
            node_size=node_sizes,
        )
        sm = plt.cm.ScalarMappable(
            cmap="turbo",
            norm=plt.Normalize(vmin=min(normalized_data), vmax=max(normalized_data)),
        )
        sm.set_array([0, max(normalized_data)])
        plt.colorbar(sm, ax=ax)
    nx.draw_networkx_edges(G=graphD, pos=position_dict, width=0.2)
    st.pyplot(fig=fig, use_container_width=True)


def show_empty_fig():
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(x=[], y=[])
    st.pyplot(fig=fig, use_container_width=True)


def apply_gft_to_signal(G, graph_signal: np.ndarray):
    G.compute_fourier_basis()
    hat_graph_signal = G.gft(graph_signal)
    return hat_graph_signal


def show_spectrum(hat_signal: np.ndarray):
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1)
    signal_index = [i for i in range(len(hat_signal))]
    ax.stem(signal_index, np.abs(hat_signal))
    st.pyplot(fig=fig, use_container_width=True)


def normalize_graph_signal(graph_signal: np.ndarray, axis: int = 0):
    mean_gs = np.mean(graph_signal, axis=axis, keepdims=True)
    std_gs = np.std(graph_signal, axis=axis, keepdims=True)
    return (graph_signal - mean_gs) / std_gs


def gsp_design_smooth_indicator(G, a1, a2):
    G.compute_fourier_basis()
    lmax = G.lmax
    fx = lambda x, a: np.exp(-a / x) * (x >= 0)
    gx = lambda x, a: fx(x, a) / (fx(x, a) + fx(1 - x, a))
    ffin = lambda x, a1, a2: np.where(
        x >= a1, gx(1 - (x - a1) / (a2 - a1), 1), np.where(x >= 0, 1, 0)
    )
    g = lambda x: ffin(x / lmax, a1, a2)
    return filters.Filter(G, g)


def st_show_filter(g, fig_title: str = None):
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1)
    g.plot(plot_eigenvalues=True, ax=ax)
    ax.set_title(fig_title)
    fig.tight_layout()
    st.pyplot(fig=fig, use_container_width=True)
