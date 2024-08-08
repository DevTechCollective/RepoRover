from chat_rover import ChatRover
from github_scraper import GitHubScraper
import os

user_input = "tell me something about this repo"

gitHubScraper = GitHubScraper("https://github.com/DevTechCollective/RepoRover")
rover = ChatRover(gitHubScraper)
rover.retrieve_context(user_input)
print(rover.conversation_history)
# rover.run_chat(user_input="tell me something about this repo")