from dotenv import load_dotenv
from aiconfig import AIConfigRuntime, InferenceOptions
load_dotenv()
import github_scraper
import os

class RunQuery(object):
    """
    This is a class that runs a query.
    """
    def __init__(self):
        self.config = AIConfigRuntime.load('RepoRover_aiconfig.json')
        self.param = ""
        self.readme = ""
        self.file_struct = ""

        if os.path.exists("file_structure.txt") and os.path.getsize("file_structure.txt") != 0:
            with open("file_structure.txt", "r") as file:
                self.file_struct = file.read()
        

    async def get_query(self, input):
        """
        This is a method that runs a query.
        """
        self.param = {
            "user_question": input,
            "file_structure": self.file_struct,
            }
        inference_options = InferenceOptions(stream=True) # Defines a console streaming callback
        #await self.config.run("chatbot", self.param, options=inference_options)
        
        await self.config.run("chatbot", self.param)
        response = self.config.get_output_text("chatbot")
        return response
        
    async def update_url(self, url):
        """
        This is a method that passes in the url
        """

        self.readme, self.file_struct = github_scraper.get_return(url)

        with open("file_structure.txt", "w") as file:
            file_structure_str = str(self.file_struct)
            file.write(file_structure_str)

        owner, repo = github_scraper.get_github_repo_info(url)
        self.param = {
            "readme_file": self.readme,
            "repo_name": repo
        }
        await self.config.run("summarize_readme", self.param)
        response = self.config.get_output_text("summarize_readme")
        return response