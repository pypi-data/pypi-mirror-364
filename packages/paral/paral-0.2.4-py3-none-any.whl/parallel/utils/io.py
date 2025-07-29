import os

import yaml

def save(config: dict):
    with open(
        os.path.join(os.path.join(os.path.expanduser("~"), ".parallel"), "config.yml"),
        "w",
        encoding="utf-8",
    ) as f:
        yaml.safe_dump(config, f, default_flow_style=False, allow_unicode=True)
    return config

def init_config():
    if os.path.isdir(os.path.join(os.path.expanduser("~"), ".parallel")):
        if os.path.isfile(
            os.path.join(os.path.join(os.path.expanduser("~"), ".parallel"), "config.yml")
        ):
            with open(
                os.path.join(
                    os.path.join(os.path.expanduser("~"), ".parallel"), "config.yml"
                ),
                "r",
                encoding="utf-8",
            ) as f:
                config = yaml.safe_load(f)
        else:
            config = {"v": 0, "users": [], "aliases": []}
            with open(
                os.path.join(
                    os.path.join(os.path.expanduser("~"), ".parallel"), "config.yml"
                ),
                "w",
                encoding="utf-8",
            ) as f:
                yaml.safe_dump(config, f)
            with open(
                os.path.join(
                    os.path.join(os.path.expanduser("~"), ".parallel"), "config.yml"
                ),
                "r",
                encoding="utf-8",
            ) as f:
                config = yaml.safe_load(f)
    else:
        os.mkdir(os.path.join(os.path.expanduser("~"), ".parallel"))
        config = {"v": 0, "users": [], "aliases": []}
        with open(
            os.path.join(os.path.join(os.path.expanduser("~"), ".parallel"), "config.yml"),
            "w",
            encoding="utf-8",
        ) as f:
            yaml.safe_dump(config, f)
        with open(
            os.path.join(os.path.join(os.path.expanduser("~"), ".parallel"), "config.yml"),
            "r",
            encoding="utf-8",
        ) as f:
            config = yaml.safe_load(f)
    return config