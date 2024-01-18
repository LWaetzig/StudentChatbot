import streamlit as st


def clear_chat():
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello, I am JARVIS. How can I help you?"}
    ]


def reset_file():
    st.session_state.file = [{"name": "", "processed": False, "processor": None}]
