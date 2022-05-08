from os import environ
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['BUNDLE_ERRORS'] = True
# fix cringe: https://stackoverflow.com/questions/71950802/flask-cors-work-only-for-first-request-whats-the-bug-in-my-code
# CORS(app)

# configure database postgres
USER = environ.get('USER')
PASSWORD = environ.get('PASSWORD')
HOST = environ.get('HOST')
DB_PORT = environ.get('DB_PORT')
DB_NAME = environ.get('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@{}:{}/{}'.format(
                                        USER, PASSWORD, HOST, DB_PORT, DB_NAME)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = environ.get('FLASK_SECRET')

db = SQLAlchemy(app)

import model
import resources

api = Api(app)

# map urls with functions
api.add_resource(resources.Event, '/events')
api.add_resource(resources.Invitation, '/invitation')
api.add_resource(resources.Wishlist, '/wishlist')
api.add_resource(resources.AssignGiftees, '/assignee')


# fix cringe: https://stackoverflow.com/questions/71950802/flask-cors-work-only-for-first-request-whats-the-bug-in-my-code
@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Headers', 'Token, content-type')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Methods', 'PUT, GET, POST, DELETE, PATCH, OPTIONS')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.before_first_request
def create_tables():
    # create test users with simple authentication
    model.User.get_or_create(f"alisa-test@santa.com")
    for i in range(10):
        model.User.get_or_create(f"test{i}@santa.com")
    db.create_all()


if __name__ == '__main__':
    app.run('0.0.0.0', environ.get('PORT', 8000))
    