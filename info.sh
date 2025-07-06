#!/bin/bash
# Файл: github_api_example.sh

# --- Налаштування змінних ---
TOKEN="YOUR_GITHUB_TOKEN"
OWNER="your_github_username"      # Ваш логін GitHub
REPO="my-new-repo"                # Ім'я репозиторія, який будемо створювати
ORG="your_org"                    # Якщо створюєте репозиторій для організації
BASE_COMMIT_SHA="BASE_COMMIT_SHA" # SHA базового коміту (наприклад, останній коміт у main)
BASE_TREE_SHA="BASE_TREE_SHA"     # SHA дерева, яке буде базою для нового дерева
NEW_BRANCH="feature-branch"       # Ім'я нової гілки
PULL_NUMBER=1                     # Номер пулл реквеста для мерджу

# --- 1. Створення репозиторія ---
# Створення репозиторія для користувача:
echo "Створення репозиторія $REPO для користувача..."
curl -s -X POST \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "name": "'"$REPO"'",
        "description": "Опис мого нового репозиторія",
        "private": false
      }' \
  https://api.github.com/user/repos
echo -e "\nРепозиторій створено (якщо немає помилок)."

# Якщо потрібно створити репозиторій для організації, розкоментуйте нижченаведений блок:
#: <<'ORG_REPO'
# echo "Створення репозиторія $REPO для організації $ORG..."
# curl -s -X POST \
#   -H "Authorization: token $TOKEN" \
#   -H "Content-Type: application/json" \
#   -d '{
#         "name": "'"$REPO"'",
#         "description": "Опис мого нового репозиторія",
#         "private": false
#       }' \
#   https://api.github.com/orgs/$ORG/repos
# echo -e "\nРепозиторій організації створено (якщо немає помилок)."
#ORG_REPO

# --- 2. Додавання комітів (послідовність операцій) ---

# 2.1. Створення blob (об'єкта з вмістом файлу):
echo -e "\nСтворення blob (файл hello.txt)..."
BLOB_RESPONSE=$(curl -s -X POST \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "content": "Hello, world!",
        "encoding": "utf-8"
      }' \
  https://api.github.com/repos/$OWNER/$REPO/git/blobs)

BLOB_SHA=$(echo $BLOB_RESPONSE | jq -r .sha)
echo "Blob SHA: $BLOB_SHA"

# 2.2. Створення дерева (tree) із вказанням файлів:
echo -e "\nСтворення дерева для файлу hello.txt..."
TREE_RESPONSE=$(curl -s -X POST \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "base_tree": "'"$BASE_TREE_SHA"'",
        "tree": [
          {
            "path": "hello.txt",
            "mode": "100644",
            "type": "blob",
            "sha": "'"$BLOB_SHA"'"
          }
        ]
      }' \
  https://api.github.com/repos/$OWNER/$REPO/git/trees)

TREE_SHA=$(echo $TREE_RESPONSE | jq -r .sha)
echo "Tree SHA: $TREE_SHA"

# 2.3. Створення коміту:
echo -e "\nСтворення коміту для додавання hello.txt..."
COMMIT_RESPONSE=$(curl -s -X POST \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "message": "Додаємо hello.txt",
        "tree": "'"$TREE_SHA"'",
        "parents": ["'"$BASE_COMMIT_SHA"'"]
      }' \
  https://api.github.com/repos/$OWNER/$REPO/git/commits)

COMMIT_SHA=$(echo $COMMIT_RESPONSE | jq -r .sha)
echo "Commit SHA: $COMMIT_SHA"

# 2.4. Оновлення reference (оновлення гілки, наприклад, main)
echo -e "\nОновлення гілки main новим комітом..."
curl -s -X PATCH \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "sha": "'"$COMMIT_SHA"'",
        "force": false
      }' \
  https://api.github.com/repos/$OWNER/$REPO/git/refs/heads/main
echo "Гілка main оновлена."

# --- 3. Додавання (створення) гілки ---
echo -e "\nСтворення нової гілки $NEW_BRANCH..."
curl -s -X POST \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "ref": "refs/heads/'"$NEW_BRANCH"'",
        "sha": "'"$BASE_COMMIT_SHA"'"
      }' \
  https://api.github.com/repos/$OWNER/$REPO/git/refs
echo "Гілка $NEW_BRANCH створена."

# --- 4. Мердж пулл реквестів ---
echo -e "\nМердж пулл реквеста #$PULL_NUMBER..."
curl -s -X PUT \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "commit_title": "Об’єднання пулл реквеста",
        "commit_message": "Мерж пулл реквеста з гілки '"$NEW_BRANCH"'",
        "sha": "'"$COMMIT_SHA"'"
      }' \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PULL_NUMBER/merge
echo "Пулл реквест #$PULL_NUMBER об'єднано."
