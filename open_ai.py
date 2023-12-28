from openai import OpenAI
import os
from dotenv import load_dotenv

# load env
load_dotenv()


class ChatAi():

    def __init__(self, file_structure, readme_file, repo_name):
        api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=api_key)

        self.file_struct = file_structure
        self.readme = readme_file
        self.repo = repo_name

        # provide scraped info to our model
        self.conversation_history = self.initialize_history()


    def initialize_history(self):
        file_prompt = "Consider the following file structure from the " + self.repo + " GitHub repository: " + self.file_struct
        readme_prompt = "Consider this README.md file from the same GitHub repository: " + self.readme
        role_prompt = "You are an expert on this repo and will answer any questions I may have about the " + self.repo + " repository."

        history = [
            {"role": "user", "content": file_prompt},
            {"role": "assistant", "content": "I understand this file structure and will remember it."},
            {"role": "user", "content": readme_prompt},
            {"role": "assistant", "content": "I understand this README.md file and will remember it."},
            {"role": "user", "content": role_prompt}
        ]
        return history
    

    def run_chat(self, user_input):

        self.conversation_history.append({"role": "user", "content": user_input})

        stream = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=self.conversation_history,
            stream=True,
        )

        response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                response += chunk.choices[0].delta.content

        self.conversation_history.append({"role": "assistant", "content": response})
        return response