import os
import requests
from dotenv import load_dotenv
import base64

load_dotenv()
BASE_URL = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
USER_LOGIN = os.getenv("GITHUB_USERNAME")

def _github_request(token: str, method: str, url: str, **kwargs):
    headers = kwargs.pop("headers", {})
    headers.update({
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    return requests.request(method, url, headers=headers, timeout=15, **kwargs)

def repo_creation(repo_name):
    return _github_request(
            TOKEN,
            "POST",
            f"{BASE_URL}/user/repos",
            json={"name": repo_name, "auto_init": True, "private": False},
        )
def invite_collaborator(owner_login, repo_name, APPROVER_LOGIN):
    return _github_request(
        TOKEN,
        "PUT",
        f"{BASE_URL}/repos/{owner_login}/{repo_name}/collaborators/{APPROVER_LOGIN}",
        json={"permission": "push"},
    )
def check_invitations(APPROVER_TOKEN):
    return _github_request(APPROVER_TOKEN,
        "GET",
        f"{BASE_URL}/user/repository_invitations")

def check_invitation_id(APPROVER_TOKEN,inv_id):
    return _github_request(
        APPROVER_TOKEN,
        "PATCH",
        f"{BASE_URL}/user/repository_invitations/{inv_id}",
    )
def take_sha_commit_of_main_branch(owner_login, repo_name, default_branch):
    return _github_request(
        TOKEN,
        "GET",
        f"{BASE_URL}/repos/{owner_login}/{repo_name}/git/ref/heads/{default_branch}",
    ).json()["object"]["sha"]

def creation_branch_with_name(owner_login, repo_name, branch_name, main_sha):
    return _github_request(
        TOKEN,
        "POST",
        f"{BASE_URL}/repos/{owner_login}/{repo_name}/git/refs",
        json={"ref": f"refs/heads/{branch_name}", "sha": main_sha},
    )

def add_new_file(owner_login, repo_name, branch_name):
    return _github_request(
        TOKEN,
        "PUT",
        f"{BASE_URL}/repos/{owner_login}/{repo_name}/contents/hello.py",
        json={
            "message": "add hello",
            "content": base64.b64encode(b"print('hello')").decode(),
            "branch": branch_name,
        },
    )