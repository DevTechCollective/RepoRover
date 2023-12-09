import streamlit as st

# Title for your app
st.title("RepoRover")

# Input box
user_input = st.text_input("Enter a Repo URL")

# Button
if st.button("Learn the Repo"):
    # What to do after button is clicked
    