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

@pytest.fixture
def repo_name():
    """Фікстура для генерації унікального імені репозиторію."""
    random_number = random.randint(1000000, 9999999)
    return f"test-repo-api-{random_number}"

def create_branches(repo_name, default_branch, initial_commit_sha, count=1):
    branch_name = f"feature-branch-{random.randint(1000, 9999)}"
    branch_name_template = branch_name
    branches_name = []
    for i in range(count):
        branch_name = branch_name_template
        if count == 1:
            branch_name = f'{branch_name}'
            branches_name.append(branch_name)
        else:
            branch_name = f'{branch_name}-{i}'
            branches_name.append(branch_name)
        # Крок 3: Створення нової гілки, базованої на SHA initial commit
        branch_payload = {
            "ref": f"refs/heads/{branch_name}",
            "sha": initial_commit_sha
        }
        branch_creation_url = f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/git/refs"
        branch_response = requests.post(branch_creation_url, headers=HEADERS, json=branch_payload)
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
        encoded_content = file_get_response.json()["content"]
        decoded_content = base64.b64decode(encoded_content).decode("utf-8")
        assert decoded_content == new_file_content

    return repo_name, default_branch, branches_name