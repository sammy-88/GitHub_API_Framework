import os
import random
import requests
import pytest
from dotenv import load_dotenv
import new_pr_approver_helper as pr_helper

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

# ===================  NEW END-TO-END FLOW  ===================

import time
import base64

APPROVER_TOKEN = os.getenv("GITHUB_REVIEWER_TOKEN")
APPROVER_LOGIN = os.getenv("GITHUB_REVIEWER_USERNAME")


def _github_request(token: str, method: str, url: str, **kwargs):
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
    # Repository creation
    r = pr_helper.repo_creation(repo_name)
    assert r.status_code == 201, f"Не вдалося створити репозиторій: {r.text}"
    repo_data = r.json()
    owner_login = repo_data["owner"]["login"]
    default_branch = repo_data["default_branch"]

    # Invite collaborators in repository
    invite = pr_helper.invite_collaborator(owner_login, repo_name, APPROVER_LOGIN)
    assert invite.status_code in (201, 202), f"Invite error: {invite.text}"

    inv_resp = pr_helper.check_invitations(APPROVER_TOKEN)
    inv_id = next(
        (
            i["id"]
            for i in inv_resp.json()
            if i["repository"]["name"] == repo_name
        ),
        None,
    )
    assert inv_id, "Не знайдено запрошення"

    acc_resp = pr_helper.check_invitation_id(APPROVER_TOKEN, inv_id)
    assert acc_resp.status_code == 204, f"Не вдалося прийняти запрошення: {acc_resp.text}"

    time.sleep(2)

    # TAKE SHA COMMIT OF MASTER BRANCH
    main_sha = pr_helper.take_sha_commit_of_main_branch(owner_login, repo_name, default_branch)

    # Creation branch with name "feature"
    branch_name = "feature"
    pr_helper.creation_branch_with_name(owner_login, repo_name, branch_name, main_sha)

    # ADD NEW FILE
    pr_helper.add_new_file(owner_login, repo_name, branch_name)

    # CREATION PULL REQUEST
    pr_resp = pr_helper.creation_pull_request(owner_login, repo_name, branch_name, default_branch)
    assert pr_resp.status_code == 201, f"Не вдалося створити PR: {pr_resp.text}"
    pr_number = pr_resp.json()["number"]

    rev_resp = pr_helper.check_invitations(APPROVER_TOKEN)
    assert rev_resp.status_code == 200, f"Approve failed: {rev_resp.text}"

    # Merge pull request
    merge_method = "squash"
    merge_resp = pr_helper.merge_pull_request(owner_login, repo_name, pr_number)
    assert merge_resp.status_code == 200, f"Merge failed: {merge_resp.text}"

    #clean_up_repos()

# ===================  NEW END-TO-END FLOW  ===================

import time
import base64

APPROVER_TOKEN = os.getenv("GITHUB_REVIEWER_TOKEN")
APPROVER_LOGIN = os.getenv("GITHUB_REVIEWER_USERNAME")


def _github_request(token: str, method: str, url: str, **kwargs):
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
def test_full_collaborator_flow_second(repo_name):
    """Створити репо → запросити колаборатора → PR → approve → merge"""

    r = _github_request(
        TOKEN,
        "POST",
        f"{BASE_URL}/user/repos",
        json={"name": repo_name, "auto_init": True, "private": False},
    )
    assert r.status_code == 201, f"Не вдалося створити репозиторій: {r.text}"
    repo_data = r.json()
    owner_login = repo_data["owner"]["login"]
    default_branch = repo_data["default_branch"]

    invite = _github_request(
        TOKEN,
        "PUT",
        f"{BASE_URL}/repos/{owner_login}/{repo_name}/collaborators/{APPROVER_LOGIN}",
        json={"permission": "push"},
    )
    assert invite.status_code in (201, 202), f"Invite error: {invite.text}"

    inv_resp = _github_request(APPROVER_TOKEN, "GET", f"{BASE_URL}/user/repository_invitations")
    inv_id = next(
        (
            i["id"]
            for i in inv_resp.json()
            if i["repository"]["name"] == repo_name
        ),
        None,
    )
    assert inv_id, "Не знайдено запрошення"
    acc_resp = _github_request(
        APPROVER_TOKEN,
        "PATCH",
        f"{BASE_URL}/user/repository_invitations/{inv_id}",
    )
    assert acc_resp.status_code == 204, f"Не вдалося прийняти запрошення: {acc_resp.text}"

    time.sleep(2)

    main_sha = _github_request(
        TOKEN,
        "GET",
        f"{BASE_URL}/repos/{owner_login}/{repo_name}/git/ref/heads/{default_branch}",
    ).json()["object"]["sha"]

    branch_name = "feature"
    _github_request(
        TOKEN,
        "POST",
        f"{BASE_URL}/repos/{owner_login}/{repo_name}/git/refs",
        json={"ref": f"refs/heads/{branch_name}", "sha": main_sha},
    )

    _github_request(
        TOKEN,
        "PUT",
        f"{BASE_URL}/repos/{owner_login}/{repo_name}/contents/hello.py",
        json={
            "message": "add hello",
            "content": base64.b64encode(b"print('hello')").decode(),
            "branch": branch_name,
        },
    )

    pr_resp = _github_request(
        TOKEN,
        "POST",
        f"{BASE_URL}/repos/{owner_login}/{repo_name}/pulls",
        json={"title": "Add hello", "head": branch_name, "base": default_branch},
    )
    assert pr_resp.status_code == 201, f"Не вдалося створити PR: {pr_resp.text}"
    pr_number = pr_resp.json()["number"]

    rev_resp = _github_request(
        APPROVER_TOKEN,
        "POST",
        f"{BASE_URL}/repos/{owner_login}/{repo_name}/pulls/{pr_number}/reviews",
        json={"event": "APPROVE", "body": "LGTM"},
    )
    assert rev_resp.status_code == 200, f"Approve failed: {rev_resp.text}"

    merge_resp = _github_request(
        TOKEN,
        "PUT",
        f"{BASE_URL}/repos/{owner_login}/{repo_name}/pulls/{pr_number}/merge",
        json={"merge_method": "squash"},
    )
    assert merge_resp.status_code == 200, f"Merge failed: {merge_resp.text}"

    # clean_up_repos()