import uuid

def add_alias(config, username: str, email: str) -> dict:
    if config.get("aliases") is None:
        config["aliases"] = []

    try:
        config["aliases"].append(
            {"id": str(uuid.uuid4()), "username": username, "email": email}
        )
    except KeyError:
        config["aliases"] = [
            {"id": str(uuid.uuid4()), "username": username, "email": email}
        ]
    return config