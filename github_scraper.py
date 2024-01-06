import requests

IGNORE_EXTS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.mp4', '.mp3',
               '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.tar', '.gz', '.rar',
               '.7z', '.exe', '.dll', '.jar', '.war', '.class']


class GitHubScraper:

    def __init__(self, github_url, branch=None, condensed=False):
        self.github_url = github_url
        self.owner, self.repo = self.get_github_repo_info()
        self.branch = self.get_default_branch() if branch is None else branch

        self.root_readme = ""
        self.file_paths = []
        self.set_files(condensed)
        self.file_contents = {}

    # Getters
    def get_repo_name(self):
        return self.repo

    def get_file_paths(self):
        return self.file_paths

    def get_readme(self):
        return self.root_readme

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

    def set_files(self, condensed=False):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/trees/{self.branch}?recursive=1"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            files = []
            for file in data['tree']:
                if file['type'] == 'blob':
                    file_name = file['path'].lower()
                    file_extension = file_name.split('.')[-1]
                    if file_extension not in IGNORE_EXTS:
                        if file_name == 'readme.md':
                            # must use correct casing to get file
                            self.root_readme = self.get_file_raw(file['path'])  
                        files.append(file['path'])
            if condensed:
                files = self._condense_file_structure(files)
            self.file_paths = files
        else:
            print("Error:", response.status_code, response.text)

    def get_file_raw(self, file_path):
        if file_path in self.file_contents:
            return self.file_contents[file_path]

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


if __name__ == "__main__":
    # Replace with your GitHub URL
    github_url = 'https://github.com/Stability-AI/generative-models'

    scraper = GitHubScraper(github_url)
    print(scraper.root_readme)
    print(scraper.file_paths)
