import questionary

from ..lib.io import save


def delete_user_prompt(config):
    users = []

    for user in config["users"]:
        if 'username' in user and 'email' in user:
            users.append(f"{user['username']} ({user['email']}) | {user['url']}")
        elif 'linkTo' in user:
            linked_user = next((alias for alias in config["aliases"] if alias.get('id') == user['linkTo']), None)
            if linked_user:
                users.append(f"{linked_user['username']} ({linked_user['email']}) | {user['url']} (alias)")
            else:
                users.append(f"Unknown User | {user['url']} (alias)")
        else:
            users.append(f"Unknown User | {user['url']}")

    users.append("Exit")
    select_user = questionary.select("Select users to delete", choices=users).unsafe_ask()

    if select_user != "Exit":
        selected_index = users.index(select_user)
        selected_user = config["users"][selected_index]

        confirm = questionary.confirm(
            "Are you sure you want to delete it? This operation cannot be undone.",
            default=False,
        ).unsafe_ask()
        if confirm:
            config["users"].remove(selected_user)
            config = save(config)
            print(f"User {selected_user['username']} has been removed.")
        else:
            print("No users were removed.")
    else:
        print("No users were removed.")
    return config
