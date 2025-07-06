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

#autorization
def test_get_user_info():
    """Тест на отримання інформації про поточного користувача."""
    response = requests.get(f"{BASE_URL}/user", headers=HEADERS)
    assert response.status_code == 200, "Не вдалося отримати інформацію про користувача"
    user_data = response.json()
    assert "login" in user_data, "Поле 'login' відсутнє в відповіді"

def test_check_user_login():
    response = requests.get(f"{BASE_URL}/user", headers=HEADERS)
    assert response.status_code == 200, "Не вдалося отримати інформацію про користувача"
    user_data = response.json()
    assert "login" in user_data, "Поле 'login' відсутнє в відповіді"
    assert user_data['login'] == USER_LOGIN

#getting all repositories list
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

#getting all branches of repository
def test_all_branches_of_repository(repo_name):
    #precondition
    default_branch, initial_commit_sha = create_repos(repo_name)
    create_branches(repo_name,default_branch, initial_commit_sha, count=10)
    # https: // api.github.com / repos / {owner} / {repo} / branches

    branch_response = requests.get(f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}/branches", headers=HEADERS)
    print(branch_response.json())
    assert len(branch_response.json()) == 10+1

    #postcondition
    clean_up_repos()

def test_creating_of_pull_requests(repo_name):
    default_branch, initial_commit_sha = create_repos(repo_name)
    repo_name, default_branch, branches_name = create_branches(repo_name, default_branch, initial_commit_sha, count=10)
    create_pull_requests(repo_name, default_branch, branches_name)

    # postcondition
    clean_up_repos()

def test_delete_pull_requests(repo_name):
    default_branch, initial_commit_sha = create_repos(repo_name)
    repo_name, default_branch, branches_name = create_branches(repo_name, default_branch, initial_commit_sha, count=10)
    pr_list = create_pull_requests(repo_name, default_branch, branches_name)
    for pr in pr_list:
        print(pr["number"])

    close_pull_requests(repo_name,pr_list)
    # postcondition
    # clean_up_repos()


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

    pr_resp = _gh_request(
        TOKEN,
        "POST",
        f"{BASE_URL}/repos/{owner_login}/{repo_name}/pulls",
        json={"title": "Add hello", "head": branch_name, "base": default_branch},
    )
    assert pr_resp.status_code == 201, f"Не вдалося створити PR: {pr_resp.text}"
    pr_number = pr_resp.json()["number"]

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

    # clean_up_repos()

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

    pr_resp = _gh_request(
        TOKEN,
        "POST",
        f"{BASE_URL}/repos/{owner_login}/{repo_name}/pulls",
        json={"title": "Add hello", "head": branch_name, "base": default_branch},
    )
    assert pr_resp.status_code == 201, f"Не вдалося створити PR: {pr_resp.text}"
    pr_number = pr_resp.json()["number"]

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

    # clean_up_repos()