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
import pandas as pd
import streamlit as st

from libraries.iw_handler import IWHandler

@st.cache_data
def convert_df(df):
    return df.to_csv().encode("utf-8")

if 'handler' not in st.session_state:
    st.session_state['mainF'] = None
    st.session_state['extF'] = None

# do not create in session to make config editing easier
handler = IWHandler()

st.title("IW Group Creator")
st.markdown("""
    In the following please provide the following two things:
    1. The main excel file containing the user choices
    2. The file containing info about buddy group assignment
    """)

main_file = st.file_uploader("Main file", type=["xlsx", "xls"])
help_file = st.file_uploader("Extra file (buddy group info)", type=["xlsx", "xls"])

inputExistent = False
output_df = pd.DataFrame()
downloadDisabled = True

if st.button("Generate groups"):
    # check if input was provided
    if main_file is None or help_file is None:
        # if no input was provided check if previous session input exists
        if st.session_state['mainF'] is None or st.session_state['extF'] is None:
            st.error("Input missing", icon="🚨")
        else:
            st.warning('Using previous data from this session', icon="⚠️")
            inputExistent = True
    else:
        # save to session state
        st.session_state['mainF'] = main_file
        st.session_state['extF'] = help_file
        inputExistent = True

if inputExistent:
    handler.load_data(st.session_state['mainF'], st.session_state['extF'])
    with st.status("Creating groups"):
        st.write("Assigning to groups")
        st.write("Creating sub-groups")
        st.write("Adjusting order")
        output_df = handler.compute()
    downloadDisabled=False
    st.success("Successfully created groups", icon="✅")

st.divider()
st.write("### Output:")
st.download_button(
    label="Download result ",
    data=convert_df(output_df),
    file_name="IW_Groups.csv",
    mime="text/csv",
    disabled=downloadDisabled
)
if not downloadDisabled:
    st.write(output_df)

st.divider()
st.write("> ©️ 2024 - AR")