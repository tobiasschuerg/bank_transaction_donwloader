import os
import sqlite3


def connect_to_db(db_folder="transactions", db_filename="transactions.db"):
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)

    db_filepath = os.path.join(db_folder, db_filename)
    conn = sqlite3.connect(db_filepath)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Create tables for transactions, banks, and categories
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        transactionId TEXT PRIMARY KEY,
                        bankName TEXT NOT NULL,
                        bookingDate TEXT NOT NULL,
                        valueDate TEXT,
                        amount REAL NOT NULL,
                        currency TEXT NOT NULL,
                        description TEXT,
                        creditorName TEXT,
                        creditorAccount TEXT,
                        debtorAccount TEXT,
                        category TEXT,
                        FOREIGN KEY (bankName) REFERENCES banks (bankName),
                        FOREIGN KEY (category) REFERENCES categories (category)
                    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS banks (
                        bankName TEXT PRIMARY KEY,
                        iban TEXT NOT NULL
                    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS categories (
                        id INTEGER PRIMARY KEY,
                        category TEXT NOT NULL UNIQUE
                    )''')

    conn.commit()
    return conn
