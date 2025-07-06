import base64
from dotenv import load_dotenv
import os
import requests
import pytest
import random

load_dotenv()

# Configuration
GITHUB_API_URL = "https://api.github.com"
PERSONAL_ACCESS_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"token {PERSONAL_ACCESS_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def create_repository(repo_name, description="", private=True):
    """
    Creates a new GitHub repository.
    """
    data = {
        "name": repo_name,
        "description": description,
        "private": private
    }
    response = requests.post(f"{GITHUB_API_URL}/user/repos", headers=HEADERS, json=data)
    response.raise_for_status()
    return response.json()

def create_file(repo_name, file_path, content, commit_message="Initial commit"):
    """
    Creates a file in the repository and commits it.
    """
    # Encode the file content in Base64
    content_encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    data = {
        "message": commit_message,
        "content": content_encoded
    }
    response = requests.put(
        f"{GITHUB_API_URL}/repos/{get_user()['login']}/{repo_name}/contents/{file_path}",
        headers=HEADERS,
        json=data
    )
    response.raise_for_status()
    return response.json()

def get_user():
    """
    Fetch the authenticated user's information.
    """
    response = requests.get(f"{GITHUB_API_URL}/user", headers=HEADERS)
    response.raise_for_status()
    return response.json()

# Usage
if __name__ == "__main__":
    try:
        # Step 1: Create a new repository
        repo_name = "test-repo-api-16122471"
        description = "This is the description of my new repository."
        repo = create_repository(repo_name, description=description)
        print(f"Repository created: {repo['html_url']}")

        # Step 2: Add an initial commit with a README file
        file_path = "README.md"
        content = "# Welcome to My Repository\n\nThis is the initial README file."
        commit_response = create_file(repo_name, file_path, content, commit_message="Initial commit")
        print(f"Initial commit created: {commit_response['commit']['html_url']}")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
