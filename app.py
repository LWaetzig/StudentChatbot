import time

import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space

from utils.utils import clear_chat, reset_file
from utils.FileProcessor import FileProcessor
from utils.Chatbot import Chatbot

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

    add_vertical_space(2)

    uploaded_file = st.file_uploader(
        "Upload a file", type=["pdf"], on_change=reset_file
    )

    add_vertical_space(2)
    # button to clear chat history
    st.button("Clear Chat", on_click=clear_chat)


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
    with st.status("Processing file...", expanded=True) as status:
        st.write("Extracting text from file")
        time.sleep(1)
        st.write("Splitting text into chunks")
        fp.process_pdf(uploaded_file)
        time.sleep(1)
        status.update(label="Done!", state="complete", expanded=False)


# accept user input
prompt = st.chat_input()
if prompt and not uploaded_file and st.session_state.file[0]["processed"] == False:
    # store user input in session_state
    st.session_state.messages.append({"role": "user", "content": prompt})
    # display user input
    with st.chat_message(name="user", avatar="🧑‍💻"):
        st.write(prompt)

    with st.chat_message(name="assistant", avatar="🤖"):
        # generate response
        response = "Hello World Test"
        # store response in session_state
        st.session_state.messages.append({"role": "assistant", "content": response})
        # simulate thinking process
        with st.spinner("Thinking..."):
            time.sleep(3)
        # display response message
        message_placeholder = st.empty()
        # simulate typing process
        full_response = str()
        for chunk in response.split():
            full_response += chunk + " "
            time.sleep(0.1)
            message_placeholder.write(full_response + "▌")
        message_placeholder.markdown(full_response[:-1])


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
                prompt, matched_documents[0].page_content
            )
            st.session_state.messages.append({"role": "assistant", "content": response})
            time.sleep(2)

        message_placeholder = st.empty()
        # simulate typing process
        full_response = str()
        for chunk in response.split():
            full_response += chunk + " "
            time.sleep(0.1)
            message_placeholder.write(full_response + "▌")
        message_placeholder.markdown(full_response[:-1])


print(st.session_state.messages)
print(st.session_state.file)
