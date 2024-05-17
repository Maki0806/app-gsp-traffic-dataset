from pathlib import Path
import streamlit as st


def top_dir() -> Path:
    return Path(__file__).parent.parent


def get_paths_of_target_suffix(parent_path, suffix):
    file_paths = parent_path.glob(f"**/*.{suffix}")
    return [*file_paths]


def get_file_names_from_paths(file_paths):
    return [file_path.stem for file_path in file_paths]


def init_page_st(page_title):
    st.set_page_config(
        page_title=page_title,
        layout="wide",
        initial_sidebar_state="auto",
    )
