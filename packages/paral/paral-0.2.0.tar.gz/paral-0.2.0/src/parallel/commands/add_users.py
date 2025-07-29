import questionary

from ..lib.user import check_user_exists, add_user
from ..lib.io import save

def add_user_prompt(config):
    while True:
        remote = questionary.text("Enter Remote URL").unsafe_ask()
        if remote != "":
            break
        else:
            print("Enter a value.")

    link_alias = questionary.confirm(
        "Link to an existing alias?", default=False
    ).unsafe_ask()
    if not link_alias:
        while True:
            username = questionary.text("Enter Git username").unsafe_ask()
            if username != "":
                break
            else:
                print("Enter a value.")
        while True:
            email = questionary.text("Enter Git email").unsafe_ask()
            if email != "":
                break
            else:
                print("Enter a value.")
    else:
        aliases = [f"{user['username']} ({user['email']})" for user in config["aliases"]]
        aliases.append("No link to aliases")
        select_alias = questionary.select("Select aliases to delete", choices=aliases).unsafe_ask()
        if select_alias != "No link to aliases":
            selected_index = aliases.index(select_alias)
            selected_alias = config["aliases"][selected_index]
            link_to = selected_alias["id"]
            username = None
            email = None
        else:
            while True:
                username = questionary.text("Enter Git username").unsafe_ask()
                if username != "":
                    break
                else:
                    print("Enter a value.")
            while True:
                email = questionary.text("Enter Git email").unsafe_ask()
                if email != "":
                    break
                else:
                    print("Enter a value.")
            link_to = None

    confirm = questionary.confirm(
        "Would you like to add with this information?", default=False
    ).unsafe_ask()
    if not confirm:
        print("No users were added.")
    else:
        is_exists = check_user_exists(config, remote, username, email, link_to)
        if is_exists:
            print("This user already exists.")
        else:
            config = add_user(config, remote, username, email, link_to)
            config = save(config)
            print("User added!")
    return config