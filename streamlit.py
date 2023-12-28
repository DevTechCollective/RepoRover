import streamlit as st
import threading
import asyncio
from app import RunQuery
import streamlit.components.v1 as components


AVATAR_IMAGE = 'https://raw.githubusercontent.com/Marcozc19/RepoRover/main/images/rover3.png'
USER_IMAGE = "https://raw.githubusercontent.com/Marcozc19/RepoRover/main/images/moon.png"


run_query = RunQuery()

# Title for the app
st.title("RepoRover")

# Input box
repo_url = st.text_input("Enter a Repo URL")

# thread function
def thread_function():
    return asyncio.run(run_query.update_url(repo_url))

# Button
if st.button("Learn the Repo"):
    if repo_url:
        thread = threading.Thread(target=thread_function)
        thread.start()

        # Show a message while the thread is running
        st.info("Processing... Please wait.")

        # Join the thread to ensure it completes before moving on
        thread.join()

        st.success("Done!")
    else: 
        st.write("Please enter a URL")

# generate chatbot area
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = AVATAR_IMAGE if message['role'] == 'assistant' else USER_IMAGE
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything about this repo"):
    st.chat_message("user", avatar=USER_IMAGE).markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    chat_response = asyncio.run(run_query.get_query(prompt))

    response = f"AI: {chat_response}"

    with st.chat_message("assistant", avatar=AVATAR_IMAGE):
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

# What to do after button is clicked