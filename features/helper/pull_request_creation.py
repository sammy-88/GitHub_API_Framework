import base64
import os
import random
import requests
import pytest
from dotenv import load_dotenv

# pip install --upgrade pip
# pip install -r requirements.txt

# Завантаження змінних оточення з файлу .env
load_dotenv()

# Конфігурація
BASE_URL = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN")
USER_LOGIN = os.getenv("GITHUB_USERNAME")
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
def create_pull_request(repo_name, default_branch, branch_name):
    pr_payload = {
    "title": f"Merge {branch_name} into {default_branch}",
    "head": branch_name,  # гілка з якої робиться pull request
    "base": default_branch,  # цільова гілка
    "body": "This pull request is created by automated API test."
    }
    pr_response = requests.post(f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/pulls", headers=HEADERS,
                                    json=pr_payload)
    # TODO separate assert from function
    assert pr_response.status_code == 201, f"Створення pull request не вдалося. Статус: {pr_response.status_code}"
    pr_data = pr_response.json()
    pr_html_url = pr_data.get("html_url")

    return pr_data