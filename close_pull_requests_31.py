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
def close_pull_requests(repo_name, results):
    for result in results:
        pull_number = result["number"]
        # Крок 5:Закриття pull request з нової гілки до дефолтної
        pr_payload = {
            "state": "closed"
        }
        pr_response = requests.patch(f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/pulls/{pull_number}", headers=HEADERS,
                                    json=pr_payload)