from dotenv import load_dotenv
import github_scraper
import os
from open_ai import ChatAi

load_dotenv()


class RunQuery(object):
    """
    This is a class that runs a query.
    """
    def __init__(self):
        self.param = ""
        self.readme = ""
        self.file_struct = ""
        self.repo_name =""

        # if os.path.exists("file_structure.txt") and os.path.getsize("file_structure.txt") != 0:
        #     with open("file_structure.txt", "r") as file:
        #         self.file_struct = file.read()

        # if os.path.exists("readme.txt") and os.path.getsize("readme.txt") != 0:
        #     with open("readme.txt", "r") as file:
        #         self.readme = file.read()

        self.chatBot = ChatAi(self.file_struct, self.readme, self.repo_name)
        

    async def get_query(self, input):
        """
        Get output for a given user_input
        """
        return self.chatBot.run_chat(input)
    
        
    async def update_url(self, url):
        """
        Update object vairables with new url
        """

        self.readme, self.file_struct = github_scraper.get_return(url)

        # with open("file_structure.txt", "w") as file:
        #     file_structure_str = str(self.file_struct)
        #     file.write(file_structure_str)

        # with open("readme.txt", "w") as file:
        #     readme_str = str(self.readme)
        #     file.write(readme_str)

        owner, repo = github_scraper.get_github_repo_info(url)
        self.repo_name = repo

        self.chatBot = ChatAi(self.file_struct, self.readme, self.repo_name)