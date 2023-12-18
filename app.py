import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space

# site config
st.set_page_config(
    page_title="JARVIS",
    page_icon=":robot:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://chat.openai.com/",
        "Report a bug": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "About": "# You got jebaited. HAHA",
    },
)

# Session states
if "messages" not in st.session_state:
    st.session_state.messages = []


# site content
with st.sidebar:
    st.title("JARVIS")
    st.caption("Just A Rather Very Intelligent Student")

    add_vertical_space(5)
    uploaded_file = st.file_uploader("Datei auswählen", type=["pdf", "txt"])
    