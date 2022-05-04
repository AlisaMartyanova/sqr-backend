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
        'state': True,
        'wishlist': "This is my wishlist",
        'wrong_event_id': 0
    }

    def test_patch(self):
        response = app.test_client().patch('/assignee')
        assert json.loads(response.data.decode('utf-8')) == {'message': {'token': 'This field cannot be blank'}}

        response = app.test_client().patch('/assignee', headers={'token': 'token'})
        assert json.loads(response.data.decode('utf-8')) == {'message': 'Invalid Firebase ID Token'}

        response = app.test_client().patch('/assignee', headers={'token': self.token})
        assert json.loads(response.data.decode('utf-8')) == {'message': {'event_id': 'This field cannot be blank'}}

        response = app.test_client().patch('/assignee', headers={'token': self.token},
                                           json={'event_id': self.event_info['wrong_event_id']})
        assert json.loads(response.data.decode('utf-8')) == {'message': 'No events found'}

        response = app.test_client().post('/events', headers={'token': self.token},
                                          json={'name': self.event_info['event_name'],
                                                'gift_date': '2022-02-25',
                                                'location': self.event_info['place'], 'members': self.data['email']})
        id = json.loads(response.data.decode('utf-8'))['id']
        response = app.test_client().patch('/assignee', headers={'token': self.token}, json={'event_id': id})
        assert json.loads(response.data.decode('utf-8')) == {'message': 'Not enough participants'}

        conftest.pytest_unconfigure()
