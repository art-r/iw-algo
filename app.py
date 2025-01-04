"""
The streamlit main file

Notes:
- Session state of core class to preserve across runs!
- when clicking compute button:
    if new input -> use new input,
    elif no input & prev input -> use prev input,
    else -> error
- output should be excel file (downloadable)
"""
from libraries.iw_handler import IWHandler
