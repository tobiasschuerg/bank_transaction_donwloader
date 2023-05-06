from data.classifier_data import data
from database import insert_categories
from frontend.flask import app

if __name__ == '__main__':
    insert_categories(data)

    app.run(debug=True)
