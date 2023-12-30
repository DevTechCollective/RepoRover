from openai import OpenAI
import os
from dotenv import load_dotenv

# load env
load_dotenv()


class ChatRover():

    def __init__(self, file_structure, readme_file, repo_name):
        api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=api_key)

        self.file_struct = self._trim_to_context(file_structure)
        self.readme = self._trim_to_context(readme_file)
        self.repo = repo_name

        # provide scraped info to our model
        self.conversation_history = self.initialize_history()

    def initialize_history(self):
        role_prompt = f"You are an expert on the {self.repo} repository. You are given the file structure and README you will understand what the repo is and how files are organized. You will then be able to answer questions related to this repo, refering to specific files if helpful."
        file_prompt = f"Consider the following file structure from the GitHub repository:\n{self.file_struct}"
        readme_prompt = "Consider this README.md file from the same GitHub repository:\n{self.readme}"
        
        history = [
            {"role": "system", "content": role_prompt},
            {"role": "user", "content": file_prompt},
            {"role": "assistant", "content": "I understand this file structure and will remember it. I will use this to answer questions and reference specific files."},
            {"role": "user", "content": readme_prompt},
            {"role": "assistant", "content": "I understand this README.md file and will remember it. I have the contents of the README and can use it to understand and explain the repo."},
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

    # TODO: replace with RAG
    def _trim_to_context(self, item, length=30000):
        if len(item) > length:
            return item[:length]
        return item
