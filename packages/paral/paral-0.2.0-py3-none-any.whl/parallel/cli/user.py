import typer


from ..commands import add_user_prompt, delete_user_prompt, switch_user_prompt
from ..lib.io import init_config

app = typer.Typer(name="user")

@app.command("switch", short_help="Change current user. Use --local to apply this change only locally.")
def switch_user(local: bool = False):
    config = init_config()
    try:
        switch_user_prompt(config, local)
    except KeyboardInterrupt:
        pass


@app.command("add", short_help="Add a new user.")
def add_user():
    config = init_config()
    try:
        add_user_prompt(config)
    except KeyboardInterrupt:
        pass
    
@app.command("delete", short_help="Delete an existing user.")
def delete_user():
    config = init_config()
    try:
        delete_user_prompt(config)
    except KeyboardInterrupt:
        pass