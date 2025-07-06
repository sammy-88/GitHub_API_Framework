import base64
import os
import random
import requests
import pytest
from dotenv import load_dotenv

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

def create_pull_requests(repo_name, default_branch, branches_name):
    results = []
    for branch_name in branches_name:
        # Крок 5: Створення pull request з нової гілки до дефолтної
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
        assert branch_name in pr_data['title']
        results.append(pr_data)

    return results