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


def condense_file_structure(file_structure):
    condensed_structure = {}

    def add_to_structure(base_structure, path_segments):
        if len(path_segments) == 1:
            # Add the file to the '_files' list of the current structure
            base_structure.setdefault('_files', []).append(path_segments[0])
            return

        # The first segment is a directory
        directory = path_segments[0]

        # Ensure the directory has a dictionary entry
        if directory not in base_structure:
            base_structure[directory] = {}

        # Recursively add the rest of the path
        add_to_structure(base_structure[directory], path_segments[1:])

    for file_path in file_structure:
        path_segments = file_path.split('/')
        add_to_structure(condensed_structure, path_segments)

    return condensed_structure


def print_condensed_structure(structure, indent_level=0):
    for key, value in structure.items():
        if key == '_files':
            for file in value:
                print("  " * indent_level + file)
        else:
            print("  " * indent_level + key)
            if isinstance(value, dict):
                print_condensed_structure(value, indent_level + 1)



# Replace with your GitHub URL
github_url = 'https://github.com/Stability-AI/generative-models'

owner, repo = get_github_repo_info(github_url)
default_branch = get_default_branch(owner, repo)

if default_branch:
    file_structure = get_repo_file_structure(owner, repo, default_branch)

    read_me_path = get_readme(file_structure)
    for file in read_me_path:
        print(get_file_raw(owner, repo, default_branch, file))
    if file_structure:
        items = []
        for item in file_structure:
            # print(item['path'])
            items.append(item['path'])
        condensed_output = condense_file_structure(items)
        print_condensed_structure(condensed_output)
