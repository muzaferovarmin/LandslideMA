"""
Utils for credentials, this saves the credentials in the user keyring
"""

import keyring
import os
import json

APP_NAME = "Satellite Data Pipeline"
CONFIG_PATH = os.path.expanduser("~/.LandslidePipeline_config.json")

def save_credentials(client_id, client_secret):
    with open(CONFIG_PATH, "w") as f:
        json.dump({"client_id": client_id}, f)
    keyring.set_password(APP_NAME, client_id, client_secret)

def get_credentials():
    if not os.path.exists(CONFIG_PATH):
        return None, None
    with open(CONFIG_PATH, "r") as f:
        client_id = json.load(f).get("client_id")
    if client_id:
        client_secret = keyring.get_password(APP_NAME, client_id)
        return client_id, client_secret
    return None, None
