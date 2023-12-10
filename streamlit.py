import streamlit as st
import threading
import asyncio
from app import RunQuery


# Function to add a background image
def add_bg_from_url():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("images/rover.jpg");
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


config = RunQuery()

# Title for the app
st.title("RepoRover")

# Input box
user_input = st.text_input("Enter a Repo URL")

# thread function
def thread_function():
    asyncio.run(config.update_url(user_input))

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

        # generate chatbot area
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask me anything about this repo"):
            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            chat_response = asyncio.run(config.get_query(prompt))

            response = f"AI: {chat_response}"

            with st.chat_message("assistant"):
                st.markdown(response)

            st.session_state.messages.append({"role": "assistant", "content": response})

    else: 
        st.write("Please enter a URL")
    # What to do after button is clicked


    
