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

def test_check_all_repos(repo_name):
    #preconditions
    create_repos(repo_name, 10)

    repo_name_template = repo_name
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


