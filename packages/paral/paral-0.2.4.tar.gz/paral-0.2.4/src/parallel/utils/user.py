import uuid

def check_user_exists(config, url: str, username: str, email: str, link_to: str) -> bool:
    user_tuple = (url, username, email, link_to)

    for user in config.get("users", []) if config.get("users", []) is not None else []:
        if (user["url"], user.get("username"), user.get("email"), user.get("linkTo")) == user_tuple:
            return True
    return False


def add_user(config, url: str, username: str, email: str, link_to: str) -> dict:
    user = {
        "id": str(uuid.uuid4()),
        "url": url,
        "current": False
    }
    if username and email:
        if username:
            user["username"] = username
        if email:
            user["email"] = email
    elif link_to:
        user["linkTo"] = link_to
    else:
        raise Exception("Invalid parameter")
    
    if config.get("users") is None:
        config["users"] = []

    try:
        config["users"].append(user)
    except KeyError:
        config["users"] = [user]
    return config