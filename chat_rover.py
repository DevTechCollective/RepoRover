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

        # constants
        self.model = "gpt-3.5-turbo-1106"
        self.max_tokens = 16000
        self.readme_top_k = 5
        self.file_top_k = 10

        # create vector stores
        self.readme_vector = self.create_readme_vector(readme_file)
        # file_structure = ','.join(file_structure)   # type conversion
        self.file_vector = self.create_file_vector(file_structure)

        self.repo = repo_name
        self.conversation_history = []
        self.conversation_tokens = 0
        self.encoding = tiktoken.encoding_for_model(self.model)

    def create_file_vector(self, files):
        if not files:
            return
        
        print("Creating file vector...")
        split_data = [Document(page_content=x) for x in files]

        # Creating the Vector Store
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_documents(split_data, embedding=embeddings)
        print("File vector complete!")
        return vectorstore


    # return Faiss object (vector) for given data
    def create_readme_vector(self, data):
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
        role_prompt = f"You are an expert on the {self.repo} repository. Relevant portions of the file structure and README are below, allowing you to understand the repo and how files are organized. There is also a question. Answer this question being precise and refering to specific files if helpful."

        # embeddings = OpenAIEmbeddings()  # Assuming this is the same embeddings used for the documents
        # query_vector = embeddings.embed_query(query)

        readme_query = self.readme_vector.similarity_search(query, self.readme_top_k)
        file_query = self.file_vector.similarity_search(query, self.file_top_k)

        readme_string = "\n".join(doc.page_content for doc in readme_query)
        file_string = ",".join(doc.page_content for doc in file_query)

        readme_response = self.trim(readme_string)
        file_response = self.trim(file_string)

        # readme_response = self.trim(self.readme_vector.similarity_search(query)[0].page_content)
        # file_response = self.trim(self.file_vector.similarity_search(query)[0].page_content)

        readme_prompt = "README.md portion:\n" + readme_response
        file_prompt = "Comma seperated file structure portion:\n" + file_response

        return f"{role_prompt}\n{readme_prompt}\n{file_prompt}\nUser Q: {query}"

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
        self.conversation_tokens += self.token_count(content)

        while self.conversation_tokens > self.max_tokens and self.conversation_history:
            removed_entry = self.conversation_history.pop(0)
            self.conversation_tokens -= self.token_count(removed_entry['content'])


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