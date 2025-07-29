import argparse
import warnings

import questionary

from .commands import switch_user_prompt, add_user_prompt, add_alias_prompt, delete_user_prompt, delete_alias_prompt
from .lib.io import init_config


parser = argparse.ArgumentParser(description="Example script.")
parser.add_argument('--local', action='store_true')
args = parser.parse_args()

def run():
    warnings.warn("The prl command is deprecated; please use the paral command.", DeprecationWarning)
    config = init_config()
    try:
        while True:
            command = questionary.select(
                "What do you do?",
                choices=["Switch User", "Add User", "Add Aliases", "Delete User", "Delete Aliases", "Exit"],
            ).unsafe_ask()

            if command == "Switch User":
                config = switch_user_prompt(config, args.local)
            elif command == "Add User":
                config = add_user_prompt(config)
            elif command == "Delete User":
                config = delete_user_prompt(config)
            elif command == "Add Aliases":
                config = add_alias_prompt(config)
            elif command == "Delete Aliases":
                config = delete_alias_prompt(config)
            elif command == "Exit":
                break
            else:
                print("Unknown Command.")
    except KeyboardInterrupt:
        print("Bye!")