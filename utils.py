import os
import pprint
from uuid import uuid4

import yaml


def load_connection_details(file):
    connections_path = 'connections'
    if not os.path.exists(connections_path):
        os.makedirs(connections_path)
    connection_file = os.path.join(connections_path, file)

    if os.path.exists(connection_file):
        with open(connection_file, "r") as f:
            return yaml.safe_load(f)
    else:
        raise FileNotFoundError(connection_file)


# Save tokens and IDs to file
def store_connection(connection):
    connections_path = 'connections'
    if not os.path.exists(connections_path):
        os.makedirs(connections_path)

    connection_file = os.path.join(connections_path, f"{connection['bank_name']}.yaml")

    with open(connection_file, "w") as f:
        yaml.dump(connection, f)


# List all the connections
def list_connections():
    connections_path = 'connections'
    if not os.path.exists(connections_path):
        os.makedirs(connections_path)
    yaml_files = [f for f in os.listdir(connections_path) if f.endswith(".yaml")]
    return [load_connection_details(file) for file in yaml_files]


def get_requisition_id(nordigen_client, connection_details):
    if "bank_name" not in connection_details:
        name = input("Give this bank connection a custom name: ")
        if len(name) == 0:
            raise ValueError("name cannot be empty")
        connection_details["bank_name"] = name
        store_connection(connection_details)

    if "requisition_id" in connection_details:
        return connection_details["requisition_id"]
    else:
        # Initialize bank session
        print("Initializing bank session...")
        session = nordigen_client.initialize_session(
            institution_id=connection_details["institution_id"],
            redirect_uri="https://nordigen.com",
            reference_id=str(uuid4()),
            max_historical_days=connection_details["institution_total_days"]
        )

        # Get requisition_id and link to initiate authorization process with a bank
        link = session.link
        print(f"Bank authorization link: {link}")
        requisition_id = session.requisition_id

        connection_details["requisition_id"] = requisition_id
        store_connection(connection_details)
        input("use the link above to authorize and press <enter>")
        return requisition_id


def select_bank_connection(nordigen_client):
    connections = list_connections()
    # Prompt the user for the bank name or select an existing connection
    print("Enter the bank name or choose from the list of existing connections:")
    for idx, connection in enumerate(connections):
        print(idx, connection.get("bank_name", connection["institution_id"]))
    choice = input("> ")
    if choice.isdigit() and int(choice) < len(connections):
        connection_details = connections[int(choice)]
        print("Using existing institution ID.")
    else:
        print(f"Getting institution ID for {choice}...")
        institution_id = nordigen_client.institution.get_institution_id_by_name(
            country="DE",
            institution=choice
        )
        institution = nordigen_client.institution.get_institution_by_id(institution_id)
        pprint.pprint(institution)

        connection_details = {
            "institution_id": institution_id,
            "institution_logo": institution['logo'],
            "institution_total_days": institution['transaction_total_days']
        }
        print(f"Institution ID for {choice}: {institution_id}")
    return connection_details
