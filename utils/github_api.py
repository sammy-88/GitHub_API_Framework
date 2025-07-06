import requests
from .config import GITHUB_API_URL, HEADERS

def get_user():
    response = requests.get(f"{GITHUB_API_URL}/user", headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_repositories():
    response = requests.get(f"{GITHUB_API_URL}/user/repos", headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_branches(repo_name):
    response = requests.get(f"{GITHUB_API_URL}/repos/{get_user()['login']}/{repo_name}/branches", headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_pull_requests(repo_name):
    response = requests.get(f"{GITHUB_API_URL}/repos/{get_user()['login']}/{repo_name}/pulls", headers=HEADERS)
    response.raise_for_status()
    return response.json()

def create_pull_request(repo_name, head, base, title="New Pull Request"):
    data = {
        "title": title,
        "head": head,
        "base": base
    }
    response = requests.post(f"{GITHUB_API_URL}/repos/{get_user()['login']}/{repo_name}/pulls", headers=HEADERS, json=data)
    response.raise_for_status()
    return response.json()

def delete_pull_request(repo_name, pull_number):
    # GitHub doesn't allow direct deletion of PRs via the API
    raise NotImplementedError("GitHub API doesn't support deleting pull requests.")

def approve_pull_request(repo_name, pull_number):
    # GitHub API supports merging a PR as approval
    response = requests.put(f"{GITHUB_API_URL}/repos/{get_user()['login']}/{repo_name}/pulls/{pull_number}/merge", headers=HEADERS)
    response.raise_for_status()
    return response.json()

