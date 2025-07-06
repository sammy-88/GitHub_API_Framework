from behave import given, when, then
import requests
from features.helper.prepare_user_data import user_data_response, saved_user_login, extract_user_login


@given('I receive user data info request')
def receive_user_data(context):
    user_data = user_data_response()
    context.user_data = user_data


@when('I compare user login with saved')
def compare_user_login(context):
    context.saved_user_login = saved_user_login()
    context.github_user_login = extract_user_login(context.user_data)


@when('I compare user login with custom "{user_login}"')
def compare_user_login(context, user_login):
    context.saved_user_login = user_login
    context.github_user_login = extract_user_login(context.user_data)


@then('I assert that user login as expected')
def assert_user_login(context):
    assert context.github_user_login == context.saved_user_login, f"{context.github_user_login} != {context.saved_user_login}"

# from dotenv import load_dotenv
# import os
# import requests
# import pytest
# import random
#
# # pip install --upgrade pip
# # pip install -r requirements.txt
#
# load_dotenv()
# BASE_URL = "https://api.github.com"
# TOKEN = os.getenv("GITHUB_TOKEN")
# HEADERS = {
#     "Authorization": f"token {TOKEN}"
# }
# USER_LOGIN = os.getenv("GITHUB_USERNAME")
#
#
# @pytest.fixture
# def repo_name():
#     """Фікстура для генерації імені репозиторію."""
#     random_number = str(random.randint(1000000, 9999999))
#     return "test-repo-api-" + random_number
#
#
# @pytest.fixture
# def repo_name1():
#     """Фікстура для генерації імені репозиторію."""
#     random_number = random.randint(1000000, 9999999)
#     return f"test-repo-api-{random_number}"
#
#
# def test_get_user_info():
#     """Тест на отримання інформації про поточного користувача."""
#     response = requests.get(f"{BASE_URL}/user", headers=HEADERS)
#     assert response.status_code == 200, "Не вдалося отримати інформацію про користувача"
#     user_data = response.json()
#     assert "login" in user_data, "Поле 'login' відсутнє в відповіді"
#     print(f"User login: {user_data['login']}")
