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

def test_create_branch_merge_pull_request(repo_name):
    default_branch, initial_commit_sha = create_repos(repo_name)

    # Крок 3: Створення нової гілки, базованої на SHA initial commit
    branch_name = f"feature-branch-{random.randint(1000, 9999)}"
    branch_payload = {
        "ref": f"refs/heads/{branch_name}",
        "sha": initial_commit_sha
    }
    branch_response = requests.post(f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/git/refs", headers=HEADERS, json=branch_payload)
    assert branch_response.status_code == 201, f"Створення гілки не вдалося. Статус: {branch_response.status_code}"
    print(f"New branch '{branch_name}' created.")

    # Крок 4: Коміт у новій гілці - додавання файлу branch_file.txt
    new_file_path = "branch_file.txt"
    new_file_content = "This is a commit on the new branch."
    encoded_new_file_content = base64.b64encode(new_file_content.encode("utf-8")).decode("utf-8")
    new_commit_payload = {
        "message": "Add branch_file.txt",
        "content": encoded_new_file_content,
        "branch": branch_name  # вказуємо, що коміт робиться саме в цій гілці
    }
    new_commit_url = f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/contents/{new_file_path}"
    new_commit_response = requests.put(new_commit_url, headers=HEADERS, json=new_commit_payload)
    assert new_commit_response.status_code in (200, 201), f"Коміт у новій гілці не вдалося. Статус: {new_commit_response.status_code}"
    new_commit_data = new_commit_response.json()
    print(f"New branch commit SHA: {new_commit_data.get('commit', {}).get('sha')}")

    # Крок 5: Створення pull request з нової гілки до дефолтної
    pr_payload = {
        "title": f"Merge {branch_name} into {default_branch}",
        "head": branch_name,
        "base": default_branch,
        "body": "This pull request is created by an automated API test."
    }
    pr_response = requests.post(f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/pulls", headers=HEADERS, json=pr_payload)
    assert pr_response.status_code == 201, f"Створення pull request не вдалося. Статус: {pr_response.status_code}"
    pr_data = pr_response.json()
    pr_number = pr_data.get("number")
    print(f"Pull request created: {pr_data.get('html_url')} (PR #{pr_number})")

    # Крок 6: Merge pull request
    merge_payload = {
        "commit_title": f"Merge pull request #{pr_number} from {branch_name}",
        "commit_message": "Merged by automated test."
    }
    merge_url = f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/pulls/{pr_number}/merge"
    merge_response = requests.put(merge_url, headers=HEADERS, json=merge_payload)
    assert merge_response.status_code in (200, 201), f"Merge pull request failed. Статус: {merge_response.status_code}"
    merge_data = merge_response.json()
    assert merge_data.get("merged") is True, "Pull request was not merged"
    print(f"Pull request #{pr_number} merged successfully.")

    # Крок 7: Перевірка, що зміни з нової гілки з'явилися у дефолтній гілці
    file_get_url = f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/contents/{new_file_path}?ref={default_branch}"
    file_get_response = requests.get(file_get_url, headers=HEADERS)
    assert file_get_response.status_code == 200, f"Файл {new_file_path} не знайдено у дефолтній гілці після merge. Статус: {file_get_response.status_code}"

    # Перевірка: отримання файлу з нової гілки
    file_get_url = f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/contents/{new_file_path}?ref={default_branch}"
    file_get_response = requests.get(file_get_url, headers=HEADERS)
    assert file_get_response.status_code == 200, f"Не вдалося отримати файл з нової гілки. Статус: {file_get_response.status_code}"
    encoded_content = file_get_response.json()["content"]
    decoded_content = base64.b64decode(encoded_content).decode("utf-8")
    assert decoded_content == new_file_content

    clean_up_repos()

