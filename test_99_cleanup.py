from dotenv import load_dotenv
import os
import requests
import pytest
import random

# pip install --upgrade pip
# pip install -r requirements.txt

load_dotenv()
BASE_URL = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {TOKEN}"}
USER_LOGIN = os.getenv("GITHUB_USERNAME")
REPO_PREFIX = "test-repo-api-"

def test_delete_repositories():
    # Отримуємо список репозиторіїв
    response = requests.get(f"{BASE_URL}/user/repos", headers=HEADERS)
    repos = response.json()

    # Фільтруємо репозиторії, які потрібно видалити
    test_repos = []

    for repo in repos:
        if REPO_PREFIX in repo.get("name", ""):
            test_repos.append(repo)

    # Видаляємо кожен знайдений репозиторій
    for repo in test_repos:
        repo_name = repo.get("name")
        if repo_name:
            delete_response = requests.delete(f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}", headers=HEADERS)
            if delete_response.status_code == 204:
                print(f"Репозиторій '{repo_name}' успішно видалено")
            else:
                print(f"Не вдалося видалити репозиторій '{repo_name}': {delete_response.status_code}, {delete_response.text}")
