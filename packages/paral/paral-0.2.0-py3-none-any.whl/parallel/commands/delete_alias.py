import questionary
from ..lib.io import save

def delete_alias_prompt(config):
    aliases = [f"{user['username']} ({user['email']})" for user in config["aliases"]]
    aliases.append("Exit")
    select_alias = questionary.select("Select aliases to delete", choices=aliases).unsafe_ask()

    if select_alias != "Exit":
        selected_index = aliases.index(select_alias)
        selected_alias = config["aliases"][selected_index]

        linked_users = [user for user in config["users"] if user.get('linkTo') == selected_alias['id']]
        
        if linked_users:
            urls = [user['url'] for user in linked_users if 'url' in user]
            url_list = ', '.join(urls) if urls else "Unknown Host"
            warning_message = (
                f"Warning: The following urls are linked to this alias and will be affected:\n"
                f"{url_list}\n"
                "Do you still want to proceed with the deletion?"
            )
            confirm = questionary.confirm(warning_message, default=False).unsafe_ask()
        else:
            confirm = questionary.confirm(
                "Are you sure you want to delete it? This operation cannot be undone.",
                default=False,
            ).unsafe_ask()

        if confirm:
            config["aliases"].remove(selected_alias)
            config = save(config)
            print(f"Alias {selected_alias['username']} has been removed.")
        else:
            print("No aliases were removed.")
    else:
        print("No aliases were removed.")
    
    return config
