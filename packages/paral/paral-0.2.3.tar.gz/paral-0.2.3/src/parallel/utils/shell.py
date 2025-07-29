import os
import subprocess
import sys
from typing import Tuple


def find(executable_name):
    for dir in os.environ["PATH"].split(os.pathsep):
        path = os.path.join(dir, executable_name)
        if os.path.isfile(path):
            return path
    return None


def is_unixlike() -> Tuple[bool, str | None]:
    if sys.platform == "linux":
        return True, None
    elif sys.platform == "darwin":
        return True, None
    elif sys.platform == "aix":
        return True, None
    elif sys.platform == "android":
        return True, None
    elif sys.platform == "ios":
        return True, None
    elif sys.platform.startswith("freebsd"):
        return True, "freebsd"
    else:
        return False, None


def launch(env: dict):
    if sys.platform == "win32":
        pwsh_name = "pwsh.exe"
        powershell_name = "powershell.exe"
        cmd_name = "cmd.exe"

        pwsh_path = find(pwsh_name)
        if pwsh_path:
            subprocess.run(
                [
                    pwsh_path,
                    "-NoExit",
                    "-Command",
                    'function Prompt { $color = "Blue"; Write-Host "(parallel)" -ForegroundColor $color -NoNewLine; Write-Host " $PWD> " -NoNewLine; return " "; }',
                ],
                env=env,
            )
            return

        powershell_path = find(powershell_name)
        if powershell_path:
            subprocess.run(
                [
                    powershell_path,
                    "-NoExit",
                    "-Command",
                    'function Prompt { $color = "Blue"; Write-Host "(parallel)" -ForegroundColor $color -NoNewLine; Write-Host " $PWD> " -NoNewLine; return " "; }',
                ],
                env=env,
            )
            return

        cmd_path = find(cmd_name)
        if cmd_path:
            subprocess.run(
                [cmd_path, "/k", "prompt (parallel) $p$g"], env=env, shell=True
            )
            return
        
    elif is_unixlike()[0]:
        subprocess.run([os.environ.get("SHELL")])
        return