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

        st.write("## Settings")
        st.write("### Time and Noize Settings")
        self._load_graph_signal()
        selected_time = self._select_gs_time(
            slider_disabled=slider_disabled, max_value=self._max_time
        )
        noize_std = self._select_noize_std(slider_disabled=slider_disabled)
        change_noize_signal = st.button(
            "Change noize signals", disabled=slider_disabled
        )
        if not slider_disabled:
            self._make_noize_signal(
                noize_std=noize_std, change_noize_signal=change_noize_signal
            )
        self._make_noizy_data(selected_time=selected_time)
        noize_gs_col, plus_col, true_gs_col, equal_col, noizy_gs_col = st.columns(
            [1, 0.1, 1, 0.1, 1]
        )
        spacing_html = self._get_html_spacer()
        st.markdown(spacing_html, unsafe_allow_html=True)
        with noize_gs_col:
            showing_data_noize = None
            if self._gs_variables:
                showing_data_noize = self._noize_signal
            self._show_gs(selected_time, showing_data_noize)
        with plus_col:
            st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
            st.latex(r"+")
        with true_gs_col:
            showing_data_gs = None
            if self._gs_variables:
                showing_data_gs = self._gs_variables.normalized_data[:, selected_time]
            self._show_gs(selected_time, showing_data_gs)
        with equal_col:
            st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
            st.latex(r"=")
        with noizy_gs_col:
            showing_data_noizy = None
            if self._gs_variables:
                showing_data_noizy = self._noizy_data
            self._show_gs(selected_time, showing_data_noizy)

        st.write("### Filter Settings")
        a1, a2 = self._select_filter_parameters(slider_disabled=slider_disabled)
        noizy_spectrum_col, filter_col, filtered_spectrum = st.columns(3)
        with noizy_spectrum_col:
            self._show_gs_spectrum(showing_data=self._noizy_data)
            st.write("Spectrum of Noizy Signal")
        with filter_col:
            self._filter_design(a1=a1, a2=a2)
            st.write("Designed Filter")
        self._apply_filter_to_noizy_data()
        with filtered_spectrum:
            self._show_gs_spectrum(showing_data=self._filtered_gs)
            st.write("Spectrum of Filtered Signal")

        st.write("## Filtering Results")
        true_gs_col, noizy_gs_col, filtered_gs_col = st.columns(3)
        with true_gs_col:
            showing_data_gs = None
            if self._gs_variables:
                showing_data_gs = self._gs_variables.normalized_data[:, selected_time]
            self._show_gs(selected_time, showing_data_gs)
            st.write("True Signal")
        with noizy_gs_col:
            showing_data_noizy = None
            if self._gs_variables:
                showing_data_noizy = self._noizy_data
            self._show_gs(selected_time, showing_data_noizy)
            st.write("Noizy Signal")
        with filtered_gs_col:
            showing_data_filtered = None
            if self._gs_variables:
                showing_data_filtered = self._filtered_gs
            self._show_gs(selected_time, showing_data_filtered)
            st.write("FIltered Singal")

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
                # NOTE: graph signal を読み込んだあとに、noize signal の初期化が必要
                # この初期化がないと、前の graph signal の noize signal が使用される
                self._make_noize_signal(noize_std=0, change_noize_signal=True)
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

    def _select_noize_std(self, slider_disabled):
        noize_std = st.slider(
            label="Select the noize standard deviation: ",
            min_value=0.0,
            max_value=1.0,
            value=0.2,
            step=0.01,
            disabled=slider_disabled,
            key="noize_std",
        )
        return noize_std

    def _make_noize_signal(
        self,
        noize_std,
        change_noize_signal,
    ):
        if variables._standard_normal_dist is None or change_noize_signal:
            noize_size = self._gs_variables.normalized_data.shape[0]
            _standard_normal_dist = np.random.normal(loc=0, scale=1, size=noize_size)
            variables._standard_normal_dist = _standard_normal_dist
            self._noize_signal = (noize_std**2) * _standard_normal_dist
        else:
            self._noize_signal = (noize_std**2) * variables._standard_normal_dist

    def _make_noizy_data(self, selected_time):
        if self._gs_variables is not None and selected_time is not None:
            self._noizy_data = (
                self._gs_variables.normalized_data[:, selected_time]
                + self._noize_signal
            )
        else:
            self._noizy_data = None

    def _get_html_spacer(self):
        # TODO: 画像サイズによって動的に margin-top を変更できるようにする
        spacing_html = """
<style>
.spacer {
    margin-top: 120px;  /* Adjust this value as needed */
}
</style>
"""
        return spacing_html

    def _show_gs(self, selected_time, showing_data):
        if self._gs_variables is not None and selected_time is not None:
            draw_graph_signals(
                G=self._gs_variables.G,
                pos=self._gs_variables.pos,
                data=self._gs_variables.data[:, selected_time],
                normalized_data=showing_data,
            )
        else:
            show_empty_fig()

    def _show_gs_spectrum(self, showing_data):
        if self._gs_variables is not None and showing_data is not None:
            hat_graph_signal = apply_gft_to_signal(
                G=self._gs_variables.G,
                graph_signal=showing_data,
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

    def _filter_design(self, a1, a2):
        if self._gs_variables is not None:
            self._g = gsp_design_smooth_indicator(G=self._gs_variables.G, a1=a1, a2=a2)
            st_show_filter(g=self._g)
        else:
            show_empty_fig()

    def _apply_filter_to_noizy_data(self):
        if self._noizy_data is not None:
            self._filtered_gs = self._g.filter(self._noizy_data)
        else:
            self._filtered_gs = None
