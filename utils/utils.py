from pathlib import Path
import streamlit as st


def top_dir() -> Path:
    return Path(__file__).parent.parent


def init_page_st(page_title):
    st.set_page_config(
        page_title=page_title,
        layout="wide",
        initial_sidebar_state="auto",
    )
