import time

import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space

from utils.Chatbot import Chatbot
from utils.FileProcessor import FileProcessor

# TODO: test how preprocessing behaves with more than one uploaded pdf
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

    # select model
    model = st.selectbox(
        "Model",
        ("T5", "BART", "QA_BERTA", "Custom"),
        index=0,  # selects T5 as default model
        placeholder="Select a model...",
        disabled=False,
    )
    if model == "T5" or model == "BART" or model == "QA_BERTA":
        st.info(
            "The model is embedded using huggingface api. Please provide a valid api token. See https://huggingface.co/docs/api-inference/quicktour#get-your-api-token for more information."
        )
        api_token = st.text_input("API Token", "")
        if api_token != "":
            st.success("API Token set")
        else:
            st.error("Please provide a valid API Token from your Huggingface account")
    else:
        st.info(
            "Custom models are not implemented yet. Please use T5 or BART. See https://huggingface.co/models for more information."
        )

    add_vertical_space(2)

    # component to upload and process file
    uploaded_file = st.file_uploader("Upload file", type=["pdf", "txt"])

    if uploaded_file is not None:
        file_processor = FileProcessor(uploaded_file)

        # check status of uploaded file and preprocess file only if it is new
        if uploaded_file.name != st.session_state.file_info["file_name"]:
            with st.status("Processing file...", expanded=True) as status:
                st.write("Extracting text from file")
                file_processor.process_pdf()
                time.sleep(1)
                st.write("Splitting text into chunks")
                time.sleep(1)
                status.update(label="Done!", state="complete", expanded=False)

    st.sidebar.button("Clear Chat History", on_click=clear_chat())


# display stored messages
for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "🧑‍💻"
    with st.chat_message(name=message["role"], avatar=avatar):
        st.markdown(message["content"])

# chat input
prompt = st.chat_input()
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message(name="user", avatar="🧑‍💻"):
        st.write(prompt)

    # get matched documents based on prompt
    if uploaded_file:
        print(uploaded_file.name)
        response = file_processor.get_matched_documents(prompt, uploaded_file.name)
        response = [document.page_content for document in response][0]
        # st.write(response)
        chatbot = Chatbot(model, api_token)
        if model == "QA_BERTA":
            response = chatbot.generate_response(
                {"question": prompt, "context": response}
            )
        else:
            st.error(
                "WARNING: If you want to retrieve knowledge from your uploaded documents, please select the model QA_BERTA."
            )
    else:
        # generate response
        chatbot = Chatbot(model, api_token)
        response = chatbot.generate_response(prompt)

    # display response
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message(name="assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = str()
        for chunk in response.split():
            full_response += chunk + " "
            time.sleep(0.1)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response[:-1])
