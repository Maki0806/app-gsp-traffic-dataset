from utils import (
    init_page_st,
    top_dir,
    get_paths_of_target_suffix,
    get_file_names_from_paths,
    get_graph_variables,
    draw_graph_signals,
    show_empty_fig,
    variables,
    apply_gft_to_signal,
    show_spectrum,
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
        st.write(f"Selcted Graph Signal: {self._selected_gs_data}")
        selected_time, gs_variables = None, None
        max_time = 1
        slider_disabled = self._use_gs_fpath is None
        if slider_disabled:
            st.warning(
                "Please load the data of graph signals in the sidebar.", icon="⚠️"
            )
        else:
            if (
                variables.prev_use_gs_fpath
                and variables.prev_use_gs_fpath == self._use_gs_fpath
            ):
                gs_variables = variables.gs_variables
            else:
                gs_variables = get_graph_variables(self._use_gs_fpath)
                variables.prev_use_gs_fpath = self._use_gs_fpath
                variables.gs_variables = gs_variables
            max_time = gs_variables.max_time

        selected_time = self._select_gs_time(
            slider_disabled=slider_disabled, max_value=max_time
        )

        gs_draw_col, spectrum_draw_col = st.columns(2)
        with gs_draw_col:
            self.gs_draw_col_function(gs_variables, selected_time)
        with spectrum_draw_col:
            self.spectrum_draw_col_function(gs_variables, selected_time)

    def _select_gs_time(self, slider_disabled, max_value=1):
        selected_time = st.slider(
            label="Select the time of graph signals: ",
            min_value=0,
            max_value=max_value,
            step=1,
            disabled=slider_disabled,
        )
        return selected_time

    def gs_draw_col_function(self, gs_variables, selected_time):
        if gs_variables and selected_time is not None:
            draw_graph_signals(
                G=gs_variables.G,
                pos=gs_variables.pos,
                data=gs_variables.data[:, selected_time],
            )
        else:
            show_empty_fig()

    def spectrum_draw_col_function(self, gs_variables, selected_time):
        if gs_variables and selected_time is not None:
            hat_graph_signal = apply_gft_to_signal(
                G=gs_variables.G, graph_signal=gs_variables.data[:, selected_time]
            )
            show_spectrum(hat_signal=hat_graph_signal)
        else:
            show_empty_fig()
