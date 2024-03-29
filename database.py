import datetime
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


def get_transactions(bank_name=None, start_date=None, end_date=None, category=None):
    conn = connect_to_db()
    c = conn.cursor()

    query = '''
             SELECT t.*, b.bankName, b.iban , c.name as category
             FROM transactions t
             JOIN banks b ON t.bankId = b.id
             LEFT JOIN categories c ON t.categoryId = c.id
     '''

    # Add filtering conditions
    conditions = []
    params = []

    if bank_name:
        conditions.append("bankName = ?")
        params.append(bank_name)

    if start_date:
        conditions.append("bookingDate >= ?")
        params.append(start_date)

    if end_date:
        conditions.append("bookingDate <= ?")
        params.append(end_date)

    if category is not None:
        conditions.append(f"categoryId IS {category}")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY bookingDate DESC"

    print(query)
    print(conditions)

    c.execute(query, params)
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

    c.execute('''
            SELECT t.*, b.bankName, b.iban , c.name as category
            FROM transactions t
            JOIN banks b ON t.bankId = b.id
            LEFT JOIN categories c ON t.categoryId = c.id
            WHERE transactionId = ?
    ''', (transaction_id,))
    transaction = c.fetchone()
    conn.close()
    return transaction


def transaction_remove_category(transaction_id):
    conn = connect_to_db()
    c = conn.cursor()

    # Update the transaction with the category ID set to NULL
    c.execute('UPDATE transactions SET categoryId = NULL WHERE transactionId = ?', (transaction_id,))
    conn.commit()
    conn.close()


def update_description(transaction_id, new_description):
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute(
        '''
        UPDATE transactions
        SET description = ?
        WHERE transactionId = ?
        ''',
        (new_description, transaction_id)
    )

    conn.commit()
    cursor.close()


def get_category_sums(start_month: datetime.date = None, end_month: datetime.date = None):
    conn = connect_to_db()
    c = conn.cursor()

    query = '''
    SELECT categories.id, categories.name, strftime('%Y-%m', transactions.bookingDate) as month, SUM(transactions.amount) as sum
    FROM transactions
    JOIN categories ON transactions.categoryId = categories.id
    WHERE month >= ? AND month <= ?
    GROUP BY categories.name, month
    ORDER BY month DESC, categories.name
    '''
    print(f"parameters: {start_month, end_month}")

    if start_month is None:
        start_month = '0000-00'  # This represents the earliest possible date
    else:
        start_month = start_month

    if end_month is None:
        end_month = '9999-12'  # This represents the latest possible date
    else:
        # Add one month to the end_month
        end_month = end_month

    print(f"Executing query: {query} with parameters: {start_month, end_month}")
    c.execute(query, (start_month, end_month))

    categories = {}
    category_sums = {}
    category_avg_sums = {}
    for row in c.fetchall():
        categories[row['name']] = row['id']
        if row['name'] not in category_sums:
            category_sums[row['name']] = {}
        category_sums[row['name']][row['month']] = row['sum']

        if row['name'] not in category_avg_sums:
            category_avg_sums[row['name']] = {'total': 0, 'count': 0}
        category_avg_sums[row['name']]['total'] += row['sum']
        category_avg_sums[row['name']]['count'] += 1

    # Calculate average sum for each category
    for category in category_avg_sums:
        category_avg_sums[category] = category_avg_sums[category]['total'] / category_avg_sums[category]['count']

    # Sort categories by name
    category_sums = dict(sorted(category_sums.items()))

    conn.close()

    return categories, category_sums, category_avg_sums
