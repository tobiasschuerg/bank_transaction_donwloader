import os
import sqlite3


def connect_to_db(db_folder="transactions", db_filename="transactions.db"):
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)

    db_filepath = os.path.join(db_folder, db_filename)
    conn = sqlite3.connect(db_filepath)
    c = conn.cursor()

    # Create tables for banks and transactions if they don't exist
    c.execute('''CREATE TABLE IF NOT EXISTS banks (
                    bankName text PRIMARY KEY,
                    iban text NOT NULL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    transactionId text PRIMARY KEY,
                    bankName text NOT NULL,
                    bookingDate date NOT NULL,
                    valueDate date,
                    amount real NOT NULL,
                    currency text,
                    description text,
                    creditorName text,
                    creditorAccount text,
                    debtorAccount text,
                    FOREIGN KEY (bankName) REFERENCES banks(bankName))''')
    return conn
