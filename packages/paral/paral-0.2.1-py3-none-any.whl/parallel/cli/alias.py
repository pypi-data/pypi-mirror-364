import typer


from ..commands import add_alias_prompt, delete_alias_prompt
from ..lib.io import init_config

app = typer.Typer(name="alias")

@app.command("add", short_help="Add a new alias.")
def add_alias():
    config = init_config()
    try:
        add_alias_prompt(config)
    except KeyboardInterrupt:
        pass

@app.command("delete", short_help="Delete an existing alias.")
def delete_alias():
    config = init_config()
    try:
        delete_alias_prompt(config)
    except KeyboardInterrupt:
        pass