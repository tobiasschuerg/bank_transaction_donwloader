import credentials
import utils
from transactions import store_transactions


def process_account(account, bank_name):
    # Fetch account metadata
    meta_data = account.get_metadata()
    # pprint.pprint(meta_data)
    print(f"Account: {meta_data['iban']} {meta_data['owner_name']}")
    # Fetch details
    # details = account.get_details()
    # pprint.pprint(details)
    # Fetch balances
    # balances = account.get_balances()
    # print("Account balances")
    # pprint.pprint(balances, indent=4)
    # Fetch transactions for the selected account
    transactions = account.get_transactions(date_from="2023-01-01")['transactions']['booked']
    print(f"Got {len(transactions)} transactions from {bank_name}")
    store_transactions(transactions, bank_name, meta_data['iban'])


if __name__ == '__main__':
    nordigen_client = credentials.create_nordigen_client()
    connection_details = utils.select_bank_connection(nordigen_client)
    requisition_id = utils.get_requisition_id(nordigen_client, connection_details)

    # Fetch the account list
    requisition = nordigen_client.requisition.get_requisition_by_id(requisition_id=requisition_id)

    for account_id in requisition['accounts']:
        account = nordigen_client.account_api(id=account_id)
        process_account(account, connection_details["bank_name"])
