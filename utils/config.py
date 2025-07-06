from dotenv import load_dotenv
import os
import requests
import pytest
import random

load_dotenv()
GITHUB_API_URL = "https://api.github.com"
PERSONAL_ACCESS_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"token {PERSONAL_ACCESS_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
