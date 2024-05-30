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
    gsp_design_smooth_indicator,
    st_show_filter,
)
import streamlit as st
import numpy as np


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
        self._gs_variables = None
        selected_time = None
        self._max_time = 1
        slider_disabled = self._use_gs_fpath is None

        st.write("## Make Noizy Singals")
        self._load_graph_signal()
        selected_time = self._select_gs_time(
            slider_disabled=slider_disabled, max_value=self._max_time
        )
        noise_std = self._select_noise_std(slider_disabled=slider_disabled)
        if not slider_disabled:
            self._make_noise_signal(noise_std=noise_std)

        gs_draw_col, gs_spectrum_draw_col = st.columns(2)
        with gs_draw_col:
            self._gs_draw_col_function(self._gs_variables, selected_time)
        with gs_spectrum_draw_col:
            self._gs_spectrum_draw_col_function(self._gs_variables, selected_time)

        st.write("## Filtering")
        a1, a2 = self._select_filter_parameters(slider_disabled=slider_disabled)
        filter_col, filtered_spectrum, filtered_gs = st.columns(3)
        with filter_col:
            self._filter_design(
                gs_variables=self._gs_variables,
                a1=a1,
                a2=a2,
                selected_time=selected_time,
            )
        with filtered_spectrum:
            self._show_filtered_gs_spetrum(
                gs_variables=self._gs_variables, selected_time=selected_time
            )
        with filtered_gs:
            self._show_filtered_gs(
                gs_variables=self._gs_variables, selected_time=selected_time
            )

    def _load_graph_signal(self):
        gs_path_not_exists = self._use_gs_fpath is None
        if gs_path_not_exists:
            st.warning(
                "Please load the data of graph signals in the sidebar.", icon="⚠️"
            )
        else:
            if (
                variables.prev_use_gs_fpath
                and variables.prev_use_gs_fpath == self._use_gs_fpath
            ):
                self._gs_variables = variables.gs_variables
            else:
                self._gs_variables = get_graph_variables(self._use_gs_fpath)
                variables.prev_use_gs_fpath = self._use_gs_fpath
                variables.gs_variables = self._gs_variables
            self._max_time = self._gs_variables.max_time

    def _select_gs_time(self, slider_disabled, max_value=1):
        selected_time = st.slider(
            label="Select the time of graph signals: ",
            min_value=0,
            max_value=max_value,
            step=1,
            disabled=slider_disabled,
            key="time_of_graph_signal",
        )
        return selected_time

    def _select_noise_std(self, slider_disabled):
        noise_std = st.slider(
            label="Select the noise standard deviation: ",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            disabled=slider_disabled,
            key="noise_std",
        )
        return noise_std

    def _make_noise_signal(
        self,
        noise_std,
    ):
        noise_size = self._gs_variables.normalized_data.shape[0]
        self._noise_signal = np.random.normal(loc=0, scale=noise_std, size=noise_size)

    def _gs_draw_col_function(self, gs_variables, selected_time):
        if gs_variables is not None and selected_time is not None:
            noisy_data = (
                self._gs_variables.normalized_data[:, selected_time]
                + self._noise_signal
            )
            draw_graph_signals(
                G=gs_variables.G,
                pos=gs_variables.pos,
                data=gs_variables.data[:, selected_time],
                normalized_data=noisy_data,
            )
        else:
            show_empty_fig()

    def _gs_spectrum_draw_col_function(self, gs_variables, selected_time):
        if gs_variables is not None and selected_time is not None:
            noisy_data = (
                self._gs_variables.normalized_data[:, selected_time]
                + self._noise_signal
            )
            hat_graph_signal = apply_gft_to_signal(
                G=gs_variables.G,
                graph_signal=noisy_data,
            )
            show_spectrum(hat_signal=hat_graph_signal)
        else:
            show_empty_fig()

    def _select_filter_parameters(self, slider_disabled):
        a1 = st.slider(
            label="Select a1 for a filter: ",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            value=0.1,
            disabled=slider_disabled,
            key="filter_a1",
        )
        a2 = st.slider(
            label="Select a2 for a filter: ",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            value=0.5,
            disabled=slider_disabled,
            key="filter_a2",
        )
        return a1, a2

    def _filter_design(self, gs_variables, a1, a2, selected_time):
        if gs_variables is not None and selected_time is not None:
            self._g = gsp_design_smooth_indicator(G=gs_variables.G, a1=a1, a2=a2)
            st_show_filter(g=self._g)
        else:
            show_empty_fig()

    def _show_filtered_gs_spetrum(self, gs_variables, selected_time):
        if gs_variables is not None and selected_time is not None:
            noisy_data = (
                self._gs_variables.normalized_data[:, selected_time]
                + self._noise_signal
            )
            self._filtered_gs = self._g.filter(noisy_data)
            hat_filtered_gs = apply_gft_to_signal(
                G=gs_variables.G,
                graph_signal=self._filtered_gs,
            )
            show_spectrum(hat_signal=hat_filtered_gs)
        else:
            show_empty_fig()

    def _show_filtered_gs(self, gs_variables, selected_time):
        if gs_variables is not None and selected_time is not None:
            draw_graph_signals(
                G=gs_variables.G,
                pos=gs_variables.pos,
                data=gs_variables.data[:, selected_time],
                normalized_data=self._filtered_gs,
            )
        else:
            show_empty_fig()
