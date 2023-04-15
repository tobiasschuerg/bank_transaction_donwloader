# main.py

import csv
import os
from uuid import uuid4

import yaml
from nordigen import NordigenClient

from credentials import load_credentials
from utils import load_tokens_and_ids, save_tokens_and_ids, list_connections

# Load credentials from file or prompt user
credentials = load_credentials()

# Initialize Nordigen client with SECRET_ID and SECRET_KEY
client = NordigenClient(
    secret_id=credentials["SECRET_ID"],
    secret_key=credentials["SECRET_KEY"]
)

# List existing connections
connections = list_connections()

# Prompt the user for the bank name or select an existing connection
print("Enter the bank name or choose from the list of existing connections:")
for idx, connection in enumerate(connections):
    print(f"{idx}. {connection}")

choice = input("> ")

if choice.isdigit() and int(choice) < len(connections):
    bank_name = connections[int(choice)]
else:
    bank_name = choice

# Load tokens and IDs from file
tokens_and_ids = load_tokens_and_ids(bank_name)

# Check if access_token is not set and generate it
if "access_token" not in credentials:
    print("Generating access token...")
    token_data = client.generate_token()
    credentials["access_token"] = token_data["access"]
    credentials["refresh_token"] = token_data["refresh"]
    with open("credentials.yaml", "w") as f:
        yaml.dump(credentials, f)
    print("New access token generated.")
else:
    print("Using existing access token.")
    client.token = credentials["access_token"]

# Check if institution_id is not set and get it
if "institution_id" not in tokens_and_ids:
    print(f"Getting institution ID for {bank_name}...")
    institution_id = client.institution.get_institution_id_by_name(
        country="DE",
        institution=bank_name
    )
    tokens_and_ids["institution_id"] = institution_id
    save_tokens_and_ids(tokens_and_ids, bank_name)
    print(f"Institution ID for {bank_name}: {institution_id}")
else:
    print("Using existing institution ID.")
    institution_id = tokens_and_ids["institution_id"]

if "requisition_id" not in tokens_and_ids:
    # Initialize bank session
    print("Initializing bank session...")
    session = client.initialize_session(
        institution_id=institution_id,
        redirect_uri="https://nordigen.com",
        reference_id=str(uuid4()),
        max_historical_days=360
    )

    # Get requisition_id and link to initiate authorization process with a bank
    link = session.link
    print(f"Bank authorization link: {link}")
    requisition_id = session.requisition_id

    tokens_and_ids["requisition_id"] = requisition_id
    save_tokens_and_ids(bank_name, tokens_and_ids)
    input("use the link above to authorize and press any key")
else:
    requisition_id = tokens_and_ids["requisition_id"]

# Fetch the account list
accounts = client.requisition.get_requisition_by_id(
    requisition_id=requisition_id
)

# Choose an account ID to fetch transactions
if len(accounts['accounts']) == 1:
    account_index = 0
else:
    print("Accounts:")
    for idx, x in enumerate(accounts['accounts']):
        print(idx, x)
    account_index = input("Enter the account ID to fetch transactions: ")

account = client.account_api(id=accounts['accounts'][int(account_index)])

# Fetch account metadata
meta_data = account.get_metadata()
print(f"Account: {meta_data['iban']} {meta_data['owner_name']}")

# Fetch details
# details = account.get_details()
# print("Account details:", details)

# Fetch balances
balances = account.get_balances()
print("Account balances:", balances)

# Fetch transactions for the selected account
transactions = account.get_transactions(date_from="2023-01-01")['transactions']['booked']

print("Transactions:", transactions)

# Save transactions to CSV
csv_folder = "transactions"
if not os.path.exists(csv_folder):
    os.makedirs(csv_folder)

csv_filename = f"{bank_name}_{meta_data['iban']}_transactions.csv"
csv_filepath = os.path.join(csv_folder, csv_filename)

with open(csv_filepath, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["transactionId", "bookingDate", "valueDate", "amount", "currency", "description", "creditorName",
                  "creditorAccount", "debtorAccount"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for transaction in transactions:
        transaction_id = transaction.get("transactionId", transaction.get("internalTransactionId"))
        writer.writerow({
            "transactionId": transaction_id,
            "bookingDate": transaction["bookingDate"],
            "valueDate": transaction["valueDate"],
            "amount": transaction["transactionAmount"]['amount'],
            "currency": transaction['transactionAmount']["currency"],
            "description": transaction.get("remittanceInformationUnstructured",
                                           transaction.get("remittanceInformationUnstructuredArray")),
            "creditorName": transaction.get("creditorName", ""),
            "creditorAccount": transaction.get("creditorAccount", {}).get("iban", ""),
            "debtorAccount": transaction.get("debtorAccount", {}).get("iban", ""),
        })

print(f"Transactions saved to {csv_filepath}")
