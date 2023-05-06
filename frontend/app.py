import pprint

from flask import Flask, render_template, request, jsonify

from database import connect_to_db

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    selected_bank = request.args.get('bankName', '')
    transactions = get_transactions_from_db(selected_bank)
    banks = get_banks_from_db()
    return render_template('index.html', transactions=transactions, banks=banks, selected_bank=selected_bank)


def get_transactions_from_db(selected_bank):
    conn = connect_to_db("../transactions")
    c = conn.cursor()

    if selected_bank:
        c.execute('''
            SELECT *
            FROM transactions t
            JOIN banks b ON t.bankName = b.bankName
            WHERE b.bankName = ?
            ORDER BY t.bookingDate DESC
        ''', (selected_bank,))
    else:
        c.execute('''
            SELECT *
            FROM transactions t
            JOIN banks b ON t.bankName = b.bankName
            ORDER BY t.bookingDate DESC
        ''')
    transactions = c.fetchall()
    conn.close()
    return transactions


def get_banks_from_db():
    conn = connect_to_db("../transactions")
    c = conn.cursor()

    c.execute('SELECT bankName FROM banks ORDER BY bankName')
    banks = c.fetchall()
    conn.close()
    return banks


@app.route('/categories', methods=['GET'])
def get_categories():
    conn = connect_to_db("../transactions")
    c = conn.cursor()
    c.execute("SELECT * FROM categories")
    categories = [{"id": row['id'], "category": row['category']} for row in c.fetchall()]
    conn.close()
    return jsonify(categories)


@app.route('/transaction/<transaction_id>/category', methods=['PUT'])
def update_transaction_category(transaction_id):
    data = request.get_json()
    category_id = data['category_id']

    conn = connect_to_db("../transactions")
    c = conn.cursor()

    # Get the category name based on the category ID
    c.execute("SELECT category FROM categories WHERE id = ?", (category_id,))
    category = c.fetchone()[0]

    # Update the transaction with the category name
    c.execute('UPDATE transactions SET category = ? WHERE transactionId = ?', (category, transaction_id))
    conn.commit()
    conn.close()

    return '', 204


if __name__ == '__main__':
    app.run(debug=True)
