from flask import Flask

from classifier.app import classifier_blueprint
from data.classifier_data import training_data
from database import insert_categories
from frontend.flask import data_blueprint

if __name__ == '__main__':
    insert_categories(training_data)

    app = Flask(__name__,
                template_folder="frontend/templates",
                static_folder="frontend/static")

    app.register_blueprint(data_blueprint)
    app.register_blueprint(classifier_blueprint)

    app.run(debug=True)
