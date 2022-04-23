from os import environ
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/SantaDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = ''

db = SQLAlchemy(app)

import model
import resources

api = Api(app)

# map urls with functions
api.add_resource(resources.Event, '/events')
api.add_resource(resources.UserLogin, '/login')
api.add_resource(resources.Invitation, '/invitation')
api.add_resource(resources.Wishlist, '/wishlist')
api.add_resource(resources.AssignGiftees, '/assignee')


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == '__main__':
    app.run('0.0.0.0', environ.get('PORT', 8000))
