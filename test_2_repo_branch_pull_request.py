import base64
import os
import random
import requests
import pytest
from dotenv import load_dotenv
from clean_up_99 import clean_up_repos
from create_repos_11 import create_repos

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


@pytest.fixture
def repo_name():
    """Фікстура для генерації унікального імені репозиторію."""
    random_number = random.randint(1000000, 9999999)
    return f"test-repo-api-{random_number}"


def test_create_branch_and_pull_request(repo_name):
    default_branch, initial_commit_sha = create_repos(repo_name)

    # Крок 3: Створення нової гілки, базованої на SHA initial commit
    branch_name = f"feature-branch-{random.randint(1000, 9999)}"
    branch_payload = {
        "ref": f"refs/heads/{branch_name}",
        "sha": initial_commit_sha
    }
    branch_response = requests.post(f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/git/refs", headers=HEADERS,
                                    json=branch_payload)
    assert branch_response.status_code == 201, f"Створення гілки не вдалося. Статус: {branch_response.status_code}"
    print(f"New branch '{branch_name}' created.")

    # Крок 4: Коміт у новій гілці - додавання файлу branch_file.txt
    new_file_path = "branch_file.txt"
    new_file_content = "This file is added in the new branch."
    encoded_new_file_content = base64.b64encode(new_file_content.encode("utf-8")).decode("utf-8")
    new_commit_payload = {
        "message": "Commit on new branch: Add branch_file.txt",
        "content": encoded_new_file_content,
        "branch": branch_name  # вказуємо, що коміт робиться саме в цій гілці
    }
    new_commit_url = f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/contents/{new_file_path}"
    new_commit_response = requests.put(new_commit_url, headers=HEADERS, json=new_commit_payload)
    assert new_commit_response.status_code in (
    200, 201), f"Коміт у новій гілці не вдалося. Статус: {new_commit_response.status_code}"
    new_commit_data = new_commit_response.json()
    new_commit_sha = new_commit_data.get("commit", {}).get("sha")
    print(f"New branch commit SHA: {new_commit_sha}")

    # Перевірка: отримання файлу з нової гілки
    branch_file_get_url = f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/contents/{new_file_path}?ref={branch_name}"
    file_get_response = requests.get(branch_file_get_url, headers=HEADERS)
    assert file_get_response.status_code == 200, f"Не вдалося отримати файл з нової гілки. Статус: {file_get_response.status_code}"

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

    clean_up_repos()
