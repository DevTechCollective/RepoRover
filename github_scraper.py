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

def get_file_raw(owner, repo, branch, file_path):
    url = f'https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}'
    headers = {'Accept': 'application/vnd.github.v3.raw'}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve file: {response.status_code}")
        return None

def get_readme(file_structure):
    output = []
    for file in file_structure:
        #print(file['path'][-9:] )
        if file['path'][-9:] == 'README.md':
            output.append(file['path'])
    return output





# Replace with your GitHub URL
github_url = 'https://github.com/lastmile-ai/aiconfig'

owner, repo = get_github_repo_info(github_url)
default_branch = get_default_branch(owner, repo)

if default_branch:
    file_structure = get_repo_file_structure(owner, repo, default_branch)

    read_me_path = get_readme(file_structure)
    for file in read_me_path:
        print(get_file_raw(owner, repo, default_branch, file))
    if file_structure:
        for item in file_structure:
            #print(item['path'])
            pass