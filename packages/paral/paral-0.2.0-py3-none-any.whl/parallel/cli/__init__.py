import typer

from ..commands.switch_user import switch_user_prompt, switch_user_prompt_temporary
from ..lib import shell
from ..lib.io import init_config
from . import alias, user

app = typer.Typer(no_args_is_help=True, short_help="An Git User/Credential Switcher")
app.add_typer(alias.app)
app.add_typer(user.app)

@app.command("env", short_help="Open a temporary session with the any Git informations.")
def environment():
    config = init_config()
    env = switch_user_prompt_temporary(config)
    if env:
        shell.launch(env)

@app.command("switch", short_help="Change current user. Use --local to apply this change only locally.")
def switch_user(local: bool = False):
    config = init_config()
    try:
        switch_user_prompt(config, local)
    except KeyboardInterrupt:
        pass