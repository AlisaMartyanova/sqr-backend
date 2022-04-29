from os import environ
import model
from app import db, app


def config():
    USER = environ.get('USER_TEST')
    PASSWORD = environ.get('PASSWORD_TEST')
    HOST = environ.get('HOST_TEST')
    DB_PORT = environ.get('DB_PORT_TEST')
    DB_NAME = environ.get('DB_NAME_TEST')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@{}:{}/{}'.format(USER, PASSWORD, HOST, DB_PORT, DB_NAME)


def save_users(emails):
    unique = set(emails)
    for e in emails:
        model.User.get_or_create(e)
    users = len(model.User.query.filter_by().all())
    model.User.query.filter_by().delete()
    db.session.commit()
    assert len(unique) == users


def test_save_users():
    config()
    users = ['1234@sdf.com', '1234@sdf.com', 'sdfghj@sdf.com']
    save_users(users)


