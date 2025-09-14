from dotenv import load_dotenv
import os
import requests
import base64


# pip install --upgrade pip
# pip install -r requirements.txt

load_dotenv()
BASE_URL = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"token {TOKEN}"
}
USER_LOGIN = os.getenv("GITHUB_USERNAME")

def create_pull_request1(repo_name, default_branch, branch_name):
# Крок 5: Створення pull request з нової гілки до дефолтної
    pr_payload = {
        "title": f"Merge {branch_name} into {default_branch}",
        "head": branch_name,  # гілка з якої робиться pull request
        "base": default_branch,  # цільова гілка
        "body": "This pull request is created by automated API test."
    }
    pr_response = requests.post(f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/pulls", headers=HEADERS, json=pr_payload)
    assert pr_response.status_code == 201, f"Створення pull request не вдалося. Статус: {pr_response.status_code}"
    pr_data = pr_response.json()
    pr_html_url = pr_data.get("html_url")
    print(f"Pull request created: {pr_html_url}")

    return pr_data
