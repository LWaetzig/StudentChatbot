import os
import time

import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space

from utils.Chatbot import Chatbot
from utils.FileProcessor import FileProcessor
from utils.helper import clear_chat, reset_file

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

# define session states
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello, I am JARVIS. How can I help you?"}
    ]
if "file" not in st.session_state:
    st.session_state.file = [{"name": "", "processed": False, "processor": None}]

# side bar component
with st.sidebar:
    st.title("JARVIS")
    st.caption("Just A Rather Very Intelligent Student")
    st.divider()

    # display disclaimer
    with st.status("Disclaimer", expanded=False, state="error"):
        st.write(
            """This software application employs open-source models sourced from Hugging Face, seamlessly integrated through an API. 
            Kindly refrain from submitting personal information or documents governed by data protection or copyright regulations. The provider assumes no liability for any consequences arising from such submissions.""",
        )

    # accept user input for HuggingFace API key and save it in environment variable
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = st.text_input(
        "HuggingFace API Key", type="password"
    )
    if os.environ["HUGGINGFACEHUB_API_TOKEN"]:
        st.success("API Key saved!")

    add_vertical_space(2)

    # upload file component
    uploaded_file = st.file_uploader(
        "Upload a file", type=["pdf"], on_change=reset_file
    )

    add_vertical_space(2)
    # button to clear chat history
    st.button("Clear Chat", on_click=clear_chat, use_container_width=True)


# show predefined assistant message
for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "🧑‍💻"
    with st.chat_message(name=message["role"], avatar=avatar):
        st.write(message["content"])


# process uploaded file
if uploaded_file and st.session_state.file[0]["processed"] == False:
    fp = FileProcessor()
    # update file information in session_state
    st.session_state.file[0] = {
        "name": uploaded_file.name,
        "processed": True,
        "processor": fp,
    }
    # display progress
    with st.status("Processing file...", expanded=True) as status:
        st.write("Extracting text from file")
        time.sleep(1)
        st.write("Splitting text into chunks")
        fp.process_pdf(uploaded_file)
        time.sleep(1)
        status.update(label="Done!", state="complete", expanded=False)


# accept raw user input
prompt = st.chat_input()
if prompt and not uploaded_file and st.session_state.file[0]["processed"] == False:
    # store user input in session_state
    st.session_state.messages.append({"role": "user", "content": prompt})
    # display user input
    with st.chat_message(name="user", avatar="🧑‍💻"):
        st.write(prompt)

    with st.chat_message(name="assistant", avatar="🤖"):
        # generate response
        response = "Please upload a file so that I can answer the question"
        # store response in session_state
        st.session_state.messages.append({"role": "assistant", "content": response})
        # simulate thinking process
        with st.spinner("Thinking..."):
            time.sleep(3)
        # display response message
        # simulate typing process
        message_placeholder = st.empty()
        full_response = str()
        for chunk in response.split():
            full_response += chunk + " "
            time.sleep(0.1)
            message_placeholder.write(full_response + "▌")
        message_placeholder.markdown(full_response[:-1])

# accept user input related to uploaded file
if prompt and uploaded_file and st.session_state.file[0]["processed"] == True:
    assistant = Chatbot()
    # store user input in session_state
    st.session_state.messages.append({"role": "user", "content": prompt})
    # display user input
    with st.chat_message(name="user", avatar="🧑‍💻"):
        st.write(prompt)
    # get matched documents based on prompt
    fp = st.session_state.file[0]["processor"]
    matched_documents = fp.get_matched_documents(prompt)

    # display matched documents
    with st.chat_message(name="assistant", avatar="🤖"):
        # generate response
        with st.spinner("Thinking..."):
            response = assistant.generate_answer(
                prompt, " ".join([each.page_content for each in matched_documents])
            )
            st.session_state.messages.append({"role": "assistant", "content": response})
            time.sleep(2)

        # display response message
        # simulate typing process
        message_placeholder = st.empty()
        full_response = str()
        for chunk in response.split():
            full_response += chunk + " "
            time.sleep(0.1)
            message_placeholder.write(full_response + "▌")
        message_placeholder.markdown(full_response[:-1])
