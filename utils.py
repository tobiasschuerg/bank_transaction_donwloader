import os

import yaml


def load_tokens_and_ids(bank_name):
    if os.path.exists(f"connections/{bank_name}_tokens_and_ids.yaml"):
        with open(f"connections/{bank_name}_tokens_and_ids.yaml", "r") as f:
            return yaml.safe_load(f)
    return {}


def save_tokens_and_ids(tokens_and_ids, bank_name):
    with open(f"connections/{bank_name}_tokens_and_ids.yaml", "w") as f:
        yaml.dump(tokens_and_ids, f)
