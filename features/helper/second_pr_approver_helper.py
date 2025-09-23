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
# APPROVER_TOKEN = os.getenv("GITHUB_REVIEWER_TOKEN")
# APPROVER_LOGIN = os.getenv("GITHUB_REVIEWER_USERNAME")

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
def create_invite_request(TOKEN, owner_login, repo_name, APPROVER_LOGIN):
    return _github_request(
        TOKEN,
        "PUT",
        f"{BASE_URL}/repos/{owner_login}/{repo_name}/collaborators/{APPROVER_LOGIN}",
        json={"permission": "push"},
    )