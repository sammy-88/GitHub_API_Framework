from dotenv import load_dotenv
import os
import requests
import base64


# pip install --upgrade pip
# pip install -r requirements.txt

load_dotenv()
BASE_URL = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"token {TOKEN}"
}
USER_LOGIN = os.getenv("GITHUB_USERNAME")

def default_branch_checking(repo_response):
    # Отримання дефолтної гілки (як правило, 'main' або 'master')
    default_branch = repo_response.get("default_branch", "main")
    return default_branch

def create_commit(repo_name):
    # Крок 2: Initial commit - створення файлу README.md у дефолтній гілці
    file_path = "README.md"
    initial_content = f"# Initial Commit\n\nThis is the initial commit in the default branch."
    encoded_content = base64.b64encode(initial_content.encode("utf-8")).decode("utf-8")
    commit_payload = {
        "message": f"Initial commit",
        "content": encoded_content
    }
    commit_url = f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/contents/{file_path}"
    commit_response = requests.put(commit_url, headers=HEADERS, json=commit_payload)
    assert commit_response.status_code in (200, 201), f"Initial commit failed. Статус: {commit_response.status_code}"
    commit_data = commit_response.json()
    initial_commit_sha = commit_data["commit"]["sha"]
    return initial_commit_sha

def create_branch(repo_name, initial_commit_sha, branch_name):
    # Крок 3: Створення нової гілки, базованої на SHA initial commit
    branch_payload = {
        "ref": f"refs/heads/{branch_name}",
        "sha": initial_commit_sha
    }
    branch_creation_url = f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/git/refs"
    branch_response = requests.post(branch_creation_url, headers=HEADERS, json=branch_payload)
    return branch_response.json()

#
# # Крок 4: Коміт у новій гілці - додавання файлу branch_file.txt
# new_file_path = "branch_file.txt"
# new_file_content = "This file is added in the new branch."
# encoded_new_file_content = base64.b64encode(new_file_content.encode("utf-8")).decode("utf-8")
# new_commit_payload = {
#     "message": "Commit on new branch: Add branch_file.txt",
#     "content": encoded_new_file_content,
#     "branch": branch_name  # вказуємо, що коміт робиться саме в цій гілці
# }
# new_commit_url = f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/contents/{new_file_path}"
# new_commit_response = requests.put(new_commit_url, headers=HEADERS, json=new_commit_payload)
# assert new_commit_response.status_code in (
#     200, 201), f"Коміт у новій гілці не вдалося. Статус: {new_commit_response.status_code}"
# new_commit_data = new_commit_response.json()
# new_commit_sha = new_commit_data.get("commit", {}).get("sha")
# print(f"New branch commit SHA: {new_commit_sha}")
#
# # Перевірка: отримання файлу з нової гілки
# branch_file_get_url = f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/contents/{new_file_path}?ref={branch_name}"
# file_get_response = requests.get(branch_file_get_url, headers=HEADERS)
# assert file_get_response.status_code == 200, f"Не вдалося отримати файл з нової гілки. Статус: {file_get_response.status_code}"
# encoded_content = file_get_response.json()["content"]
# decoded_content = base64.b64decode(encoded_content).decode("utf-8")
# assert decoded_content == new_file_content