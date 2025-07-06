import base64
import os
import random
import requests
import pytest
from dotenv import load_dotenv
from clean_up_99 import clean_up_repos

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

def test_five_branches_with_unique_files(repo_name):
    # Крок 1: Створення нового репозиторію
    payload = {
        "name": repo_name,
        "description": "Repository for testing 5 branches with unique files",
        "private": False
    }
    create_response = requests.post(f"{BASE_URL}/user/repos", headers=HEADERS, json=payload)
    assert create_response.status_code == 201, f"Не вдалося створити репозиторій. Статус: {create_response.status_code}"
    repo_data = create_response.json()
    print(f"Repository created: {repo_data.get('html_url')}")

    # Крок 2: Initial commit у дефолтній гілці (створення файлу README.md)
    file_path = "README.md"
    initial_content = "# Initial Commit\n\nThis is the initial commit."
    encoded_content = base64.b64encode(initial_content.encode("utf-8")).decode("utf-8")
    commit_payload = {
        "message": "Initial commit",
        "content": encoded_content
    }
    commit_url = f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/contents/{file_path}"
    commit_response = requests.put(commit_url, headers=HEADERS, json=commit_payload)
    assert commit_response.status_code in (200, 201), f"Initial commit failed. Статус: {commit_response.status_code}"
    commit_data = commit_response.json()
    initial_commit_sha = commit_data["commit"]["sha"]
    print(f"Initial commit SHA: {initial_commit_sha}")

    # Крок 3: Створення 5 нових гілок та додавання унікального файлу в кожну з них
    branch_names = [f"branch-{i}" for i in range(1, 6)]
    for branch in branch_names:
        # Створення нової гілки на базі initial commit
        branch_payload = {
            "ref": f"refs/heads/{branch}",
            "sha": initial_commit_sha
        }
        branch_response = requests.post(f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/git/refs", headers=HEADERS, json=branch_payload)
        assert branch_response.status_code == 201, f"Не вдалося створити гілку '{branch}'. Статус: {branch_response.status_code}"
        print(f"Branch '{branch}' created.")

        # Додавання унікального файлу в цю гілку
        # Ім'я файлу: <branch>_unique.txt, вміст: "This is the unique file for <branch>."
        unique_file = f"{branch}_unique.txt"
        file_content = f"This is the unique file for {branch}."
        encoded_file_content = base64.b64encode(file_content.encode("utf-8")).decode("utf-8")
        file_commit_payload = {
            "message": f"Add {unique_file} to {branch}",
            "content": encoded_file_content,
            "branch": branch  # коміт робиться саме в цій гілці
        }
        file_commit_url = f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/contents/{unique_file}"
        file_commit_response = requests.put(file_commit_url, headers=HEADERS, json=file_commit_payload)
        assert file_commit_response.status_code in (200, 201), f"Не вдалося додати файл {unique_file} в гілці {branch}. Статус: {file_commit_response.status_code}"
        print(f"Unique file '{unique_file}' added to branch '{branch}'.")

    # Крок 4: Перевірка, що всі 5 гілок створено та містять відповідний файл
    branches_response = requests.get(f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/branches", headers=HEADERS)
    assert branches_response.status_code == 200, f"Не вдалося отримати список гілок. Статус: {branches_response.status_code}"
    branches = branches_response.json()
    returned_branch_names = [branch_obj["name"] for branch_obj in branches]

    for branch in branch_names:
        assert branch in returned_branch_names, f"Гілка '{branch}' не знайдена у репозиторії."
        # Перевірка наявності унікального файлу в гілці
        unique_file = f"{branch}_unique.txt"
        file_url = f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/contents/{unique_file}?ref={branch}"
        file_response = requests.get(file_url, headers=HEADERS)
        assert file_response.status_code == 200, f"Файл '{unique_file}' не знайдено в гілці '{branch}'. Статус: {file_response.status_code}"
        print(f"Verified: Branch '{branch}' contains file '{unique_file}'.")

    # Опціонально: перевіримо, що серед повернених гілок є рівно 5 створених нами гілок (як мінімум)
    created_branches_count = sum(1 for branch in returned_branch_names if branch in branch_names)
    assert created_branches_count == 5, f"Очікувалось 5 створених гілок, знайдено {created_branches_count}."

    clean_up_repos()
