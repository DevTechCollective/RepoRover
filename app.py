from chat_rover import ChatRover
import streamlit as st
from github_scraper import GitHubScraper


AVATAR_IMAGE = 'https://raw.githubusercontent.com/Marcozc19/RepoRover/main/images/rover3.png'
USER_IMAGE = "https://raw.githubusercontent.com/Marcozc19/RepoRover/main/images/moon.png"


# Updates rover based on URL
def update_url(url):
    scraper = GitHubScraper(url)
    st.session_state.chat_rover = ChatRover(scraper.file_paths, scraper.root_readme, scraper.repo)


# Get the Rover if it exists
chat_rover = st.session_state.chat_rover if 'chat_rover' in st.session_state else None

# Title for the app
st.title("RepoRover")

# Input box
repo_url = st.text_input("Enter a Repo URL")

# Button
if st.button("Learn the Repo"):
    if repo_url:
        st.info("Processing... Please wait.")
        update_url(repo_url)
        st.session_state.messages = []
        st.success("Done!")
    else:
        st.write("Please enter a URL")

# generate chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = AVATAR_IMAGE if message['role'] == 'assistant' else USER_IMAGE
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything about this repo"):
    st.chat_message("user", avatar=USER_IMAGE).markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    chat_response = chat_rover.run_chat(prompt)

    response = f"AI: {chat_response}"

    with st.chat_message("assistant", avatar=AVATAR_IMAGE):
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
