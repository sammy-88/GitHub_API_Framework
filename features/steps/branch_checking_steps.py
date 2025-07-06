from behave import given, when, then
import requests
from features.helper.prepare_user_data import user_data_response, saved_user_login, extract_user_login
from features.helper.prepare_branch_data import get_branch_name
from features.helper.branch_creation import default_branch_checking, create_commit, create_branch


@given('I create commit in repository "{repo_name}"')
def commit_creation_request(context, repo_name):
    context.default_branch = default_branch_checking(context.repo_response)
    context.initial_commit_sha = create_commit(repo_name)


@when('I create new branch with name "{branch_name}" in repository "{repo_name}"')
def branch_creation_request(context, branch_name, repo_name):
    context.created_branch_response = create_branch(repo_name, context.initial_commit_sha, branch_name)

@then('I should see the branch "{branch_name}"')
def branch_should_see_the_expected_branch(context, branch_name):
    created_branch_name = get_branch_name(context.created_branch_response)
    assert created_branch_name == branch_name