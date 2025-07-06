from dotenv import load_dotenv
import os
import random
import requests
import pytest
from dotenv import load_dotenv
from clean_up_99 import clean_up_repos
from create_repos_11 import create_repos
from create_branches_12 import create_branches
from create_pull_requests_21 import create_pull_requests
from close_pull_requests_31 import close_pull_requests
# pip install --upgrade pip
# pip install -r requirements.txt

load_dotenv()
BASE_URL = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
USER_LOGIN = os.getenv("GITHUB_USERNAME")

@pytest.fixture
def repo_name():
    """Фікстура для генерації унікального імені репозиторію."""
    random_number = random.randint(1000000, 9999999)
    return f"test-repo-api-{random_number}"

# autorization
def test_get_user_info():
    """Тест на отримання інформації про поточного користувача."""
    response = requests.get(f"{BASE_URL}/user", headers=HEADERS)
    assert response.status_code == 200, "Не вдалося отримати інформацію про користувача"
    user_data = response.json()
    assert user_data["login"] == USER_LOGIN, "Логін користувача не відповідає очікуваному"


def test_create_repo_and_branches(repo_name):
    """Створення репозиторію та 10 гілок"""
    default_branch, initial_commit_sha = create_repos(repo_name)
    repo_name, default_branch, branches_name = create_branches(
        repo_name, default_branch, initial_commit_sha, count=10)

    branch_response = requests.get(
        f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/branches", headers=HEADERS)
    assert len(branch_response.json()) == 10 + 1

    clean_up_repos()


def test_creating_of_pull_requests(repo_name):
    default_branch, initial_commit_sha = create_repos(repo_name)
    repo_name, default_branch, branches_name = create_branches(
        repo_name, default_branch, initial_commit_sha, count=10)
    create_pull_requests(repo_name, default_branch, branches_name)

    clean_up_repos()


def test_delete_pull_requests(repo_name):
    default_branch, initial_commit_sha = create_repos(repo_name)
    repo_name, default_branch, branches_name = create_branches(
        repo_name, default_branch, initial_commit_sha, count=10)
    pr_list = create_pull_requests(repo_name, default_branch, branches_name)

    close_pull_requests(repo_name, pr_list)


# ===================  NEW END-TO-END FLOW  ===================

import time
import base64

APPROVER_TOKEN = os.getenv("GITHUB_REVIEWER_TOKEN")
APPROVER_LOGIN = os.getenv("GITHUB_REVIEWER_USERNAME")


def _gh_request(token: str, method: str, url: str, **kwargs):
    headers = kwargs.pop("headers", {})
    headers.update({
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    return requests.request(method, url, headers=headers, timeout=15, **kwargs)


@pytest.mark.skipif(
    not APPROVER_TOKEN or not APPROVER_LOGIN,
    reason="Не встановлені облікові дані ревʼювера",
)
def test_full_collaborator_flow(repo_name):
    """Створити репо → запросити колаборатора → PR → approve → merge"""

    r = _gh_request(
        TOKEN,
        "POST",
        f"{BASE_URL}/user/repos",
        json={"name": repo_name, "auto_init": True, "private": False},
    )
    assert r.status_code == 201, f"Не вдалося створити репозиторій: {r.text}"
    repo_data = r.json()
    owner_login = repo_data["owner"]["login"]
    default_branch = repo_data["default_branch"]

    invite = _gh_request(
        TOKEN,
        "PUT",
        f"{BASE_URL}/repos/{owner_login}/{repo_name}/collaborators/{APPROVER_LOGIN}",
        json={"permission": "push"},
    )
    assert invite.status_code in (201, 202), f"Invite error: {invite.text}"

    inv_resp = _gh_request(APPROVER_TOKEN, "GET", f"{BASE_URL}/user/repository_invitations")
    inv_id = next(
        (
            i["id"]
            for i in inv_resp.json()
            if i["repository"]["name"] == repo_name
        ),
        None,
    )
    assert inv_id, "Не знайдено запрошення"
    acc_resp = _gh_request(
        APPROVER_TOKEN,
        "PATCH",
        f"{BASE_URL}/user/repository_invitations/{inv_id}",
    )
    assert acc_resp.status_code == 204, f"Не вдалося прийняти запрошення: {acc_resp.text}"

    time.sleep(2)

    main_sha = _gh_request(
        TOKEN,
        "GET",
        f"{BASE_URL}/repos/{owner_login}/{repo_name}/git/ref/heads/{default_branch}",
    ).json()["object"]["sha"]

    branch_name = "feature"
    _gh_request(
        TOKEN,
        "POST",
        f"{BASE_URL}/repos/{owner_login}/{repo_name}/git/refs",
        json={"ref": f"refs/heads/{branch_name}", "sha": main_sha},

    )

    # # Крок 3: Створення нової гілки, базованої на SHA initial commit
    # branch_name = f"feature-branch-{random.randint(1000, 9999)}"
    # branch_payload = {
    #     "ref": f"refs/heads/{branch_name}",
    #     "sha": initial_commit_sha
    # }
    # branch_response = requests.post(f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/git/refs", headers=HEADERS,
    #                                 json=branch_payload)
    # assert branch_response.status_code == 201, f"Створення гілки не вдалося. Статус: {branch_response.status_code}"
    # print(f"New branch '{branch_name}' created.")

    _gh_request(
        TOKEN,
        "PUT",
        f"{BASE_URL}/repos/{owner_login}/{repo_name}/contents/hello.py",
        json={
            "message": "add hello",
            "content": base64.b64encode(b"print('hello')").decode(),
            "branch": branch_name,
        },
    )

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
    # 200, 201), f"Коміт у новій гілці не вдалося. Статус: {new_commit_response.status_code}"
    # new_commit_data = new_commit_response.json()
    # new_commit_sha = new_commit_data.get("commit", {}).get("sha")
    # print(f"New branch commit SHA: {new_commit_sha}")

    pr_resp = _gh_request(
        TOKEN,
        "POST",
        f"{BASE_URL}/repos/{owner_login}/{repo_name}/pulls",
        json={"title": "Add hello", "head": branch_name, "base": default_branch},
    )
    assert pr_resp.status_code == 201, f"Не вдалося створити PR: {pr_resp.text}"
    pr_number = pr_resp.json()["number"]

    # # Крок 5: Створення pull request з нової гілки до дефолтної
    # pr_payload = {
    #     "title": f"Merge {branch_name} into {default_branch}",
    #     "head": branch_name,
    #     "base": default_branch,
    #     "body": "This pull request is created by an automated API test."
    # }
    # pr_response = requests.post(f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/pulls", headers=HEADERS, json=pr_payload)
    # assert pr_response.status_code == 201, f"Створення pull request не вдалося. Статус: {pr_response.status_code}"
    # pr_data = pr_response.json()
    # pr_number = pr_data.get("number")
    # print(f"Pull request created: {pr_data.get('html_url')} (PR #{pr_number})")

    rev_resp = _gh_request(
        APPROVER_TOKEN,
        "POST",
        f"{BASE_URL}/repos/{owner_login}/{repo_name}/pulls/{pr_number}/reviews",
        json={"event": "APPROVE", "body": "LGTM"},
    )
    assert rev_resp.status_code == 200, f"Approve failed: {rev_resp.text}"

    merge_resp = _gh_request(
        TOKEN,
        "PUT",
        f"{BASE_URL}/repos/{owner_login}/{repo_name}/pulls/{pr_number}/merge",
        json={"merge_method": "squash"},
    )
    assert merge_resp.status_code == 200, f"Merge failed: {merge_resp.text}"

    # # Крок 6: Merge pull request
    # merge_payload = {
    #     "commit_title": f"Merge pull request #{pr_number} from {branch_name}",
    #     "commit_message": "Merged by automated test."
    # }
    # merge_url = f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/pulls/{pr_number}/merge"
    # merge_response = requests.put(merge_url, headers=HEADERS, json=merge_payload)
    # assert merge_response.status_code in (200, 201), f"Merge pull request failed. Статус: {merge_response.status_code}"
    # merge_data = merge_response.json()
    # assert merge_data.get("merged") is True, "Pull request was not merged"
    # print(f"Pull request #{pr_number} merged successfully.")

    # clean_up_repos()
