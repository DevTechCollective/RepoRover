from chat_rover import ChatRover
import streamlit as st
from github_scraper import GitHubScraper
import time

AVATAR_IMAGE = 'https://raw.githubusercontent.com/Marcozc19/RepoRover/main/images/rover3.png'
USER_IMAGE = "https://raw.githubusercontent.com/Marcozc19/RepoRover/main/images/moon.png"


# Updates rover based on URL
def update_url(url):
    gitHubScraper = GitHubScraper(url)
    st.session_state.sub_title = gitHubScraper.repo
    st.session_state.chat_rover = ChatRover(gitHubScraper)


# Get the Rover if it exists
chat_rover = st.session_state.chat_rover if 'chat_rover' in st.session_state else None
repo_name = st.session_state.sub_title if 'sub_title' in st.session_state else ""
sub_title = f" ...Currently Exploring {repo_name}" if repo_name != "" else ""

# Title for the app
st.title("RepoRover")

# Input box
repo_url = st.text_input("Enter a Repo URL")

# Button
if st.button("Learn the Repo"):
    if repo_url:
        with st.spinner("Discovering new repo... Performing initial scans... Please wait."):
            update_url(repo_url)
            st.session_state.messages = []
        st.success(f"New world discovered! Welcome to {st.session_state.sub_title}!")
    else:
        st.write("Please enter a URL")

st.header(sub_title)

# generate chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = AVATAR_IMAGE if message['role'] == 'assistant' else USER_IMAGE
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])





# if prompt := st.chat_input("Ask me anything about this repo"):
#     st.chat_message("user", avatar=USER_IMAGE).markdown(prompt)
#     st.session_state.messages.append({"role": "user", "content": prompt})

#     with st.spinner(f"Travelling across {repo_name}..."):
#         chat_response = chat_rover.run_chat(prompt)

#     response = f"AI: {chat_response}"

#     with st.chat_message("assistant", avatar=AVATAR_IMAGE):
#         st.markdown(response)

#     st.session_state.messages.append({"role": "assistant", "content": response})
        



# if prompt := st.chat_input("Ask me anything about this repo"):
#     st.chat_message("user", avatar=USER_IMAGE).markdown(prompt)
#     st.session_state.messages.append({"role": "user", "content": prompt})

#     # Use st.spinner as a context manager
#     with st.spinner(f"Travelling across {repo_name}..."):
#         first_chunk_received = False
#         message_placeholder = st.empty()
#         full_response = ""

#         for response_chunk in chat_rover.run_chat(prompt):
#             if not first_chunk_received:
#                 first_chunk_received = True

#             full_response += response_chunk

#             with message_placeholder.container():
#                 st.chat_message("assistant", avatar=AVATAR_IMAGE).markdown(full_response + "▌")
#             # Optionally, add a small delay here to simulate typing speed

#         # After receiving all chunks, update the message placeholder without the cursor
#         with message_placeholder.container():
#             st.chat_message("assistant", avatar=AVATAR_IMAGE).markdown(full_response)

#         if not first_chunk_received:
#             # Display a message or handle the case where no response is received
#             st.error("No response received.")

#     # Append the full response to the session state
#     st.session_state.messages.append({"role": "assistant", "content": full_response})


if prompt := st.chat_input("Ask me anything about this repo"):
    st.chat_message("user", avatar=USER_IMAGE).markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # start the spinner
    spinner = st.spinner(f"Thinking deeply...")
    spinner.__enter__()

    first_chunk_received = False
    message_placeholder = st.empty()
    full_response = ""

    for response_chunk in chat_rover.run_chat(prompt):
        if not first_chunk_received:
            # Stop the spinner once first chunk is received
            spinner.__exit__(None, None, None)
            first_chunk_received = True

        full_response += response_chunk

        with message_placeholder.container():
            st.chat_message("assistant", avatar=AVATAR_IMAGE).markdown(full_response + "▌")
        time.sleep(0.05)  # small delay to simulate typing

    # After receiving all chunks, update the message placeholder without the cursor
    with message_placeholder.container():
        st.chat_message("assistant", avatar=AVATAR_IMAGE).markdown(full_response)

    if not first_chunk_received:
        # Stop spinner if no chunks were received
        spinner.__exit__(None, None, None)

    # Append full response to the session state
    st.session_state.messages.append({"role": "assistant", "content": full_response})
