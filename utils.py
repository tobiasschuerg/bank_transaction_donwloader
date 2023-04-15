import os

import yaml


# Load tokens and IDs from file
def load_tokens_and_ids(bank_name):
    connections_path = 'connections'
    if not os.path.exists(connections_path):
        os.makedirs(connections_path)

    connection_file = os.path.join(connections_path, f"{bank_name}.yaml")

    if os.path.exists(connection_file):
        with open(connection_file, "r") as f:
            return yaml.safe_load(f)
    return {}


# Save tokens and IDs to file
def save_tokens_and_ids(bank_name, tokens_and_ids):
    connections_path = 'connections'
    if not os.path.exists(connections_path):
        os.makedirs(connections_path)

    connection_file = os.path.join(connections_path, f"{bank_name}.yaml")

    with open(connection_file, "w") as f:
        yaml.dump(tokens_and_ids, f)


# List all the connections
def list_connections():
    connections_path = 'connections'
    if not os.path.exists(connections_path):
        os.makedirs(connections_path)
    yaml_files = [f for f in os.listdir(connections_path) if f.endswith(".yaml")]
    return [os.path.splitext(file)[0] for file in yaml_files]
