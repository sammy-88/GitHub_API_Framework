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
HEADERS = {
    "Authorization": f"token {TOKEN}"
}
USER_LOGIN = os.getenv("GITHUB_USERNAME")


@pytest.fixture
def repo_name():
    """Фікстура для генерації імені репозиторію."""
    random_number = str(random.randint(1000000, 9999999))
    return "test-repo-api-" + random_number


@pytest.fixture
def repo_name1():
    """Фікстура для генерації імені репозиторію."""
    random_number = random.randint(1000000, 9999999)
    return f"test-repo-api-{random_number}"


def test_get_user_info():
    """Тест на отримання інформації про поточного користувача."""
    response = requests.get(f"{BASE_URL}/user", headers=HEADERS)
    assert response.status_code == 200, "Не вдалося отримати інформацію про користувача"
    user_data = response.json()
    assert "login" in user_data, "Поле 'login' відсутнє в відповіді"
    print(f"User login: {user_data['login']}")


def test_check_user_login():
    response = requests.get(f"{BASE_URL}/user", headers=HEADERS)
    assert response.status_code == 200, "Не вдалося отримати інформацію про користувача"
    user_data = response.json()
    assert "login" in user_data, "Поле 'login' відсутнє в відповіді"
    assert user_data['login'] == USER_LOGIN


# Написать тест для проверки своего id

def test_create_repository(repo_name):
    """Тест на створення нового репозиторію."""
    payload = {"name": repo_name, "private": False}
    response = requests.post(f"{BASE_URL}/user/repos", headers=HEADERS, json=payload)
    assert response.status_code == 201, "Не вдалося створити репозиторій"
    repo_data = response.json()
    assert repo_data["name"] == repo_name, "Ім'я репозиторія не збігається"

    print(f"Repository '{repo_name}' created successfully")

    # Postcondition
    requests.delete(f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}",
                    headers=HEADERS)
    assert response.status_code == 201


# Тест на проверку приватный ли репозиторий ( 2 теста, на приватный и публичный )

def test_get_repositories():
    """Тест на отримання списку репозиторіїв користувача."""
    response = requests.get(f"{BASE_URL}/user/repos", headers=HEADERS)
    assert response.status_code == 200, "Не вдалося отримати список репозиторіїв"
    repos = response.json()
    assert isinstance(repos, list), "Відповідь не є списком"
    print(f"Found {len(repos)} repositories")


def test_get_new_repositories(repo_name):
    # Precondition
    # 3 репозитория

    # a
    payload = {"name": (repo_name + '-a'), "private": False}
    requests.post(f"{BASE_URL}/user/repos", headers=HEADERS, json=payload)

    # b
    payload = {"name": (repo_name + '-b'), "private": False}
    requests.post(f"{BASE_URL}/user/repos", headers=HEADERS, json=payload)

    # c
    payload = {"name": (repo_name + '-c'), "private": False}
    requests.post(f"{BASE_URL}/user/repos", headers=HEADERS, json=payload)

    """Тест на отримання списку репозиторіїв користувача."""
    response = requests.get(f"{BASE_URL}/user/repos", headers=HEADERS)
    assert response.status_code == 200, "Не вдалося отримати список репозиторіїв"
    repos = response.json()
    assert isinstance(repos, list), "Відповідь не є списком"
    print(f"Found {len(repos)} repositories")

    # Postcondition
    # Добавить по аналогии с прошлым


def test_delete_repository(repo_name):
    """Тест на видалення репозиторію."""
    # Precondition
    # Створюємо репозиторій, якщо його ще немає
    payload = {"name": repo_name, "private": False}
    response = requests.post(f"{BASE_URL}/user/repos", headers=HEADERS, json=payload)
    assert response.status_code == 201, "Не вдалося створити репозиторій"
    repo_data = response.json()
    assert repo_data["name"] == repo_name, "Ім'я репозиторія не збігається"

    print(f"Repository '{repo_name}' created successfully")
    # Видаляємо репозиторій
    response = requests.delete(
        f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}",
        headers=HEADERS)
    assert response.status_code == 204, "Не вдалося видалити репозиторій"
    print(f"Repository '{repo_name}' deleted successfully")
