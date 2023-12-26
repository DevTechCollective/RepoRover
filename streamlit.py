import streamlit as st
import threading
import asyncio
from app import RunQuery

import streamlit.components.v1 as components


# Function to add a background image
# def add_bg_from_url():
#     st.markdown(
#         f"""
#         <style>
#         .stApp {{
#             background-color: orange;
#             background-image: linear-gradient(rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.3)), url("https://raw.githubusercontent.com/Marcozc19/RepoRover/main/images/rover.png");
#             background-size: contain;
#             background-position: center top;
#             background-repeat: no-repeat;
#         }}
#         </style>
#         """,
#         unsafe_allow_html=True
#     )
# add_bg_from_url()


# def load_image_from_url(url):
#     response = requests.get(url)
#     if response.status_code == 200:
#         return Image.open(BytesIO(response.content))
#     else:
#         raise Exception("Could not download image from the URL")
    
avatar_url = 'https://raw.githubusercontent.com/Marcozc19/RepoRover/main/images/rover3.png'
user_url = "https://raw.githubusercontent.com/Marcozc19/RepoRover/main/images/moon.png"

# avatar_image = load_image_from_url(avatar_url)
run_query = RunQuery()


# Title for the app
st.title("RepoRover")

# Input box
user_input = st.text_input("Enter a Repo URL")

# thread function
def thread_function():
    return asyncio.run(run_query.update_url(user_input))

# Button
if st.button("Learn the Repo"):
    if user_input:
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
    avatar = avatar_url if message['role'] == 'assistant' else user_url
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything about this repo"):
    st.chat_message("user", avatar=user_url).markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    chat_response = asyncio.run(run_query.get_query(prompt))

    response = f"AI: {chat_response}"

    with st.chat_message("assistant", avatar=avatar_url):
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})


# What to do after button is clicked