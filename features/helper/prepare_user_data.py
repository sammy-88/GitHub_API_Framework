from dotenv import load_dotenv
import os
import requests


# pip install --upgrade pip
# pip install -r requirements.txt

load_dotenv()
BASE_URL = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"token {TOKEN}"
}
USER_LOGIN = os.getenv("GITHUB_USERNAME")

def user_data_response():
    response = requests.get(f"{BASE_URL}/user", headers=HEADERS)
    return response.json()

def extract_user_login(response):
    return response['login']

def saved_user_login():
    return USER_LOGIN



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
