from behave import given, when, then
import requests
from features.helper.prepare_user_data import user_data_response, saved_user_login, extract_user_login
from features.helper.prepare_branch_data import get_branch_name
from features.helper.pull_request_creation import create_pull_request
from features.helper.pull_request_deletetion import pull_request_deleted

@when('I want check deleted pull request in repository "{repo_name}"')
def pull_request_deleted_response(context, repo_name):
    context.pull_request_deleted_response = pull_request_deleted(repo_name, context.pull_request_response)

@then('I should see text message "{branch_name}" with default branch "{default_branch}"')
def should_text_message(context, branch_name, default_branch):
    assert context.pull_request_deleted_response['title'] == f'Merge {branch_name} into {default_branch}'
    assert context.pull_request_deleted_response['body'] == 'This pull request is created by automated API test.'
    assert context.pull_request_deleted_response['state'] == "closed"

