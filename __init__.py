import streamlit.components.v1 as components
import os

_FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")

physio_form = components.declare_component(
    "physio_form",
    path=_FRONTEND_DIR
)
