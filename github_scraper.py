import requests

def get_github_repo_info(github_url):
    parts = github_url.split('/')
    owner = parts[-2]
    repo = parts[-1]
    return owner, repo

def get_default_branch(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('default_branch', 'master')
    else:
        print("Error fetching default branch:", response.status_code, response.text)
        return None

def get_repo_file_structure(owner, repo, branch='master'):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data['tree']
    else:
        print("Error:", response.status_code, response.text)
        return None

# Replace with your GitHub URL
github_url = 'https://github.com/lastmile-ai/aiconfig'

owner, repo = get_github_repo_info(github_url)
default_branch = get_default_branch(owner, repo)

if default_branch:
    file_structure = get_repo_file_structure(owner, repo, default_branch)
    if file_structure:
        for item in file_structure:
            print(item['path'])
