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


def get_repo_file_structure(owner, repo, branch=None, condese=False):
    if not branch:
        branch = get_default_branch(owner, repo)
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        files = map(lambda x: x['path'], data['tree'])
        if condese:
            files = condense_file_structure(files)
        return files
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


def get_root_readme_path(file_structure):
    for file in file_structure:
        if file['path'][-9:] == 'README.md':
            return file['path']


def get_readme_path(file_structure):
    output = []
    for file in file_structure:
        # print(file['path'][-9:] )
        if file['path'][-9:] == 'README.md':
            output.append(file['path'])
    return output


def condense_file_structure(file_paths):
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

    owner, repo = get_github_repo_info(github_url)
    default_branch = get_default_branch(owner, repo)

    if default_branch:
        file_structure = get_repo_file_structure(owner, repo, default_branch)
        read_me_path = get_root_readme_path(file_structure)
        readme = get_file_raw(owner, repo, default_branch, read_me_path)
        # print(readme)
        # output_file = "combined-readmes.txt"
        # with open(output_file, 'a', encoding='utf-8') as file:
        #     for file_path in read_me_path:
        #         curr_readme_file = get_file_raw(owner, repo, default_branch, file_path)
        #         file.write(curr_readme_file + "\n\n") 
        if file_structure:
            # print(file_structure)
            items = []
            for item in file_structure:
                items.append(item['path'])
            cond_fs = condense_file_structure(items)
            print(cond_fs)
        # if file_structure:
        #     items = []
        #     for item in file_structure:
        #         items.append(item['path'])

        #     condensed_output = condense_file_structure(items)
        #     # write_condensed_structure_to_file(condensed_output, is_initial_call=True)
        #     cond_str = get_condensed_structure(condensed_output)
        #     print(cond_str)
