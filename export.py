import csv
import os
import sqlite3
from datetime import date, timedelta

import database
from database import connect_to_db


def export_transactions(output_dir, date=None):
    # Connect to SQLite database
    db_folder = "data"
    db_filename = "transactions.db"
    db_filepath = os.path.join(db_folder, db_filename)
    conn = sqlite3.connect(db_filepath)
    c = conn.cursor()

    transactions = database.get_transactions_from_db(None)

    # Group transactions by bank name
    transactions_by_bank = {}
    for transaction in transactions:
        bank_name = transaction['bankName']
        bank_iban = transaction['iban']
        if bank_name not in transactions_by_bank:
            transactions_by_bank[bank_name] = (bank_iban, [])
        transactions_by_bank[bank_name][1].append(transaction)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for bank_name, (bank_iban, transactions) in transactions_by_bank.items():
        csv_filename = f"{bank_iban}_{bank_name}.csv"
        csv_filepath = os.path.join(output_dir, csv_filename)
        with open(csv_filepath, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["transactionId", "bookingDate", "valueDate", "amount", "currency", "description",
                          "creditorName",
                          "creditorAccount", "debtorAccount"]
            writer = csv.writer(csvfile)
            writer.writerow(fieldnames)
            for transaction in transactions:
                writer.writerow((transaction[0],) + transaction[2:9])
    print(f"Transactions exported to {output_dir}")


def export_creditor_category(path):
    conn = connect_to_db()
    c = conn.cursor()

    # Retrieve creditor names and categories from the database
    c.execute('''SELECT t.description, t.creditorName, c.name as category
                FROM transactions t
                JOIN categories c ON t.categoryId = c.id
                WHERE t.categoryId IS NOT NULL''')
    creditor_categories = c.fetchall()

    # Check if the directory exists, create it if it doesn't
    if not os.path.exists(path):
        os.makedirs(path)

    output_file = os.path.join(path, "classifier_data.py")

    with open(output_file, "w", encoding="utf-8") as classifier_file:
        classifier_file.write("data = [\n")
        for description, name, category in creditor_categories:
            classifier_file.write(f"    ('{category}', '{name}: {description}'),\n")
        classifier_file.write("]\n")


if __name__ == "__main__":
    output_directory = "data"

    export_start_date = date.today() - timedelta(days=30)
    export_transactions(output_directory, export_start_date)

    export_creditor_category(output_directory)
