import time

import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space

from utils.Chatbot import Chatbot
from utils.FileProcessor import FileProcessor

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
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello, I am JARVIS. How can I help you?"}
    ]


# site content
with st.sidebar:
    st.title("JARVIS")
    st.caption("Just A Rather Very Intelligent Student")

    add_vertical_space(2)

    model = st.selectbox(
        "Model",
        ("T5", "GPT-3", "LLama 2", "BERT"),
        index=None,
        placeholder="Select a model...",
        disabled=False,
    )

    add_vertical_space(2)
    uploaded_file = st.file_uploader("Datei auswählen", type=["pdf", "txt"])
    if uploaded_file is not None:
        print(uploaded_file)
        FileProcessor = FileProcessor(uploaded_file)
        with st.spinner("Processing file..."):
            FileProcessor.process()
            st.success("Done!")


# display stored messages
for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "🧑‍💻"
    with st.chat_message(name=message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message(name="user", avatar="🧑‍💻"):
        st.write(prompt)

    # generate response
    response = Chatbot().call_t5_model(prompt)
    print(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message(name="assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = response[0]["translation_text"]

        # for chunk in response.split():
        #     full_response += chunk + " "
        #     time.sleep(0.1)
        #     message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
