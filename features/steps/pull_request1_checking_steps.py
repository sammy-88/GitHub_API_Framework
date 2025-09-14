from behave import given, when, then
import requests
from features.helper.prepare_user_data import user_data_response, saved_user_login, extract_user_login
from features.helper.prepare_branch_data import get_branch_name
from features.helper.pull_request1_creation import create_pull_request1
from dotenv import load_dotenv
import os

@when('I create new pull request1 with name "{branch_name}" in repository "{repo_name}" with default branch "{default_branch}"')
def branch_creation_request(context, branch_name, repo_name, default_branch):
    context.created_pull_request_response = create_pull_request1(repo_name, default_branch, branch_name)

@then('I should see new pull request1 branch "{branch_name}" with default branch "{default_branch}"')
def branch_should_see_the_expected_branch(context, branch_name, default_branch):
    load_dotenv()
    assert context.created_pull_request_response['user']['login'] == os.getenv("GITHUB_USERNAME")
    assert context.created_pull_request_response['title'] == f'Merge {branch_name} into {default_branch}'
    assert context.created_pull_request_response['body'] == "This pull request is created by automated API test."
#
# @when('I create new pull request with name "{branch_name}" in repository "{repo_name}" with default branch "{default_branch}"')
# def pull_request_creation(context, branch_name, repo_name, default_branch):
#     context.pull_request_response = create_pull_request(repo_name, default_branch, branch_name)
#
# @then('I should see new pull request "{branch_name}" with default branch "{default_branch}"')
# def branch_should_see_the_expected_branch(context, branch_name, default_branch):
#     assert context.pull_request_response['title'] == f'Merge {branch_name} into {default_branch}'
#     assert context.pull_request_response['body'] == 'This pull request is created by automated API test.'
