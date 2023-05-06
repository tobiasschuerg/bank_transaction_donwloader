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
        result = c.fetchone()
        if result is None:
            c.execute('''INSERT INTO transactions (transactionId, bankId, bookingDate, valueDate, amount, currency, description, creditorName, creditorAccount, debtorAccount)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                transaction_id,
                bank['id'],
                transaction.get("bookingDate"),
                transaction.get("valueDate", None),
                transaction["transactionAmount"]['amount'],
                transaction['transactionAmount']["currency"],
                transaction.get("remittanceInformationUnstructured",
                                transaction.get("remittanceInformationUnstructuredArray")),
                transaction.get("creditorName", ""),
                transaction.get("creditorAccount", {}).get("iban", None),
                transaction.get("debtorAccount", {}).get("iban", None)
            ))
        else:
            print(f"Transaction with ID {transaction_id} already exists in the database")
    conn.commit()
    conn.close()
    print(f"Transactions saved to database")
