# app.py

from flask import request, jsonify, Blueprint
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split

from classifier.classifier import TransactionClassifier
from data.classifier_data import training_data

classifier_file = 'classifier.json'
vectorizer_file = 'vectorizer.json'

classifier_blueprint = Blueprint('classifier', __name__)

categories, transactions = zip(*training_data)
X_train, X_test, y_train, y_test = train_test_split(transactions, categories, random_state=42)

vectorizer = TfidfVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

all_categories = set(categories)

classifier_model = SGDClassifier(loss='log_loss', random_state=42)
classifier_model.partial_fit(X_train_vec, y_train, classes=list(all_categories))

classifier = TransactionClassifier(classifier_model, vectorizer, all_categories)


@classifier_blueprint.route('/api/suggest_category', methods=['POST'])
def suggest_category():
    transaction = request.form.get("transaction")
    if transaction is None:
        return jsonify({"error": "transaction is required"}), 400

    suggested_category, confidence = classifier.suggest_category(transaction)
    return jsonify({"suggested_category": suggested_category, "confidence": confidence})


def update_classifier(transaction):
    category = transaction['category']
    description = transaction['description']
    print(f"update classifier {category}: {description}")
    classifier.update_classifier(description, category)
