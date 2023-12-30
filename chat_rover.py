import json
from openai import OpenAI
from transformers import RagTokenizer, RagRetriever, RagTokenForGeneration
from datasets import load_dataset, Dataset
import os
from dotenv import load_dotenv

# load env
load_dotenv()

RAG_PASSAGE_FILE = "files_and_readme.json"


class ChatRover():

    def __init__(self, file_structure, readme_file, repo_name):
        api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=api_key)

        # self.file_struct = self._trim_to_context(file_structure)
        # self.readme = self._trim_to_context(readme_file)
        self.file_struct = file_structure
        self.readme = readme_file
        self.repo = repo_name

        # Initialize RAG components for preprocessing large data
        self._format_for_rag()
        self.rag_tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-nq")
        self.rag_retriever = RagRetriever.from_pretrained("facebook/rag-token-nq", index_name="custom", passages_path=RAG_PASSAGE_FILE)
        self.rag_model = RagTokenForGeneration.from_pretrained("facebook/rag-token-nq", retriever=self.rag_retriever)

        # provide scraped info to our model
        self.conversation_history = self.initialize_history()

    def initialize_history(self):
        role_prompt = f"You are an expert on the {self.repo} repository. You are given relevant portions of the file structure and README, which allows you to understand what the repo is and how files are organized. You will then be able to answer questions related to this repo, refering to specific files if helpful. You will receive prompts formatted with a 'User Q' and 'Relevant Info', where you answer the user question using the relevant info and history."
        # file_prompt = f"Consider the following file structure from the GitHub repository:\n{self.file_struct}"
        # readme_prompt = "Consider this README.md file from the same GitHub repository:\n{self.readme}"
        
        history = [
            {"role": "system", "content": role_prompt},
            # {"role": "user", "content": file_prompt},
            # {"role": "assistant", "content": "I understand this file structure and will remember it. I will use this to answer questions and reference specific files."},
            # {"role": "user", "content": readme_prompt},
            # {"role": "assistant", "content": "I understand this README.md file and will remember it. I have the contents of the README and can use it to understand and explain the repo."},
        ]
        return history

    def run_chat(self, user_input):
        rag_context = self.process_rag(user_input)

        new_prompt = f"User Q: {user_input}\nRelevant Info: {rag_context}"
        self.conversation_history.append({"role": "user", "content": new_prompt})

        # self.conversation_history.append({"role": "user", "content": user_input})

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

    def _format_for_rag(self):
        file_passages = [{"text": file_path, "title": f"File: {file_path}"} for file_path in self.file_struct]

        readme_sections = self.readme.split('\n\n')
        readme_passages = [{"text": section, "title": f"README Section: {index}"} for index, section in enumerate(readme_sections)]

        # Combine file and README passages
        combined_passages = file_passages + readme_passages

        # Convert to JSON and write to a file
        with open(RAG_PASSAGE_FILE, 'w') as f:
            json.dump(combined_passages, f, indent=4)

    def process_rag(self, user_query):
        input_ids = self.rag_tokenizer(user_query, return_tensors="pt")
        response_ids = self.rag_model.generate(input_ids)
        rag_out = self.rag_tokenizer.batch_decode(response_ids, skip_special_tokens=True)
        return rag_out[0]
