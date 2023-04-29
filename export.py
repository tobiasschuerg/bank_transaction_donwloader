import csv
import os
import sqlite3
from datetime import date, timedelta


def export_transactions(date=None):
    # Connect to SQLite database
    db_folder = "transactions"
    db_filename = "transactions.db"
    db_filepath = os.path.join(db_folder, db_filename)
    conn = sqlite3.connect(db_filepath)
    c = conn.cursor()

    # Retrieve all transactions from the database
    c.execute('''SELECT t.transactionId, t.bankName, t.bookingDate, t.valueDate, t.amount, t.currency, t.description, t.creditorName, t.creditorAccount, t.debtorAccount, b.iban
                FROM transactions t
                JOIN banks b ON t.bankName = b.bankName
                WHERE t.bookingDate >= ?''', (date.isoformat(),))
    transactions = c.fetchall()

    # Group transactions by bank name
    transactions_by_bank = {}
    for transaction in transactions:
        bank_name = transaction[1]
        bank_iban = transaction[10]
        if bank_name not in transactions_by_bank:
            transactions_by_bank[bank_name] = (bank_iban, [])
        transactions_by_bank[bank_name][1].append(transaction)

    # Save transactions to CSV
    csv_folder = "transactions"
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)
    for bank_name, (bank_iban, transactions) in transactions_by_bank.items():
        csv_filename = f"{bank_iban}_{bank_name}.csv"
        csv_filepath = os.path.join(csv_folder, csv_filename)
        with open(csv_filepath, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["transactionId", "bookingDate", "valueDate", "amount", "currency", "description",
                          "creditorName",
                          "creditorAccount", "debtorAccount"]
            writer = csv.writer(csvfile)
            writer.writerow(fieldnames)
            for transaction in transactions:
                writer.writerow((transaction[0],) + transaction[2:9])
    print(f"Transactions exported to {csv_folder}")


if __name__ == "__main__":
    start_date = date.today() - timedelta(days=30)
    export_transactions(start_date)
