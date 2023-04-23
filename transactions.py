import csv
import os


def store_transactions(transactions, bank_name, iban):
    # Save transactions to CSV
    csv_folder = "transactions"
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)
    csv_filename = f"{iban}_{bank_name}.csv"
    csv_filepath = os.path.join(csv_folder, csv_filename)
    existing_transactions = []
    if os.path.exists(csv_filepath):
        # If the file already exists, read the existing transactions
        with open(csv_filepath, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            existing_transactions = [row for row in reader]

    # Remove duplicate transactions from the list of new transactions
    new_transactions = []
    for transaction in transactions:
        if not any(t.get("transactionId") == transaction.get("transactionId") and t.get("bookingDate") == transaction.get("bookingDate") for t in existing_transactions):
            new_transactions.append(transaction)

    # Append new transactions to the existing file
    with open(csv_filepath, "a", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["transactionId", "bookingDate", "valueDate", "amount", "currency", "description", "creditorName",
                      "creditorAccount", "debtorAccount"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if os.path.getsize(csv_filepath) == 0:
            # If the file is empty, write the header
            writer.writeheader()
        for transaction in new_transactions:
            transaction_id = transaction.get("transactionId", transaction.get("internalTransactionId"))
            writer.writerow({
                "transactionId": transaction_id,
                "bookingDate": transaction.get("bookingDate"),
                "valueDate": transaction.get("valueDate", None),
                "amount": transaction["transactionAmount"]['amount'],
                "currency": transaction['transactionAmount']["currency"],
                "description": transaction.get("remittanceInformationUnstructured",
                                               transaction.get("remittanceInformationUnstructuredArray")),
                "creditorName": transaction.get("creditorName", ""),
                "creditorAccount": transaction.get("creditorAccount", {}).get("iban", None),
                "debtorAccount": transaction.get("debtorAccount", {}).get("iban", None),
            })
    print(f"Transactions saved to {csv_filepath}")
