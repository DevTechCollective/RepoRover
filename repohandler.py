import chromadb

class GitHubRepoHandler:
    def __init__(self):
        # Initialize ChromaDB Client
        self.chroma_client = chromadb.Client()

        # Create collections for README and file structure
        self.readme_collection = self.chroma_client.create_collection(name="readme")
        self.file_structure_collection = self.chroma_client.create_collection(name="file_structures")


    def update_file_structure(self, file_paths):
        """
        Update ChromaDB with the file structure from a GitHub repository.
        Each file path is stored as a separate document with a sequential ID.
        """
        for index, path in enumerate(file_paths):
            self.file_structure_collection.add(
                documents=[path],
                ids=[f"file_{index}"]  # Assigning a sequential ID
            )
        print("File structure updated in ChromaDB.")


    def query_file_structure(self, query_text):
        """
        Query the file structure collection based on a text query.
        """
        context = self.file_structure_collection.query(
            query_texts=[query_text],
            n_results=10
        )
        return context
        

    def update_readme(self, readme_content):
        """
        Update ChromaDB with the README content. 
        Since there's only ever one README, it replaces any existing data.
        """
        self.readme_collection.add(
            documents=[readme_content],
            ids=["single_readme"]  # A constant ID since there's only one README
        )
        print("README updated in ChromaDB.")


    def query_readme(self, query_text):
        """
        Query the README collection based on a text query.
        """
        context = self.readme_collection.query(
            query_texts=[query_text],
            filter={"id": "single_readme"},
            n_results=1
        )
        return context

    


# Example usage
repo_handler = GitHubRepoHandler()

# Simulate fetching data from a GitHub repository
readme_content = "Content of README"  # Replace with actual README content
file_paths = ["/src/main.py", "/README.md", "/docs/guide.md"]  # Example file paths

# Update ChromaDB with the GitHub data
repo_handler.update_readme(readme_content)
repo_handler.update_file_structure(file_paths)

# Example queries
readme_query_result = repo_handler.query_readme("how do I install the app? (readme Q)")
file_structure_query_result = repo_handler.query_file_structure("where is the app file located? (file struct Q)")

# Process the query results as needed

