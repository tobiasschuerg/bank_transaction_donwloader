import datetime

from flask import render_template, request, Blueprint, jsonify

import database
from classifier.app import update_classifier
from database import get_banks_from_db
from date_util import calculate_past_date_string

data_blueprint = Blueprint('data', __name__)


@data_blueprint.route("/", methods=["GET"])
def index():
    bank_name = request.args.get("bankName")
    category = request.args.get('category', None)

    start_date = request.args.get("start_date")
    if not start_date:
        start_date = calculate_past_date_string(1) + "-01"

    end_date = request.args.get("end_date", "")

    transactions = database.get_transactions(bank_name, start_date, end_date, category)
    banks = get_banks_from_db()

    return render_template(
        "index.html",
        transactions=transactions,
        count=len(transactions),
        banks=banks,
        selected_bank=bank_name,
        start_date=start_date,
        end_date=end_date,
        category=category
    )


@data_blueprint.route('/categories')
def categories():
    start_month = request.args.get('start-month')
    end_month = request.args.get('end-month')

    # Convert to datetime.date objects if not None
    if start_month:
        start_month = datetime.datetime.strptime(start_month, "%Y-%m").date().strftime('%Y-%m')
    else:
        start_month = None
    if end_month:
        end_month = datetime.datetime.strptime(end_month, "%Y-%m").date().strftime('%Y-%m')
    else:
        end_month = None

    # Get category sums filtered by the selected months
    categories, category_sums, category_avg_sums = database.get_category_sums(start_month, end_month)

    # Get all unique months from the category sums and sort them
    months = sorted(set(month for sums in category_sums.values() for month in sums))

    return render_template('categories.html', categories=categories, category_sums=category_sums,
                           category_avg_sums=category_avg_sums,
                           months=months, start_month=start_month, end_month=end_month)


@data_blueprint.route('/api/categories', methods=['GET'])
def get_categories():
    categories = database.get_categories()
    return jsonify(categories)


@data_blueprint.route('/transaction/<transaction_id>/category', methods=['PUT'])
def update_transaction_category(transaction_id):
    data = request.get_json()
    category_id = data['category_id']

    transaction = database.transaction_set_category(transaction_id, category_id)

    update_classifier(transaction)
    return '', 204


@data_blueprint.route('/transaction/<transaction_id>/category', methods=['DELETE'])
def remove_transaction_category(transaction_id):
    database.transaction_remove_category(transaction_id)
    return '', 204


@data_blueprint.route('/transaction/<transaction_id>/description', methods=['PUT'])
def update_transaction_description(transaction_id):
    data = request.get_json()
    new_description = data['description']

    database.update_description(transaction_id, new_description)
    return '', 204
