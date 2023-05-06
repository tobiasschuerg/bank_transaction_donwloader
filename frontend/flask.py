from datetime import datetime

import database
from database import get_banks_from_db
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    bank_name = request.args.get("bankName")
    filter_no_category = request.args.get('category_missing')

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    transactions = database.get_transactions(bank_name, start_date, end_date, filter_no_category)
    banks = get_banks_from_db()

    return render_template(
        "index.html",
        transactions=transactions,
        count=len(transactions),
        banks=banks,
        selected_bank=bank_name,
        start_date=start_date,
        end_date=end_date
    )


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


@app.route('/transaction/<transaction_id>/description', methods=['PUT'])
def update_transaction_description(transaction_id):
    data = request.get_json()
    new_description = data['description']

    database.update_description(transaction_id, new_description)
    return '', 204
