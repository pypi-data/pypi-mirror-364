import subprocess
import os

import questionary

from ..lib.io import save

def switch_user_prompt_temporary(config) -> dict:
    users = []

    for user in config["users"]:
        if 'username' in user and 'email' in user:
            users.append(f"{user['username']} ({user['email']}) | {user['url']} {"(current)" if user["current"] else ""}")
        elif 'linkTo' in user:
            linked_user = next((alias for alias in config["aliases"] if alias.get('id') == user['linkTo']), None)
            if linked_user:
                users.append(f"{linked_user['username']} ({linked_user['email']}) | {user['url']} ({"current, " if user["current"] else ""}alias)")
            else:
                users.append(f"Unknown User | {user['url']} ({"current, " if user["current"] else ""}alias)")
        else:
            users.append(f"Unknown User | {user['url']} {"(current)" if user["current"] else ""}")

    users.append("Exit")
    select_user = questionary.select("Select Account", choices=users).unsafe_ask()

    if select_user != "Exit":
        selected_index = users.index(select_user)
        selected_user = config["users"][selected_index]
        env = os.environ.copy()
        if selected_user.get("linkTo"):
            linked_user = next((alias for alias in config["aliases"] if alias.get('id') == selected_user['linkTo']), None)
            username = linked_user["username"]
            email = linked_user["email"]
        else:
            username = selected_user["username"]
            email = selected_user["email"]
        
        env["GIT_COMMITTER_NAME"] = username
        env["GIT_AUTHOR_NAME"] = username
        env["GIT_COMMITTER_EMAIL"] = email
        env["GIT_AUTHOR_EMAIL"] = email
        env["GCM_NAMESPACE"] = selected_user["id"]
        return env
    else:
        return None

def switch_user_prompt(config, local: bool):
    users = []

    for user in config["users"]:
        if 'username' in user and 'email' in user:
            users.append(f"{user['username']} ({user['email']}) | {user['url']} {"(current)" if user["current"] else ""}")
        elif 'linkTo' in user:
            linked_user = next((alias for alias in config["aliases"] if alias.get('id') == user['linkTo']), None)
            if linked_user:
                users.append(f"{linked_user['username']} ({linked_user['email']}) | {user['url']} ({"current, " if user["current"] else ""}alias)")
            else:
                users.append(f"Unknown User | {user['url']} ({"current, " if user["current"] else ""}alias)")
        else:
            users.append(f"Unknown User | {user['url']} {"(current)" if user["current"] else ""}")

    users.append("Exit")
    select_user = questionary.select("Select Account", choices=users).unsafe_ask()

    if select_user != "Exit":
        selected_index = users.index(select_user)
        selected_user = config["users"][selected_index]
        subprocess.run(f"git config {"--global" if not local else "--local"} credential.namespace {selected_user["id"]}")
        if selected_user.get("linkTo"):
            linked_user = next((alias for alias in config["aliases"] if alias.get('id') == selected_user['linkTo']), None)
            subprocess.run(f'git config {"--global" if not local else "--local"} user.name "{linked_user["username"]}"', shell=True)
            subprocess.run(f'git config {"--global" if not local else "--local"} user.email "{linked_user["email"]}"', shell=True)
        else:
            subprocess.run(f'git config {"--global" if not local else "--local"} user.name "{selected_user["username"]}"', shell=True)
            subprocess.run(f'git config {"--global" if not local else "--local"} user.email "{selected_user["email"]}"', shell=True)
        for user in config["users"]:
            if selected_user["id"] == user["id"]:
                selected_user["current"] = True
            else:
                user["current"] = False
    else:
        pass
    return save(config)
