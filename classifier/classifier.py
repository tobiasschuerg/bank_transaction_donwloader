# classifier.py
import numpy as np


class TransactionClassifier:
    def __init__(self, classifier, vectorizer, all_categories):
        self.classifier = classifier
        self.vectorizer = vectorizer
        self.all_categories = all_categories

    def suggest_category(self, transaction):
        transaction_vec = self.vectorizer.transform([transaction])
        predict = self.classifier.predict(transaction_vec)
        predict_proba = self.classifier.predict_proba(transaction_vec)
        category = predict[0]
        confidence = np.max(predict_proba)
        return category, confidence

    def update_classifier(self, transaction, category):
        new_category = False
        if category not in self.all_categories:
            self.all_categories.add(category)
            new_category = True

        transaction_vec = self.vectorizer.transform([transaction])

        if new_category:
            self.classifier.classes_ = np.array(list(self.all_categories))
            new_coef = np.zeros((len(self.all_categories), self.classifier.coef_.shape[1]))
            new_intercept = np.zeros(len(self.all_categories))

            new_coef[:-1, :] = self.classifier.coef_
            new_intercept[:-1] = self.classifier.intercept_

            self.classifier.coef_ = new_coef
            self.classifier.intercept_ = new_intercept

        self.classifier.partial_fit(transaction_vec, [category])
