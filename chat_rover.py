from openai import OpenAI
import os
from dotenv import load_dotenv

from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema.document import Document
import tiktoken
import imghdr

from langchain.chains.summarize import load_summarize_chain
from langchain_community.chat_models import ChatOpenAI

from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
# from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import StuffDocumentsChain, LLMChain
# load env
load_dotenv()


class ChatRover():

    def __init__(self, gitHubScraper):
        api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=api_key)

        self.gitHubScraper = gitHubScraper

        # Constants
        self.model = "gpt-3.5-turbo-1106"
        self.max_tokens = 16000
        self.trim_token_limit = self.max_tokens // 3
        self.readme_top_k = 5
        self.file_top_k = 10

        # create vector stores
        self.readme_vector = self.create_readme_vector()
        self.file_vector = self.create_file_vector()

        self.repo = self.gitHubScraper.repo
        self.conversation_history = []
        self.conversation_tokens = 0
        self.encoding = tiktoken.encoding_for_model(self.model)

    # Returns vector store where each entry is a single file path
    def create_file_vector(self):
        files = self.gitHubScraper.file_paths
        if not files:
            files = "Files not found."

        print("Creating file vector...")
        split_data = [Document(page_content=file) for file in files]

        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_documents(split_data, embedding=embeddings)
        print("File vector complete!")
        return vectorstore

    # Returns vector store where each entry is a chunk of the Readme
    def create_readme_vector(self):
        data = self.gitHubScraper.root_readme
        if not data:
            data = "Readme not found."

        text_splitter = CharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
        split_data = [Document(page_content=chunk) for chunk in text_splitter.split_text(data)]

        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_documents(split_data, embedding=embeddings)
        return vectorstore
    

    def is_not_image(self, file_path):
        if imghdr.what(file_path) is None:
            return True
        return False


    # given a list of file paths, get the code and provide a summary of the file
    def code_summary(self, file_paths):
        llm = ChatOpenAI(temperature=0.3, model_name="gpt-3.5-turbo-1106")
        chain = load_summarize_chain(llm, chain_type="map_reduce")
        docs = []
        for file in file_paths:
            print("POTENTIAL: ", file)
            if self.is_not_image(file):
                code = self.gitHubScraper.get_file_raw(file)
                if code:
                    docs.append(Document(page_content=code, metadata={"file_path": file}))

        res = "Code not found."
        if docs:
            res = chain.run(docs)
        return res
    

    def summarize_files(self, file_paths):

        llm = ChatOpenAI(temperature=0)

        # Map step: Define individual file summarization
        map_template = "Summarize the following code:\n{doc}\nSummary:"
        map_prompt = PromptTemplate.from_template(map_template)
        map_chain = LLMChain(llm=llm, prompt=map_prompt)

        # Reduce step: Define how to combine individual summaries
        reduce_template = "Combine the following summaries:\n{docs}\nCombined Summary:"
        reduce_prompt = PromptTemplate.from_template(reduce_template)
        reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)

        # Combine map and reduce chains
        map_reduce_chain = MapReduceDocumentsChain(
            llm_chain=map_chain,
            reduce_documents_chain=ReduceDocumentsChain(
                combine_documents_chain=StuffDocumentsChain(
                    llm_chain=reduce_chain, document_variable_name="docs"),
                collapse_documents_chain=StuffDocumentsChain(
                    llm_chain=reduce_chain, document_variable_name="docs"),
                token_max=4000),
            document_variable_name="doc",
            return_intermediate_steps=False)

        # Load and split documents
        # docs = [self.gitHubScraper.get_file_raw(fp) for fp in file_paths]
        docs = []
        for file in file_paths:
            if self.is_not_image(file):
                code = self.gitHubScraper.get_file_raw(file)
                if code:
                    docs.append(Document(page_content=code, metadata={"file_path": file}))

        # text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        # split_docs = text_splitter.split_documents(docs)

        # Summarize
        return map_reduce_chain.run(docs)

    # Returns relevant, trimmed, and prompted input for model via vector similarity search
    def retrieve_context(self, query):
        role_prompt = f"You are an expert on the {self.repo} repository. Relevant portions of the file structure and README are below, allowing you to understand the repo and how files are organized. There is also a question. Answer this question being precise and refering to specific files if helpful."

        readme_query = self.readme_vector.similarity_search(query, self.readme_top_k)
        file_query = self.file_vector.similarity_search(query, self.file_top_k)

        top_k_files = 2
        top_file_paths = []
        i = 0 
        while i < len(file_query) and i < top_k_files:
            top_file_paths.append(file_query[i].page_content)
            i+=1

        # print("FILE 1 TOKENS: ", self.token_count(code_file1))
        # code_summary = self.code_summary(top_file_paths)
        code_summary = self.summarize_files(top_file_paths)
        print(code_summary)



        readme_string = "\n".join(doc.page_content for doc in readme_query)
        file_string = ",".join(doc.page_content for doc in file_query)

        readme_response = self.trim(readme_string)
        file_response = self.trim(file_string)

        readme_prompt = "README.md portion:\n" + readme_response
        file_prompt = "Comma seperated file structure portion:\n" + file_response

        return f"{role_prompt}\n\n{readme_prompt}\n\n{file_prompt}\n\nUser Q: {query}"

    # Trim text by number of tokens to obey context window size
    def trim(self, text):
        tokens = self.encoding.encode(text)
        if len(tokens) > self.trim_token_limit:
            trimmed_tokens = tokens[:self.trim_token_limit]
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

    # interact with the LLM and update conversation history
    def run_chat(self, user_input):
        enhanced_input = self.retrieve_context(user_input)
        self.update_history("user", enhanced_input)
        print("TOKENS: ", self.conversation_tokens)
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
