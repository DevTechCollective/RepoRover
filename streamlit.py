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
#             background-color: orange; /* Set the background color */
#             background-image: linear-gradient(rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.3)), url("https://raw.githubusercontent.com/Marcozc19/RepoRover/main/images/rover.png");
#             background-size: contain;
#             background-position: center top;
#             background-repeat: no-repeat;
#         }}
#         </style>
#         """,
#         unsafe_allow_html=True
#     )

# def add_rover_animation():
#     rover_html = """
#     <style>
#     @keyframes drive {
#         0%   {left: -120px; top: -120px;} /* Start from top-left, outside the screen */
#         25%  {left: -120px; top: 50vh;} /* Move down along the left side */
#         50%  {left: calc(100vw - 120px); top: 50vh;} /* Move to the right side, just outside the main column */
#         75%  {left: calc(100vw - 120px); top: -120px;} /* Move up along the right side */
#         100% {left: -120px; top: -120px;} /* Return to starting position outside the screen */
#     }

#     .rover {
#         position: fixed;
#         width: 100px; /* Width of the rover image */
#         height: 100px; /* Height of the rover image */
#         background-image: url('https://raw.githubusercontent.com/Marcozc19/RepoRover/main/images/rover.png'); /* Rover image URL */
#         background-size: cover;
#         animation: drive 10s linear infinite;
#     }
#     </style>
#     <div class="rover"></div>
#     """

#     components.html(rover_html, height=300)


# add_rover_animation()

# left_column, middle_column, right_column = st.columns([1, 3, 1])

# # Left column with rover animation
# with left_column:
#     components.html(add_rover_animation())



# # Right column with rover animation
# with right_column:
#     components.html(add_rover_animation())

# # You might want to store window height in the session state after user resizes the window
# # For this example, you would set it statically or via a callback when the app initializes
# if 'window_height' not in st.session_state:
#     st.session_state.window_height = 800  # Replace with your default or a JS callback to get the height

# Middle column with the main content
# with middle_column:


# add_bg_from_url()
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

        # summary = run_query.update_url(user_input)
        # st.write(summary)

        st.success("Done!")
    else: 
        st.write("Please enter a URL")

# generate chatbot area
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything about this repo"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    chat_response = asyncio.run(run_query.get_query(prompt))

    response = f"AI: {chat_response}"

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})


# What to do after button is clicked


    
