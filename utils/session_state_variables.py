import streamlit as st
import sys


def _get_session_state(key=None, default=None):
    if key is None:
        key = sys._getframe(1).f_code.co_name  # The caller function name
    if key in st.session_state:
        return st.session_state[key]
    else:
        return default


def _set_session_state(value, key=None):
    if key is None:
        key = sys._getframe(1).f_code.co_name  # The caller function name
    st.session_state[key] = value


class SessionVariables:
    @property
    def prev_use_gs_fpath(self):
        return _get_session_state()

    @prev_use_gs_fpath.setter
    def prev_use_gs_fpath(self, value):
        _set_session_state(value)

    @property
    def gs_variables(self):
        return _get_session_state()

    @gs_variables.setter
    def gs_variables(self, value):
        _set_session_state(value)

    @property
    def _standard_normal_dist(self):
        return _get_session_state()

    @_standard_normal_dist.setter
    def _standard_normal_dist(self, value):
        _set_session_state(value)
