import hashlib

from backend.database import load_data, save_data



def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()



def create_user(username, password):

    users = load_data("users.json")

    if username in users:
        return False


    users[username] = {
        "password": hash_password(password)
    }


    save_data(
        "users.json",
        users
    )

    return True



def authenticate(username, password):

    users = load_data("users.json")


    if username not in users:
        return False


    stored_password = users[username]["password"]

    if stored_password != hash_password(password):
        return False


    return True



def create_profile(
    username,
    name,
    age,
    user_type,
    goals,
    detail_level,
    income_source
):

    profiles = load_data("profiles.json")


    profiles[username] = {

        "name": name,

        "age": age,

        "user_type": user_type,

        "goals": goals,

        "detail_level": detail_level,

        "income_source": income_source

    }


    save_data(
        "profiles.json",
        profiles
    )



def get_profile(username):

    profiles = load_data("profiles.json")

    return profiles.get(username)