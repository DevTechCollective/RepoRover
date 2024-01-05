# RepoRover (started during Llama Hackathon 2023)

### Overview:
A developer's "right hand man". This tool assists developers in understanding GitHub repositories by exploring their file structure, readme files, and raw code with the help of LLMs.
Built using LangChain, OpenAi, and Streamlit.
Simply run and enter the URL of any GitHub repo, then ask away!

### Install requirements:
`pip install -r requirements.txt`

### env:
Create a `.env` file that defines your OpenAI API Key:
`OPENAI_API_KEY = <your-openai-api-key>`

### Run Command:
`streamlit run app.py`

### About:
The RepoRover uses the GPT-3.5 Turbo model from OpenAI and implements RAG with the help of the LangChain framework and FAISS vector store, allowing the Rover to explore massive repositories while remaining within the context window and providing relevant information to users. 
This is acheived via a similarity search on a vector store of the repo contents against the user query, followed by a second LLM which can request code from specific files and provide short summaries. Finally, all of this information is passed to the Rover LLM which now has the most relevant information of the entire Repo and the user query.