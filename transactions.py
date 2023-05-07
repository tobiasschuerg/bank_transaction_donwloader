import re

import database
from database import get_or_create_bank


def store_transactions(transactions, bank_name, iban):
    # Connect to SQLite database
    conn = database.connect_to_db()
    c = conn.cursor()

    bank = get_or_create_bank(bank_name, iban)

    # Insert new transactions into the database
    for transaction in transactions:
        transaction_id = transaction.get("transactionId", transaction.get("internalTransactionId"))
        c.execute('''SELECT transactionId FROM transactions WHERE transactionId = ?''', (transaction_id,))
        existing_transaction = c.fetchone()

        if existing_transaction:
            print(f"Transaction with ID {transaction_id} already exists in the database")
        else:
            description = extract_description(transaction)

            c.execute('''INSERT INTO transactions 
                        (transactionId, bankId, bookingDate, valueDate, amount, 
                        currency, description, creditorName, creditorAccount, debtorName, debtorAccount)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                transaction_id,
                bank['id'],
                transaction.get("bookingDate"),
                transaction.get("valueDate", None),
                transaction["transactionAmount"]['amount'],
                transaction['transactionAmount']["currency"],
                description,
                transaction.get("creditorName", None),
                transaction.get("creditorAccount", {}).get("iban", None),
                transaction.get("debtorName", None),
                transaction.get("debtorAccount", {}).get("iban", None)
            ))

    conn.commit()
    conn.close()
    print(f"Transactions saved to database")


def extract_description(transaction):
    description = transaction.get("remittanceInformationUnstructured")

    if description is not None:
        description = description.replace("; ", "")  # comdirect seems to replace line wraps
    else:
        description_array = transaction.get("remittanceInformationUnstructuredArray")
        description = ' '.join(description_array) if description_array else ""

    description = re.sub(r'\s+', ' ', description)  # replace multiple whitespaces by a single one
    return description
