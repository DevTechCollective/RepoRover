from openai import OpenAI
import os
from dotenv import load_dotenv

from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema.document import Document
import tiktoken

# load env
load_dotenv()


class ChatRover():

    def __init__(self, file_structure, readme_file, repo_name):
        api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=api_key)

        self.model = "gpt-3.5-turbo-1106"
        self.max_tokens = 16000

        # create vector stores
        self.readme_vector = self.create_vector_store(readme_file)
        file_structure = ','.join(file_structure)   # type conversion
        self.file_vector = self.create_vector_store(file_structure)

        self.repo = repo_name

        self.conversation_history = []
        self.encoding = tiktoken.encoding_for_model(self.model)

    # return Faiss object (vector) for given data
    def create_vector_store(self, data):
        if not data:
            return

        text_splitter = CharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
        split_data = [Document(page_content=x) for x in text_splitter.split_text(data)]

        # Creating the Vector Store
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_documents(split_data, embedding=embeddings)
        return vectorstore

    # get relevant and trimmed input for model
    def retrieve_context(self, query):
        readme_response = self.trim(self.readme_vector.similarity_search(query)[0].page_content)
        file_response = self.trim(self.file_vector.similarity_search(query)[0].page_content)

        readme_prompt = "Consider this part of the README.md file from the " + self.repo + " GitHub repository: " + readme_response
        file_prompt = "Consider this comma seperated file structure from the " + self.repo + " GitHub repository: " + file_response

        return readme_prompt + " and " + file_prompt + "\n" + query

    # trim number of tokens to obey window size
    def trim(self, text):
        max_prompt_tokens = self.max_tokens // 3
        tokens = self.encoding.encode(text)
        if len(tokens) > max_prompt_tokens:
            trimmed_tokens = tokens[:max_prompt_tokens]
            text = self.encoding.decode(trimmed_tokens)
        return text

    def token_count(self, text):
        return len(self.encoding.encode(text))

    # add conversation to history and keep history size below maxtokens
    def update_history(self, role, content):
        self.conversation_history.append({"role": role, "content": content})

        total_tokens = 0
        for entry in self.conversation_history:
            total_tokens += self.token_count(entry['content'])

        while total_tokens > self.max_tokens and self.conversation_history:
            removed_entry = self.conversation_history.pop(0)
            total_tokens -= self.token_count(removed_entry['content'])

    # interact with the LLM and keep history updated
    def run_chat(self, user_input):
        enhanced_input = self.retrieve_context(user_input)
        self.update_history("user", enhanced_input)

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=self.conversation_history,
            stream=True
        )

        response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                response += chunk.choices[0].delta.content

        self.update_history("assistant", response)
        return response
