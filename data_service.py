
import requests
import pandas as pd

BASE_URL = "https://jsonplaceholder.typicode.com"

_cache = {}


def fetch_json(path):
    if path in _cache:
        return _cache[path]

    try:
        response = requests.get(
            f"{BASE_URL}/{path}",
            timeout=5
        )
        response.raise_for_status()

        data = response.json()
        _cache[path] = data

        return data

    except requests.exceptions.RequestException:
        return None


def get_users_dataframe():
    users = fetch_json("users")

    if users is None:
        return None

    users_data = []

    for user in users:
        users_data.append({
            "user_id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "city": user["address"]["city"]
        })

    return pd.DataFrame(users_data)


def get_todos_dataframe():
    todos = fetch_json("todos")

    if todos is None:
        return None

    df = pd.DataFrame(todos)

    df = df.rename(columns={
        "userId": "user_id"
    })

    df["completed"] = df["completed"].astype(bool)

    return df

