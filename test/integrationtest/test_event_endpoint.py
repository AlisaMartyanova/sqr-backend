import requests
import json
from datetime import datetime
from os import environ

from werkzeug.exceptions import HTTPException
from werkzeug.routing import ValidationError

from app import app
from test import conftest
import resources, model


class Test:
    data = {
        "email": environ.get('TEST_USER_EMAIL'),
        "password": environ.get('TEST_USER_PASSWORD'),
        "returnSecureToken": True
    }
    resp = requests.post(environ.get('TEST_URL'), data=data)
    token = str(resp.json()['idToken'])

    event_info = {
            'event_name': 'Event1',
            'date': datetime.strptime('2022-02-25', '%Y-%m-%d'),
            'place': 'University',
            'state': True,
            'wishlist': "This is my wishlist",
            'wrong_event_id': 0,
            'members': ['1234@sdf.com', 'sdfghj@sdf.com', 'sdfhnjjhghj@kjh.com']
        }

    def test_blank_token_post(self):
        response = app.test_client().post('/events')
        assert json.loads(response.data.decode('utf-8')) == {'message': {'token': 'This field cannot be blank'}}

    def test_invalid_token_post(self):
        response = app.test_client().post('/events', headers={'token': 'token'})
        assert json.loads(response.data.decode('utf-8')) == {'message': 'Invalid Firebase ID Token'}

    def test_blank_field_post(self):
        response = app.test_client().post('/events', headers={'token': self.token},
                                          json={'name': self.event_info['event_name'], 'gift_date': '2022-02-25'})
        assert json.loads(response.data.decode('utf-8')) == \
               {'message': {'location': 'This field cannot be blank', 'members': 'This field cannot be blank'}}

    def test_invite_yourself(self):
        response = app.test_client().post('/events', headers={'token': self.token},
                                   json={'name': self.event_info['event_name'],
                                         'gift_date': '2022-02-25',
                                         'location': self.event_info['place'],
                                         'members': [self.data['email']]})
        assert json.loads(response.data.decode('utf-8')) == {'message': {'members': "You cannot invite yourself (%s)" % self.data['email']}}

    # def test_no_members(self):
    #     response = app.test_client().post('/events', headers={'token': self.token},
    #                            json={'name': self.event_info['event_name'],
    #                                  'gift_date': '2022-02-25',
    #                                  'location': self.event_info['place'],
    #                                  'members': [None]})
    #     assert json.loads(response.data.decode('utf-8')) == "At least 1 member of event is required"

    def test_post_event(self):
        conftest.pytest_unconfigure()
        member = model.User.get_or_create(self.event_info['members'][0]).email
        response = app.test_client().post('/events', headers={'token': self.token},
                                   json={'name': self.event_info['event_name'],
                                         'gift_date': '2022-02-25',
                                         'location': self.event_info['place'],
                                         'members': [member]})
        assert json.loads(response.data.decode('utf-8'))['name'] == self.event_info['event_name']

    def test_blank_token_get(self):
        response = app.test_client().get('/events')
        assert json.loads(response.data.decode('utf-8')) == {'message': {'token': 'This field cannot be blank'}}

    def test_invalid_token_get(self):
        response = app.test_client().get('/events', headers={'token': 'token'})
        assert json.loads(response.data.decode('utf-8')) == {'message': 'Invalid Firebase ID Token'}

    def test_empty_result_get(self):
        conftest.pytest_unconfigure()
        response = app.test_client().get('/events', headers={'token': self.token})
        assert json.loads(response.data.decode('utf-8')) == []

    def test_get_event(self):
        conftest.pytest_unconfigure()
        member = model.User.get_or_create(self.event_info['members'][0]).email
        app.test_client().post('/events', headers={'token': self.token},
                               json={'name': self.event_info['event_name'],
                                     'gift_date': '2022-02-25',
                                     'location': self.event_info['place'],
                                     'members': [member]})
        response = app.test_client().get('/events', headers={'token': self.token})
        assert json.loads(response.data.decode('utf-8'))[0]['name'] == self.event_info['event_name']
        assert json.loads(response.data.decode('utf-8'))[0]['location'] == self.event_info['place']
        assert json.loads(response.data.decode('utf-8'))[0]['creator'] == self.data['email']

    def test_check_user(self):
        conftest.pytest_unconfigure()
        res = resources.check_user("email")
        assert res == False

        model.User.get_or_create("member@email.com")
        res = resources.check_user("member@email.com")
        assert res == True

    def test_email(self):
        try:
            resources.email("")
        except ValidationError as e:
            assert str(e) == "Empty email present in list"

        try:
            resources.email("email")
        except ValidationError as e:
            assert str(e) == "Invalid email: email"

        assert "my@email.com" == resources.email("my@email.com")
