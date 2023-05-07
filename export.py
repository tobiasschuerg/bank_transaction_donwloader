import csv
import os
from datetime import date, timedelta

import database
from database import get_categories, get_transactions


def export_transactions(output_dir, start_date=None):
    transactions = database.get_transactions(start_date=start_date)

    # Group transactions by bank name
    transactions_by_bank = {}
    for transaction in transactions:
        bank_name = transaction['bankName']
        bank_iban = transaction['iban']
        if bank_name not in transactions_by_bank:
            transactions_by_bank[bank_name] = (bank_iban, [])
        transactions_by_bank[bank_name][1].append(transaction)

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
    categories = get_categories()
    transactions = get_transactions()

    output_file = os.path.join(path, "classifier_data.py")

    with open(output_file, "w", encoding="utf-8") as classifier_file:
        classifier_file.write("training_data = [\n")
        for category in categories:
            classifier_file.write(f"    ('{category['category']}', '{category['category']}'),\n")

        for transaction in transactions:
            category_name = transaction['category']
            if not category_name:
                continue
            debtor_name = transaction['debtorName'] if transaction['debtorName'] else ''
            creditor_name = transaction['creditorName'] if transaction['creditorName'] else ''
            classifier_file.write(
                f"    ('{category_name}', '{debtor_name} {creditor_name} {transaction['description']}'),\n")
        classifier_file.write("]\n")


if __name__ == "__main__":
    output_directory = "data"

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    export_start_date = date.today() - timedelta(days=30)
    export_transactions(output_directory, export_start_date)

    export_creditor_category(output_directory)
