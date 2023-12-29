import requests


class GitHubScraper:

    def __init__(self, github_url, branch=None, condensed=False):
        self.github_url = github_url
        self.owner, self.repo = self.get_github_repo_info()
        self.branch = self.get_default_branch() if branch is None else branch
        self.root_readme = ""   # Will be set upon traversing file structue
        self.file_paths = self.get_repo_file_structure(condensed)

    def get_github_repo_info(self):
        parts = self.github_url.split('/')
        owner = parts[-2]
        repo = parts[-1]
        return owner, repo

    def get_default_branch(self):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get('default_branch', 'master')
        else:
            print("Error fetching default branch:", response.status_code, response.text)
            return None

    def get_repo_file_structure(self, condese=False):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/trees/{self.branch}?recursive=1"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            # files = map(lambda x: x['path'], data['tree'])
            files = []
            for file in data['tree']:
                if file['type'] == 'blob':
                    if file['path'].lower() == 'readme.md':
                        self.root_readme = self.get_file_raw(file['path'])
                    files.append(file['path'])
            if condese:
                files = self._condense_file_structure(files)
            return files
        else:
            print("Error:", response.status_code, response.text)
            return None

    def get_file_raw(self, file_path):
        url = f'https://api.github.com/repos/{self.owner}/{self.repo}/contents/{file_path}?ref={self.branch}'
        headers = {'Accept': 'application/vnd.github.v3.raw'}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to retrieve file: {response.status_code}")
            return None

    def _condense_file_structure(self, file_paths):
        formatted_structure = ""
        directory_depths = {}

        file_paths.sort()  # Ensure paths are processed in a sorted order for correct structure

        for file_path in file_paths:
            path_segments = file_path.split('/')

            # Determine the current depth and adjust if necessary
            current_depth = 0
            for segment in path_segments[:-1]:
                if segment not in directory_depths or directory_depths[segment] != current_depth:
                    formatted_structure += "  " * current_depth + segment + "/\n"
                    directory_depths[segment] = current_depth
                current_depth += 1

            # Add the file at the correct depth
            formatted_structure += "  " * current_depth + path_segments[-1] + "\n"

        return formatted_structure


# def get_return(github_url):
#     owner, repo = get_github_repo_info(github_url)
#     default_branch = get_default_branch(owner, repo)

#     if default_branch:
#         file_structure = get_repo_file_structure(owner, repo, default_branch)
#         read_me_path = get_root_readme_path(file_structure)
#         readme = get_file_raw(owner, repo, default_branch, read_me_path)
#         if len(readme) > 30000:
#             readme = readme[:30000]
#         if len(file_structure) > 20000:
#             file_structure = file_structure[:20000]
#         return readme, file_structure


if __name__ == "__main__":
    # Replace with your GitHub URL
    github_url = 'https://github.com/Stability-AI/generative-models'

    scraper = GitHubScraper(github_url)
    print(scraper.root_readme)
    print(scraper.file_paths)
