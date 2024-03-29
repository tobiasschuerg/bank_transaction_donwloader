import argparse
import csv
import os
from datetime import datetime

import database
from database import get_categories, get_transactions


def export_transactions(output_dir, start_date=None):
    print(f"Exporting transactions starting from {start_date}")
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
            writer = csv.writer(csvfile)
            writer.writerow(transaction.keys())
            for transaction in transactions:
                writer.writerow(transaction)
    print(f"Transactions exported to {output_dir}")


def export_creditor_category(path):
    categories = get_categories()
    transactions = get_transactions()

    output_file = os.path.join(path, "classifier_data.py")

    with open(output_file, "w", encoding="utf-8") as classifier_file:
        classifier_file.write("training_data = [\n")
        for category in categories:
            escaped_category = category['category'].replace("'", "\\'")
            classifier_file.write(f"    ('{escaped_category}', '{escaped_category}'),\n")

        for transaction in transactions:
            category_name = transaction['category'].replace("'", "\\'") if transaction['category'] else ''
            if not category_name:
                continue
            debtor_name = transaction['debtorName'].replace("'", "\\'") if transaction['debtorName'] else ''
            creditor_name = transaction['creditorName'].replace("'", "\\'") if transaction['creditorName'] else ''
            description = transaction['description'].replace("'", "\\'")
            classifier_file.write(
                f"    ('{category_name}', '{debtor_name} {creditor_name} {description}'),\n")
        classifier_file.write("]\n")




def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


if __name__ == "__main__":
    output_directory = "data"

    # Get the first day of the current month
    now = datetime.now()
    default_date = datetime(now.year, now.month, 1)
    # Define the argument parser
    parser = argparse.ArgumentParser(description='Download bank transactions.')
    parser.add_argument('--date_from', help='The start date for transactions in YYYY-MM-DD format.',
                        default=default_date, type=valid_date)
    # Parse the arguments
    args = parser.parse_args()

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    export_start_date = args.date_from.strftime("%Y-%m-%d")
    export_transactions(output_directory, export_start_date)

    export_creditor_category(output_directory)
