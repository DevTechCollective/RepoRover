from openai import OpenAI
import os
from dotenv import load_dotenv

# from sentence_transformers import SentenceTransformer
# import faiss
# import numpy as np

# from langchain.chains.conversation.memory import ConversationSummaryBufferMemory
# from langchain.document_loaders import TextLoader
from langchain.text_splitter  import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
# from langchain.chat_models import ChatOpenAI
# from langchain.memory import ConversationBufferMemory
# from langchain.chains import ConversationalRetrievalChain
from langchain.schema.document import Document
import tiktoken
# load env
load_dotenv()


class ChatAi():

    def __init__(self, file_structure, readme_file, repo_name):
        api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=api_key)

        self.file_struct = file_structure
        self.readme = readme_file
        self.repo = repo_name

        # create vector stores
        self.readme_vector = self.create_vector_store(readme_file)
        self.file_vector = self.create_vector_store(file_structure)

        # provide scraped info to our model
        # self.conversation_history = self.initialize_history()
        self.conversation_history = []

        # other RAG impl strategies:
        # self.llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo")
        # # self.memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True, llm=self.llm)
        # self.memory = ConversationSummaryBufferMemory(memory_key='chat_history', return_messages=True)
        # self.conversation_chain = ConversationalRetrievalChain.from_llm(
        #     llm=self.llm,
        #     chain_type="stuff",
        #     retriever=self.file_vector.as_retriever(),
        #     max_tokens_limit=2000,
        #     memory=self.memory
        # )


    def create_vector_store(self, data):
        # to deal with later
        if not data:
            return

        # loader = TextLoader(data, encoding="utf-8")
        # data = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        # split_data = text_splitter.split_documents(data)
        split_data = [Document(page_content=x) for x in text_splitter.split_text(data)]

        # Creating the Vector Store
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_documents(split_data, embedding=embeddings)
        return vectorstore

    # def initialize_history(self):
    #     file_prompt = "Consider the following file structure from the " + self.repo + " GitHub repository: " + self.file_struct
    #     readme_prompt = "Consider this README.md file from the same GitHub repository: " + self.readme
    #     role_prompt = "You are an expert on this repo and will answer any questions I may have about the " + self.repo + " repository."

    #     history = [
    #         {"role": "user", "content": file_prompt},
    #         {"role": "assistant", "content": "I understand this file structure and will remember it."},
    #         {"role": "user", "content": readme_prompt},
    #         {"role": "assistant", "content": "I understand this README.md file and will remember it."},
    #         {"role": "user", "content": role_prompt}
    #     ]
    #     return history
    

    # get relevant and trimmed input for model
    def retrieve_context(self, query):
        readme_response = self.trim(self.readme_vector.similarity_search(query)[0].page_content)
        file_response = self.trim(self.file_vector.similarity_search(query)[0].page_content)

        file_prompt = "Consider the following files from the " + self.repo + " GitHub repository: " + file_response
        readme_prompt = "Consider this part of the README.md file from the same GitHub repository: " + readme_response

        return readme_prompt + " and " + file_prompt + "\n" + query
    

    # trim number of tokens to obey window size
    def trim(self, text, max_size=6000):
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        tokens = encoding.encode(text)
        
        if len(tokens) > max_size:
            trimmed_tokens = tokens[:max_size]
            text = encoding.decode(trimmed_tokens)

        return text


    def run_chat(self, user_input):
        # clear history to avoid overfilling window
        self.conversation_history = []

        enhanced_input = self.retrieve_context(user_input)
        # print(enhanced_input)
        self.conversation_history.append({"role": "user", "content": enhanced_input})

        stream = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=self.conversation_history,
            stream=True
        )

        response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                response += chunk.choices[0].delta.content

        self.conversation_history.append({"role": "assistant", "content": response})
        return response
    

    # Other RAG implementation attempts:


    # def run_chat(self, user_input):
    #     # Retrieve dynamic context based on the current query
    #     enhanced_input = self.retrieve_context(user_input)
    #     # Add user input to memory
    #     self.memory.add_message({"role": "user", "content": enhanced_input})

    #     # Get a condensed history from the memory
    #     condensed_history = self.memory.get_condensed_history()
        
    #     # Make the API call with the condensed history
    #     stream = self.client.chat.completions.create(
    #         model="gpt-3.5-turbo-1106",
    #         messages=condensed_history,
    #         stream=True,
    #         max_tokens_limit=3000
    #     )

    #     response = ""
    #     for chunk in stream:
    #         if chunk.choices[0].delta.content is not None:
    #             response += chunk.choices[0].delta.content

    #     # Add the response to memory
    #     self.memory.add_message({"role": "assistant", "content": response})

    #     return response

    # def run_chat(self, user_input):
    #     # Retrieve dynamic context based on the current query
    #     enhanced_input = self.retrieve_context(user_input)

    #     result = self.conversation_chain({"question": user_input})

    #     answer = result["answer"]
    #     return answer