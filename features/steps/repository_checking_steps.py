from behave import given, when, then
import requests
from features.helper.prepare_user_data import user_data_response, saved_user_login, extract_user_login
from features.helper.repository_creation import create_repo_by_name, delete_repo_by_name


@given('I create repository with custom name "{repo_name}"')
def repository_creation_request(context,repo_name):
    context.repo_response = create_repo_by_name(repo_name)

@when('I extract repository name from repository response')
def repository_extract(context):
    context.repo_name = context.repo_response["name"]

@then('I assert repository name is "{repo_name}"')
def repository_check_response(context, repo_name):
    assert context.repo_name == repo_name

@given('I clean up repository by name "{repo_name}"')
def repository_cleanup(context, repo_name):
   delete_repo_by_name(repo_name)


#  def test_create_repository(repo_name):
#    """Тест на створення нового репозиторію."""
#    payload = {"name": repo_name, "private": False}
#    response = requests.post(f"{BASE_URL}/user/repos", headers=HEADERS, json=payload)
#    assert response.status_code == 201, "Не вдалося створити репозиторій"
#    repo_data = response.json()
#    assert repo_data["name"] == repo_name, "Ім'я репозиторія не збігається"
#
#    print(f"Repository '{repo_name}' created successfully")
#
#    # Postcondition
#    requests.delete(f"{BASE_URL}/repos/{USER_LOGIN}/{repo_name}",
#                    headers=HEADERS)
#    assert response.status_code == 201