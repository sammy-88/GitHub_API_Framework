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
def pull_request_deleted(repo_name, result):
    pull_number = result["number"]
    # Крок 5:Закриття pull request з нової гілки до дефолтної
    pr_payload = {
        "state": "closed"
    }
    pr_response = requests.patch(f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/pulls/{pull_number}",
                                 headers=HEADERS,
                                 json=pr_payload)
    return pr_response.json()