from openai import OpenAI
from chat_rover import ChatRover
import streamlit as st
from github_scraper import GitHubScraper
import time
import random
import os
from dotenv import load_dotenv

AVATAR_IMAGE = 'https://raw.githubusercontent.com/Marcozc19/RepoRover/main/images/rover3.png'
USER_IMAGE = "https://raw.githubusercontent.com/Marcozc19/RepoRover/main/images/moon.png"

fun_facts = [
    "Did you know GitHub sent a snapshot of all its active public repositories to the Arctic Code Vault, designed to last for 1,000 years, as a part of the GitHub Archive Program?",
    "The first successful rover on Mars was Sojourner, part of NASA's Mars Pathfinder mission in 1997. It was only about the size of a microwave oven!",
    "Machine learning algorithms are being used by NASA to analyze data from telescopes and rovers, helping to identify planetary features and phenomena.",
    "The first-ever repository created on GitHub was a simple Ruby library named 'grit' by GitHub co-founder Tom Preston-Werner.",
    "GitHub Copilot, an AI pair programmer, was trained on billions of lines of code from GitHub repositories, showcasing the vast potential of LLMs in coding.",
    "The first computer program was written by Ada Lovelace in the mid-1800s for Charles Babbage's Analytical Engine.",
    "As of 2023, GitHub hosts over 200 million repositories, making it the largest host of source code in the world.",
    "The term 'bug' in computing was popularized by Grace Hopper in 1947 when a moth was found in a computer and caused a malfunction.",
    "The Internet began in the late 1960s as a project called ARPANET, funded by the US Department of Defense.",
    "The Python programming language is not named after the snake, but after the British comedy group Monty Python.",
    "As of my last update, the most forked GitHub repository was FreeCodeCamp, a non-profit organization that helps people learn to code for free.",
    "The first computer virus was created in 1971 and was named 'Creeper'. It was an experimental self-replicating program.",
    "The first ever video game was created in 1958 and was a simple tennis game, similar to Pong, called 'Tennis for Two'.",
    "My creators built me during a Large Language Model hackathon in 2023."
]


# Tests API Key
def is_valid_key(api_key):
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[{'role': 'user', 'content': "Hello, world!"}],
            max_tokens=5
        )
        # print(response)
        # print(response.choices)
        # print('choices' in response)
        return response.choices is not None
    except Exception as e:
        print(e)
        return False


# Updates rover based on URL
def update_url(url):
    gitHubScraper = GitHubScraper(url)
    st.session_state.repo_name = gitHubScraper.get_repo_name()
    st.session_state.chat_rover = ChatRover(gitHubScraper, st.session_state.api_key)


# Get the Rover if it exists
chat_rover = st.session_state.chat_rover if 'chat_rover' in st.session_state else None
repo_name = st.session_state.repo_name if 'repo_name' in st.session_state else ""
sub_title = f"Currently Exploring {repo_name}" if repo_name != "" else ""

# Title for the app
st.title("RepoRover")


# Get API Key
if 'api_key' not in st.session_state or st.session_state.api_key is None:
    # use .env key if there is .env
    load_dotenv()
    if "OPENAI_API_KEY" in os.environ:
        api_key = os.environ["OPENAI_API_KEY"]
        if is_valid_key(api_key):
            st.session_state.api_key = api_key
            st.success("API Key loaded from .env file")
        else:
            st.error("Invalid API Key from .env file")
    else:
        api_key = st.text_input("Enter your OpenAI API key", type="password")
        if st.button('Submit'):
            if is_valid_key(api_key):
                st.session_state.api_key = api_key
                st.success("API Key accepted.")
            else:
                st.error("Invalid API Key.")

# Input box
repo_url = st.text_input("Enter a Repo URL")

# Button
if st.button("Learn the Repo"):
    if repo_url:
        random_fact = random.choice(fun_facts)
        st.info(f"Fun Fact: {random_fact}")
        with st.spinner("Analyzing repository terrain... Please wait..."):
            update_url(repo_url)
            st.session_state.messages = []
        st.success(f"New world discovered! Welcome to {st.session_state.repo_name}!")
    else:
        st.write("Please enter a URL")

st.header(sub_title)

# Generate chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = AVATAR_IMAGE if message['role'] == 'assistant' else USER_IMAGE
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything about this repo"):
    st.chat_message("user", avatar=USER_IMAGE).markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # start the spinner
    spinner = st.spinner("Engaging in digital deep thought...")
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
