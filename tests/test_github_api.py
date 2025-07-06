import pytest
from utils.github_api import *

@pytest.mark.authorization
def test_authorization():
    user = get_user()
    assert "login" in user, "Authorization failed, 'login' not found in response."

@pytest.mark.repositories
def test_get_repositories():
    repos = get_repositories()
    assert isinstance(repos, list), "Repositories should be a list."

@pytest.mark.branches
def test_get_branches():
    repo_name = "test-repo"
    branches = get_branches(repo_name)
    assert isinstance(branches, list), "Branches should be a list."

@pytest.mark.pull_requests
def test_get_pull_requests():
    repo_name = "test-repo"
    pull_requests = get_pull_requests(repo_name)
    assert isinstance(pull_requests, list), "Pull requests should be a list."

@pytest.mark.pull_requests
def test_create_pull_request():
    repo_name = "test-repo"
    head = "feature-branch"
    base = "master"
    pr = create_pull_request(repo_name, head, base, title="Test PR")
    assert "id" in pr, "Pull request creation failed."


@pytest.mark.pull_requests
def test_approve_pull_request():
    repo_name = "your-repo-name"
    pull_number = 1  # Replace with a valid PR number
    merge_response = approve_pull_request(repo_name, pull_number)
    assert merge_response["merged"], "Approval (merge) failed."
