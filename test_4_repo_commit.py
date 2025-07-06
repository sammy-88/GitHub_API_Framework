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

def test_create_repo_with_initial_commit(repo_name):
    # Крок 1: Створення нового репозиторію
    payload = {
        "name": repo_name,
        "description": "Repository created via API test with an initial commit.",
        "private": False
    }
    create_response = requests.post(f"{BASE_URL}/user/repos", headers=HEADERS, json=payload)
    assert create_response.status_code == 201, (
        f"Не вдалося створити репозиторій. Статус: {create_response.status_code}"
    )
    repo_data = create_response.json()
    print(f"Repository created: {repo_data.get('html_url')}")

    # Крок 2: Створення initial commit шляхом додавання файлу README.md
    file_path = "README.md"
    content = (
        "# Welcome to My Repository\n\n"
        "This is the initial commit created via API test."
    )
    # Кодування вмісту файлу у Base64
    content_encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    commit_payload = {
        "message": "Initial commit",
        "content": content_encoded
    }
    commit_url = f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/contents/{file_path}"
    commit_response = requests.put(commit_url, headers=HEADERS, json=commit_payload)
    assert commit_response.status_code in (200, 201), (
        f"Не вдалося зробити commit. Статус: {commit_response.status_code}"
    )
    commit_data = commit_response.json()
    commit_html_url = commit_data.get("commit", {}).get("html_url", "URL не надано")
    print(f"Initial commit created: {commit_html_url}")

    # Опціонально: перевірка, що файл дійсно існує в репозиторії
    file_get_response = requests.get(commit_url, headers=HEADERS)
    assert file_get_response.status_code == 200, "Не вдалося отримати файл з репозиторію"
    file_info = file_get_response.json()
    assert file_info.get("content") is not None, "Вміст файлу відсутній"

    clean_up_repos()

def test_create_repo_with_two_commits(repo_name):
    # Крок 1: Створення нового репозиторію
    payload = {
        "name": repo_name,
        "description": "Repository for testing two commits",
        "private": False
    }
    create_response = requests.post(f"{BASE_URL}/user/repos", headers=HEADERS, json=payload)
    assert create_response.status_code == 201, f"Не вдалося створити репозиторій. Статус: {create_response.status_code}"
    repo_data = create_response.json()
    print(f"Repository created: {repo_data.get('html_url')}")

    # Крок 2: Initial commit - створення файлу README.md
    file_path1 = "README.md"
    initial_content = (
        "# Initial Commit\n\n"
        "This is the initial commit with a README file."
    )
    content_encoded1 = base64.b64encode(initial_content.encode("utf-8")).decode("utf-8")
    commit_payload1 = {
        "message": "Initial commit",
        "content": content_encoded1
    }
    commit_url1 = f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/contents/{file_path1}"
    commit_response1 = requests.put(commit_url1, headers=HEADERS, json=commit_payload1)
    assert commit_response1.status_code in (200, 201), f"Initial commit failed. Статус: {commit_response1.status_code}"
    commit_data1 = commit_response1.json()
    print(f"Initial commit URL: {commit_data1.get('commit', {}).get('html_url')}")

    # Крок 3: Другий коміт - додавання файлу second_file.txt
    file_path2 = "second_file.txt"
    second_content = "This is the second commit adding a new file."
    content_encoded2 = base64.b64encode(second_content.encode("utf-8")).decode("utf-8")
    commit_payload2 = {
        "message": "Second commit: Add second_file.txt",
        "content": content_encoded2
    }
    commit_url2 = f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/contents/{file_path2}"
    commit_response2 = requests.put(commit_url2, headers=HEADERS, json=commit_payload2)
    assert commit_response2.status_code in (200, 201), f"Second commit failed. Статус: {commit_response2.status_code}"
    commit_data2 = commit_response2.json()
    print(f"Second commit URL: {commit_data2.get('commit', {}).get('html_url')}")

    # Опціонально: перевірка, що другий файл існує
    file_get_response = requests.get(commit_url2, headers=HEADERS)
    assert file_get_response.status_code == 200, f"Не вдалося отримати файл {file_path2}. Статус: {file_get_response.status_code}"

    clean_up_repos()
