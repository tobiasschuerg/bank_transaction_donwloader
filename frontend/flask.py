import database
from database import get_transactions_from_db, get_banks_from_db
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    selected_bank = request.args.get('bankName', '')
    filter_no_category = request.args.get('category_missing')

    transactions = get_transactions_from_db(selected_bank, filter_no_category)

    banks = get_banks_from_db()
    return render_template('index.html', transactions=transactions, count=len(transactions), banks=banks, selected_bank=selected_bank)


@app.route('/categories', methods=['GET'])
def get_categories():
    categories = database.get_categories()
    return jsonify(categories)


@app.route('/transaction/<transaction_id>/category', methods=['PUT'])
def update_transaction_category(transaction_id):
    data = request.get_json()
    category_id = data['category_id']

    database.transaction_set_category(transaction_id, category_id)
    return '', 204
