import os
import time

import yaml
from nordigen import NordigenClient
from requests import HTTPError


def load_credentials():
    if os.path.exists("credentials.yaml"):
        with open("credentials.yaml", "r") as f:
            return yaml.safe_load(f)
    else:
        secret_id = input("Enter your Nordigen Secret ID: ")
        secret_key = input("Enter your Nordigen Secret Key: ")
        credentials = {"SECRET_ID": secret_id, "SECRET_KEY": secret_key}
        return save(credentials)


def save(credentials):
    with open("credentials.yaml", "w") as f:
        yaml.dump(credentials, f)
    return credentials


def get_refresh_token():
    return load_credentials()["refresh_token"]


def is_new_token_needed(credentials):
    if "access_token" not in credentials or "token_expiry" not in credentials:
        # there is no valid token at all
        return True

    current_time = time.time()
    # If the token will expire in less than 5 minutes (300 seconds), return True
    if current_time >= credentials["token_expiry"] - 300:
        return True
    else:
        # Token has not expired and should be valid
        return False


def create_nordigen_client():
    # Load credentials from file or prompt user
    credentials = load_credentials()

    # Initialize Nordigen client with SECRET_ID and SECRET_KEY
    nordigen_client = NordigenClient(
        secret_id=credentials["SECRET_ID"],
        secret_key=credentials["SECRET_KEY"]
    )

    # Check if access_token is not set and generate it
    if is_new_token_needed(credentials):
        print("Generating access token...")
        token_data = nordigen_client.generate_token()
        credentials["access_token"] = token_data["access"]
        credentials["refresh_token"] = token_data["refresh"]
        credentials["token_expiry"] = time.time() + token_data["access_expires"]
        with open("credentials.yaml", "w") as f:
            yaml.dump(credentials, f)
        print("New access token generated.")
    else:
        print("Using existing access token.")
        nordigen_client.token = credentials["access_token"]

    # check if client works
    try:
        connection_check(nordigen_client)
    except HTTPError as e:
        if e.response.status_code == 401:
            print("Access token expired. Refreshing token...")
            new_token = nordigen_client.exchange_token(get_refresh_token())
            credentials["access_token"] = new_token["access"]
            credentials["token_expiry"] = time.time() + new_token["access_expires"]
            save(credentials)
            institutions = nordigen_client.institution.get_institutions("DE")
            print("supported banks (DE):")
            for i in institutions:
                print(" - " + i['name'])
        else:
            raise e

    return nordigen_client


def connection_check(nordigen_client):
    nordigen_client.institution.get_institution_id_by_name("DE", "comdirect")
    print(f"token works.")
