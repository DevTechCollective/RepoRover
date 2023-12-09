import requests

owner = 'calcom'
repo = 'cal.com'
path = ''  # Use empty string for root directory
branch = 'main'

url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}' # Replace with the API URL you're calling



url += "?q=language:python"
header = {"Accept": "application/vnd.github.v3+json"}
response = requests.get(url, headers=header)

commit_sha = response.json()['object']['sha']
tree_url = f'https://api.github.com/repos/{owner}/{repo}/git/trees/{commit_sha}?recursive=1'
tree_response = requests.get(tree_url)

# print(f"Status code: {response.status_code}")
# with open ("response.txt", "w", encoding="utf-8") as f:
#     f.write(response.text)

# print(response.text)

# Check if the request was successful
if tree_response.status_code == 200:
    tree = tree_response.json()
    for item in tree['tree']:
        print(item['path'])  # This will print the path of every item in the repository
else:
    print(f"Failed to retrieve tree: {tree_response.status_code}")
