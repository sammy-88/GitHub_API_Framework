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

def create_repo_by_name(repo_name):
    payload = {"name": repo_name, "private": False}
    response = requests.post(f"{BASE_URL}/user/repos", headers=HEADERS, json=payload)
    return response.json()

def delete_repo_by_name(repo_name):
    requests.delete(f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}",
                    headers=HEADERS)