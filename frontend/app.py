from flask import Flask, render_template, request

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
            SELECT t.transactionId, b.bankName, b.iban, t.bookingDate, t.valueDate, t.amount, t.currency, t.description, t.creditorName, t.creditorAccount, t.debtorAccount
            FROM transactions t
            JOIN banks b ON t.bankName = b.bankName
            WHERE b.bankName = ?
            ORDER BY t.bookingDate DESC
        ''', (selected_bank,))
    else:
        c.execute('''
            SELECT t.transactionId, b.bankName, b.iban, t.bookingDate, t.valueDate, t.amount, t.currency, t.description, t.creditorName, t.creditorAccount, t.debtorAccount
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


if __name__ == '__main__':
    app.run(debug=True)
