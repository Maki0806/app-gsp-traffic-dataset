import numpy as np
from pygsp import graphs
from utils import (
    init_page_st,
    top_dir,
    get_paths_of_target_suffix,
    get_file_names_from_paths,
)
import streamlit as st


class AppVisGSP:
    def __init__(self):
        init_page_st("Graph Signal Visualization.")
        self._gs_parent_path = top_dir() / "GSP_TRAFFIC_Python"

    def run(self):
        self.sidebar_functions()
        self.main_functions()

    def sidebar_functions(self):
        with st.sidebar:
            self._gs_fpaths = get_paths_of_target_suffix(self._gs_parent_path, "npz")
            self._gs_fnames = get_file_names_from_paths(self._gs_fpaths)
            self._select_use_gs_data()

    def _select_use_gs_data(self):
        select_gs_data_diabled = not self._gs_parent_path.exists()
        self._selected_gs_data = st.selectbox(
            label="Please select the data you want to use:",
            options=self._gs_fnames,
            index=None,
            disabled=select_gs_data_diabled,
        )
        if select_gs_data_diabled:
            st.warning("Set GSP_TRAFFIC_Python in the directory of app.py.", icon="⚠️")
        self._use_gs_fpath = None
        if self._selected_gs_data:
            use_ind = self._gs_fnames.index(self._selected_gs_data)
            self._use_gs_fpath = self._gs_fpaths[use_ind]

    def main_functions(self):
        pass
