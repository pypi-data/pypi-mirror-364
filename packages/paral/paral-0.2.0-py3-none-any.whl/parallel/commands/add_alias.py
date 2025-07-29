import questionary

from ..lib.io import save
from ..lib.alias import add_alias


def add_alias_prompt(config) -> dict:
    while True:
        username = questionary.text("Enter username").unsafe_ask()
        if username != "":
            break
        else:
            print("Enter a value.")
    while True:
        email = questionary.text("Enter email").unsafe_ask()
        if email != "":
            break
        else:
            print("Enter a value.")
    confirm = questionary.confirm(
        "Would you like to add with this information?", default=False
    ).unsafe_ask()
    if not confirm:
        print("No aliases were added.")
    else:
        config = add_alias(config, username, email)
        config = save(config)
        print("Alias added!")
    return config
