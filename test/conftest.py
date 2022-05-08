from app import app
from os import environ
import model
from app import db


def pytest_configure():
    USER = environ.get('USER_TEST')
    PASSWORD = environ.get('PASSWORD_TEST')
    HOST = environ.get('HOST_TEST')
    DB_PORT = environ.get('DB_PORT_TEST')
    DB_NAME = environ.get('DB_NAME_TEST')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@{}:{}/{}'\
        .format(USER, PASSWORD, HOST, DB_PORT, DB_NAME)


def pytest_unconfigure():
    model.Membership.query.filter_by().delete()
    model.Event.query.filter_by().delete()
    model.User.query.filter_by().delete()
    db.session.commit()
