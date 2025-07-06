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

def test_check_all_repos(repo_name):
    #preconditions
    repo_name_template = repo_name
    for i in range(10):
        repo_name = repo_name_template
        repo_name = f'{repo_name}-{i}'
        # Крок 1: Створення нового репозиторію
        payload = {
            "name": repo_name,
            "description": "Repo for testing pull request merge",
            "private": False
        }
        create_response = requests.post(f"{BASE_URL}/user/repos", headers=HEADERS, json=payload)
        assert create_response.status_code == 201, f"Не вдалося створити репозиторій. Статус: {create_response.status_code}"
        repo_data = create_response.json()
        print(f"Repository created: {repo_data.get('html_url')}")

        # Отримання дефолтної гілки (як правило, 'main' або 'master')
        default_branch = repo_data.get("default_branch", "main")

        # Крок 2: Initial commit - створення файлу README.md у дефолтній гілці
        file_path = "README.md"
        initial_content = f"{i}# Initial Commit\n\nThis is the initial commit in the default branch."
        encoded_content = base64.b64encode(initial_content.encode("utf-8")).decode("utf-8")
        commit_payload = {
            "message": f"Initial commit {i}",
            "content": encoded_content
        }
        commit_url = f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/contents/{file_path}"
        commit_response = requests.put(commit_url, headers=HEADERS, json=commit_payload)
        assert commit_response.status_code in (200, 201), f"Initial commit failed. Статус: {commit_response.status_code}"
        commit_data = commit_response.json()
        initial_commit_sha = commit_data["commit"]["sha"]
        print(f"Initial commit SHA: {initial_commit_sha}")

    """Тест на отримання списку репозиторіїв користувача."""
    response = requests.get(f"{BASE_URL}/user/repos", headers=HEADERS)
    assert response.status_code == 200, "Не вдалося отримати список репозиторіїв"
    repos = response.json()
    assert isinstance(repos, list), "Відповідь не є списком"
    print(f"Found {len(repos)} repositories")
    count = 0
    for repo in repos:
        current_repo_name = repo["name"]
        if repo_name_template in current_repo_name:
            count += 1
    assert count == 10
    print(f"Found {count} recently created repositories")
    clean_up_repos()


