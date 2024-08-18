from requests import HTTPError

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
    account_get_transactions = account.get_transactions(date_from="2023-03-01")
    transactions = account_get_transactions['transactions']['booked']
    print(f"Got {len(transactions)} transactions from {bank_name}")
    store_transactions(transactions, bank_name, meta_data['iban'])


def reset_connection(cd):
    cd.pop('requisition_id')
    utils.store_connection(cd)
    print("connection reset, please try again1")


if __name__ == '__main__':
    nordigen_client = credentials.create_nordigen_client()
    bank_connections = utils.select_bank_connection(nordigen_client)
    print(f"Selected {len(bank_connections)} bank connections.")
    for connection_details in bank_connections:
        requisition_id = utils.get_requisition_id(nordigen_client, connection_details)

        # Fetch the account list
        requisition = nordigen_client.requisition.get_requisition_by_id(requisition_id=requisition_id)
        if len(requisition['accounts']) == 0:
            print("No accounts found")
            reset_connection(connection_details)
        for account_id in requisition['accounts']:
            account = nordigen_client.account_api(id=account_id)
            try:
                process_account(account, connection_details["bank_name"])
            except HTTPError as e:
                print(e)
                status_code = e.response.status_code
                if status_code == 400:
                    print("Maybe license expired")
                    reset_connection(connection_details)
                elif status_code == 401:
                    print("Please reconnect account")
                    print("Manually remove the requisition_id from the configuration")
                    print("... and retry")
                    reset_connection(connection_details)

                exit(status_code)
