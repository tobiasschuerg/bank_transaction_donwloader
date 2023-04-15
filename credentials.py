import os

import yaml


def load_credentials():
    if os.path.exists("credentials.yaml"):
        with open("credentials.yaml", "r") as f:
            return yaml.safe_load(f)
    else:
        secret_id = input("Enter your Nordigen Secret ID: ")
        secret_key = input("Enter your Nordigen Secret Key: ")
        credentials = {"SECRET_ID": secret_id, "SECRET_KEY": secret_key}
        with open("credentials.yaml", "w") as f:
            yaml.dump(credentials, f)
        return credentials
