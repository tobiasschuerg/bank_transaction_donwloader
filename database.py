import os
import sqlite3


def connect_to_db(db_folder="data", db_filename="transactions.db"):
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)

    db_filepath = os.path.join(db_folder, db_filename)
    conn = sqlite3.connect(db_filepath)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Create tables for transactions, banks, and categories
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        transactionId TEXT PRIMARY KEY,
                        bankId INTEGER NOT NULL,
                        bookingDate TEXT NOT NULL,
                        valueDate TEXT,
                        amount REAL NOT NULL,
                        currency TEXT NOT NULL,
                        description TEXT,
                        creditorName TEXT,
                        creditorAccount TEXT,
                        debtorName TEXT,
                        debtorAccount TEXT,
                        categoryId INTEGER,
                        FOREIGN KEY (bankId) REFERENCES banks (id),
                        FOREIGN KEY (categoryId) REFERENCES categories (id)
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS banks (
                        id INTEGER PRIMARY KEY,
                        bankName TEXT NOT NULL UNIQUE,
                        iban TEXT NOT NULL
                    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS categories (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL UNIQUE
                    )''')

    conn.commit()
    return conn


def get_transactions_from_db(selected_bank, without_category=False):
    conn = connect_to_db()
    c = conn.cursor()

    query = '''
            SELECT t.*, b.bankName, b.iban , c.name as category
            FROM transactions t
            JOIN banks b ON t.bankId = b.id
            LEFT JOIN categories c ON t.categoryId = c.id
    '''

    if selected_bank:
        query += f'WHERE b.bankName = "{selected_bank}"'

    if without_category:
        if selected_bank:
            query += " AND "
        else:
            query += " WHERE "
        query += f'category IS NULL'

    query += ' ORDER BY t.bookingDate DESC'
    print(query)
    c.execute(query)

    transactions = c.fetchall()
    conn.close()
    return transactions


def get_banks_from_db():
    conn = connect_to_db()
    c = conn.cursor()

    c.execute('SELECT bankName FROM banks ORDER BY bankName')
    banks = c.fetchall()
    conn.close()
    return banks


def get_or_create_bank(bank_name: str, iban: str) -> dict:
    conn = connect_to_db()
    c = conn.cursor()

    # Insert the bank information into the database if it doesn't exist
    c.execute('''SELECT * FROM banks WHERE bankName = ?''', (bank_name,))
    bank = c.fetchone()
    if bank is None:
        c.execute('''INSERT INTO banks (bankName, iban)
                    VALUES (?, ?)''', (bank_name, iban))
        conn.commit()
        c.execute('''SELECT * FROM banks WHERE bankName = ?''', (bank_name,))
        bank = c.fetchone()

    bank = dict(zip(bank.keys(), bank))
    conn.close()
    return bank


def insert_categories(categories_tuples):
    conn = connect_to_db()
    c = conn.cursor()

    # Insert categories into the database
    count = 0
    for category, _ in categories_tuples:
        c.execute('''SELECT * FROM categories WHERE name = ?''', (category,))
        result = c.fetchone()
        if result is None:
            c.execute('''INSERT INTO categories (name) VALUES (?)''', (category,))
            print("added " + category)
            count += 1

    conn.commit()
    conn.close()
    print(f"Categories saved to database")


def get_categories():
    conn = connect_to_db()
    c = conn.cursor()
    c.execute("SELECT * FROM categories ORDER BY name")
    categories = [{"id": row['id'], "category": row['name']} for row in c.fetchall()]
    conn.close()
    return categories


def transaction_set_category(transaction_id, category_id):
    conn = connect_to_db()
    c = conn.cursor()

    c.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
    category = c.fetchone()

    # Update the transaction with the category name
    c.execute('UPDATE transactions SET categoryId = ? WHERE transactionId = ?', (category['id'], transaction_id))

    conn.commit()
    conn.close()
