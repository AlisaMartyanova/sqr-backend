import requests
import json
from datetime import datetime
from os import environ
from app import app
from test import conftest


class Test:
    data = {
        "email": environ.get('TEST_USER_EMAIL'),
        "password": environ.get('TEST_USER_PASSWORD'),
        "returnSecureToken": True
    }
    resp = requests.post(environ.get('TEST_URL'), data=data)
    token = str(resp.json()['idToken'])

    emails = ['1234@sdf.com', 'sdfghj@sdf.com', 'sdfhnjjhghj@kjh.com']
    users = []
    event_info = {
        'event_name': 'Event1',
        'date': datetime.strptime('2022-02-25', '%Y-%m-%d'),
        'place': 'University',
        'state': True
    }

    def test_post_event(self):
        response = app.test_client().post('/events')
        assert json.loads(response.data.decode('utf-8')) == {'message': {'token': 'This field cannot be blank'}}

        response = app.test_client().post('/events', headers={'token': 'token'})
        assert json.loads(response.data.decode('utf-8')) == {'message': 'Invalid Firebase ID Token'}

        response = app.test_client().post('/events', headers={'token': self.token},
                                          json={'name': self.event_info['event_name'], 'gift_date': '2022-02-25'})
        assert json.loads(response.data.decode('utf-8')) == \
               {'message': {'location': 'This field cannot be blank', 'members': 'This field cannot be blank'}}

        response = app.test_client().post('/events', headers={'token': self.token},
                                          json={'name': self.event_info['event_name'],
                                                'gift_date': '2022-02-25',
                                                'location': self.event_info['place'], 'members': self.emails[0]})
        assert json.loads(response.data.decode('utf-8')) == {'message': "Cannot find users with emails: " + self.emails[0]}

        response = app.test_client().post('/events', headers={'token': self.token},
                                          json={'name': self.event_info['event_name'],
                                                'gift_date': '2022-02-25',
                                                'location': self.event_info['place'], 'members': self.data['email']})
        assert json.loads(response.data.decode('utf-8'))['name'] == self.event_info['event_name']

        conftest.pytest_unconfigure()

    def test_get_event(self):
        response = app.test_client().get('/events')
        assert json.loads(response.data.decode('utf-8')) == {'message': {'token': 'This field cannot be blank'}}

        response = app.test_client().get('/events', headers={'token': 'token'})
        assert json.loads(response.data.decode('utf-8')) == {'message': 'Invalid Firebase ID Token'}

        response = app.test_client().get('/events', headers={'token': self.token})
        assert json.loads(response.data.decode('utf-8')) == []

        app.test_client().post('/events', headers={'token': self.token},
                               json={'name': self.event_info['event_name'],
                                     'gift_date': '2022-02-25',
                                     'location': self.event_info['place'], 'members': self.data['email']})
        response = app.test_client().get('/events', headers={'token': self.token})
        assert json.loads(response.data.decode('utf-8'))[0]['name'] == self.event_info['event_name']
        assert json.loads(response.data.decode('utf-8'))[0]['location'] == self.event_info['place']
        assert json.loads(response.data.decode('utf-8'))[0]['creator'] == self.data['email']

        conftest.pytest_unconfigure()
